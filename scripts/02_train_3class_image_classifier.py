from __future__ import annotations

import json
import random
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image, UnidentifiedImageError
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset


# ============================================================
# FloodMind - Step 2: Train 3-Class Image Classifier
# Classes: Flood, Non_Flood, Unrelated
#
# IMPORTANT:
# This version uses project-relative paths.
# It does NOT use /mnt/data or any Linux/cloud path.
# Run from your project root, for example:
#   python scripts/02_train_3class_image_classifier.py
# ============================================================

SEED = 42
IMAGE_SIZE = 48
BATCH_SIZE = 64
MAX_EPOCHS = 15
EARLY_STOP_PATIENCE = 5
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4

EXPECTED_CLASSES = ["Flood", "Non_Flood", "Unrelated"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "image_dataset_balanced_224"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
SPLITS_DIR = PROJECT_ROOT / "data" / "splits"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

MODEL_PATH = MODELS_DIR / "flood_image_classifier_cnn.pth"
TORCHSCRIPT_PATH = MODELS_DIR / "flood_image_classifier_cnn_torchscript.pt"
METADATA_PATH = MODELS_DIR / "flood_image_classifier_metadata.json"
CLASS_MAPPING_MODEL_PATH = MODELS_DIR / "image_class_mapping.json"
CLASS_MAPPING_DATA_PATH = PROCESSED_DIR / "image_class_mapping.json"


# Avoid possible CPU backend issues on some Windows installs.
try:
    torch.backends.mkldnn.enabled = False
except Exception:
    pass

try:
    torch.set_num_threads(1)
except Exception:
    pass

try:
    torch.set_num_interop_threads(1)
except Exception:
    pass


def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class FastCNN(nn.Module):
    def __init__(self, n_classes: int = 3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 12, kernel_size=3, padding=1),
            nn.BatchNorm2d(12),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(12, 24, kernel_size=3, padding=1),
            nn.BatchNorm2d(24),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(24, 48, kernel_size=3, padding=1),
            nn.BatchNorm2d(48),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),

            nn.Flatten(),
            nn.Dropout(0.2),
            nn.Linear(48, n_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


def ensure_dirs() -> None:
    for folder in [MODELS_DIR, REPORTS_DIR, SPLITS_DIR, PROCESSED_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def validate_dataset_folder() -> None:
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            "Training dataset folder was not found.\n"
            f"Expected folder:\n{DATA_DIR}\n\n"
            "Run Step 1 first:\n"
            "python scripts/01_clean_check_image_dataset.py"
        )

    missing = [class_name for class_name in EXPECTED_CLASSES if not (DATA_DIR / class_name).exists()]
    if missing:
        raise FileNotFoundError(
            "One or more class folders are missing.\n"
            f"Expected class folders: {EXPECTED_CLASSES}\n"
            f"Missing: {missing}\n"
            f"Inside: {DATA_DIR}"
        )


def collect_manifest() -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for class_name in EXPECTED_CLASSES:
        class_dir = DATA_DIR / class_name
        image_files = sorted(
            p for p in class_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        )

        for image_path in image_files:
            rows.append(
                {
                    "path": str(image_path),
                    "filename": image_path.name,
                    "class_name": class_name,
                }
            )

    manifest = pd.DataFrame(rows)
    if manifest.empty:
        raise RuntimeError(
            "No training images found.\n"
            f"Checked folder: {DATA_DIR}\n"
            "Expected folders: Flood, Non_Flood, Unrelated"
        )

    class_counts = manifest["class_name"].value_counts().to_dict()
    missing_zero = [c for c in EXPECTED_CLASSES if int(class_counts.get(c, 0)) == 0]
    if missing_zero:
        raise RuntimeError(
            "One or more required classes has 0 images.\n"
            f"Class counts: {class_counts}\n"
            f"Missing/empty classes: {missing_zero}\n"
            "Run Step 1 again and check data/processed/image_dataset_balanced_224."
        )

    class_to_idx = {class_name: idx for idx, class_name in enumerate(EXPECTED_CLASSES)}
    manifest["class_index"] = manifest["class_name"].map(class_to_idx).astype(int)
    return manifest


def safe_load_image(path: str | Path, image_size: int = IMAGE_SIZE) -> np.ndarray:
    try:
        image = Image.open(path).convert("RGB").resize((image_size, image_size))
    except (UnidentifiedImageError, OSError) as exc:
        raise RuntimeError(f"Could not read image: {path}\nReason: {exc}") from exc

    arr = np.asarray(image).astype("float32") / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype="float32")
    std = np.array([0.229, 0.224, 0.225], dtype="float32")
    arr = (arr - mean) / std
    arr = np.transpose(arr, (2, 0, 1))
    return arr


def load_dataframe_as_tensors(df: pd.DataFrame) -> tuple[torch.Tensor, torch.Tensor]:
    images: list[np.ndarray] = []
    labels: list[int] = []

    for _, row in df.iterrows():
        images.append(safe_load_image(row["path"], IMAGE_SIZE))
        labels.append(int(row["class_index"]))

    x = torch.tensor(np.stack(images), dtype=torch.float32)
    y = torch.tensor(labels, dtype=torch.long)
    return x, y


def evaluate_model(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: str,
) -> tuple[float, float, float, list[int], list[int]]:
    model.eval()
    losses: list[float] = []
    predictions: list[int] = []
    true_labels: list[int] = []

    with torch.no_grad():
        for xb, yb in loader:
            xb = xb.to(device)
            yb = yb.to(device)
            logits = model(xb)
            loss = criterion(logits, yb)

            losses.append(float(loss.item()) * len(yb))
            predictions.extend(logits.argmax(dim=1).cpu().tolist())
            true_labels.extend(yb.cpu().tolist())

    avg_loss = sum(losses) / max(1, len(true_labels))
    accuracy = accuracy_score(true_labels, predictions)
    macro_f1 = f1_score(true_labels, predictions, average="macro", zero_division=0)
    return avg_loss, accuracy, macro_f1, true_labels, predictions


def save_plots(history_df: pd.DataFrame, cm: np.ndarray, classes: list[str]) -> None:
    plt.figure(figsize=(6, 5))
    plt.imshow(cm)
    plt.title("Confusion Matrix - Image Classifier")
    plt.xticks(range(len(classes)), classes, rotation=35, ha="right")
    plt.yticks(range(len(classes)), classes)
    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    for i in range(len(classes)):
        for j in range(len(classes)):
            plt.text(j, i, str(cm[i, j]), ha="center", va="center")

    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "02_CONFUSION_MATRIX.png", dpi=160)
    plt.close()

    plt.figure(figsize=(7, 4))
    plt.plot(history_df["epoch"], history_df["train_accuracy"], label="train")
    plt.plot(history_df["epoch"], history_df["val_accuracy"], label="validation")
    plt.legend()
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "02_TRAINING_CURVE_ACCURACY.png", dpi=160)
    plt.close()

    plt.figure(figsize=(7, 4))
    plt.plot(history_df["epoch"], history_df["train_loss"], label="train")
    plt.plot(history_df["epoch"], history_df["val_loss"], label="validation")
    plt.legend()
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.tight_layout()
    plt.savefig(REPORTS_DIR / "02_TRAINING_CURVE_LOSS.png", dpi=160)
    plt.close()


def main() -> None:
    set_seed(SEED)
    ensure_dirs()
    validate_dataset_folder()

    print("\nFloodMind Image Classifier Training")
    print("=" * 48)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Training data: {DATA_DIR}")

    manifest = collect_manifest()
    print("\nClass counts:")
    for class_name in EXPECTED_CLASSES:
        count = int((manifest["class_name"] == class_name).sum())
        print(f"- {class_name}: {count}")

    class_to_idx = {class_name: idx for idx, class_name in enumerate(EXPECTED_CLASSES)}
    idx_to_class = {idx: class_name for class_name, idx in class_to_idx.items()}

    train_df, temp_df = train_test_split(
        manifest,
        test_size=0.30,
        stratify=manifest["class_index"],
        random_state=SEED,
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        stratify=temp_df["class_index"],
        random_state=SEED,
    )

    train_df.to_csv(SPLITS_DIR / "image_train_split.csv", index=False)
    val_df.to_csv(SPLITS_DIR / "image_validation_split.csv", index=False)
    test_df.to_csv(SPLITS_DIR / "image_test_split.csv", index=False)

    split_summary_rows: list[dict[str, object]] = []
    for split_name, split_df in [
        ("train", train_df),
        ("validation", val_df),
        ("test", test_df),
    ]:
        for class_name in EXPECTED_CLASSES:
            split_summary_rows.append(
                {
                    "split": split_name,
                    "class_name": class_name,
                    "count": int((split_df["class_name"] == class_name).sum()),
                }
            )

    pd.DataFrame(split_summary_rows).to_csv(
        PROCESSED_DIR / "image_training_split_summary.csv",
        index=False,
    )

    print("\nLoading images into memory...")
    x_train, y_train = load_dataframe_as_tensors(train_df)
    x_val, y_val = load_dataframe_as_tensors(val_df)
    x_test, y_test = load_dataframe_as_tensors(test_df)

    train_loader = DataLoader(
        TensorDataset(x_train, y_train),
        batch_size=BATCH_SIZE,
        shuffle=True,
    )
    val_loader = DataLoader(
        TensorDataset(x_val, y_val),
        batch_size=128,
        shuffle=False,
    )
    test_loader = DataLoader(
        TensorDataset(x_test, y_test),
        batch_size=128,
        shuffle=False,
    )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    model = FastCNN(len(EXPECTED_CLASSES)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY,
    )

    history: list[dict[str, float | int]] = []
    best_val_f1 = -1.0
    best_state: dict[str, torch.Tensor] | None = None
    best_epoch = 0
    start_time = time.time()

    print("\nTraining started...")
    for epoch in range(1, MAX_EPOCHS + 1):
        model.train()
        train_losses: list[float] = []
        train_predictions: list[int] = []
        train_true: list[int] = []

        for xb, yb in train_loader:
            xb = xb.to(device)
            yb = yb.to(device)

            optimizer.zero_grad()
            logits = model(xb)
            loss = criterion(logits, yb)
            loss.backward()
            optimizer.step()

            train_losses.append(float(loss.item()) * len(yb))
            train_predictions.extend(logits.argmax(dim=1).detach().cpu().tolist())
            train_true.extend(yb.cpu().tolist())

        val_loss, val_acc, val_f1, _, _ = evaluate_model(model, val_loader, criterion, device)
        train_loss = sum(train_losses) / max(1, len(train_true))
        train_acc = accuracy_score(train_true, train_predictions)
        train_f1 = f1_score(train_true, train_predictions, average="macro", zero_division=0)

        record = {
            "epoch": epoch,
            "train_loss": round(float(train_loss), 6),
            "train_accuracy": round(float(train_acc), 6),
            "train_macro_f1": round(float(train_f1), 6),
            "val_loss": round(float(val_loss), 6),
            "val_accuracy": round(float(val_acc), 6),
            "val_macro_f1": round(float(val_f1), 6),
        }
        history.append(record)

        print(
            f"Epoch {epoch:02d} | "
            f"train_acc={record['train_accuracy']:.4f} | "
            f"val_acc={record['val_accuracy']:.4f} | "
            f"val_f1={record['val_macro_f1']:.4f}"
        )

        if val_f1 > best_val_f1:
            best_val_f1 = float(val_f1)
            best_epoch = epoch
            best_state = {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}

        if epoch - best_epoch >= EARLY_STOP_PATIENCE and epoch >= 8:
            print("Early stopping triggered.")
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    test_loss, test_acc, test_f1, y_true, y_pred = evaluate_model(model, test_loader, criterion, device)

    report = classification_report(
        y_true,
        y_pred,
        target_names=EXPECTED_CLASSES,
        digits=4,
        zero_division=0,
    )
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(EXPECTED_CLASSES))))

    checkpoint = {
        "model_state_dict": model.cpu().state_dict(),
        "class_to_idx": class_to_idx,
        "idx_to_class": idx_to_class,
        "input_size": IMAGE_SIZE,
        "architecture": "FastCNN",
        "normalization": {
            "mean": [0.485, 0.456, 0.406],
            "std": [0.229, 0.224, 0.225],
        },
    }
    torch.save(checkpoint, MODEL_PATH)

    model.eval()
    dummy_input = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)
    scripted = torch.jit.trace(model, dummy_input)
    scripted.save(str(TORCHSCRIPT_PATH))

    training_seconds = round(time.time() - start_time, 2)
    metadata = {
        "model_name": "FloodMind 3-Class Image Classifier",
        "model_type": "Compact CNN image classifier",
        "framework": "PyTorch",
        "classes": EXPECTED_CLASSES,
        "class_to_idx": class_to_idx,
        "idx_to_class": idx_to_class,
        "input_size": IMAGE_SIZE,
        "train_rows": int(len(train_df)),
        "validation_rows": int(len(val_df)),
        "test_rows": int(len(test_df)),
        "best_epoch": int(best_epoch),
        "test_loss": float(test_loss),
        "test_accuracy": float(test_acc),
        "test_macro_f1": float(test_f1),
        "training_seconds": training_seconds,
        "data_dir": str(DATA_DIR),
        "notes": "Step 2 training on balanced cleaned dataset. More Flood images are recommended for stronger real-world performance.",
    }

    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    mapping_payload = {
        "class_to_idx": class_to_idx,
        "idx_to_class": idx_to_class,
    }
    CLASS_MAPPING_MODEL_PATH.write_text(json.dumps(mapping_payload, indent=2), encoding="utf-8")
    CLASS_MAPPING_DATA_PATH.write_text(json.dumps(mapping_payload, indent=2), encoding="utf-8")

    history_df = pd.DataFrame(history)
    history_df.to_csv(REPORTS_DIR / "02_TRAINING_HISTORY.csv", index=False)
    (REPORTS_DIR / "02_CLASSIFICATION_REPORT.txt").write_text(report, encoding="utf-8")
    pd.DataFrame(cm, index=EXPECTED_CLASSES, columns=EXPECTED_CLASSES).to_csv(
        REPORTS_DIR / "02_CONFUSION_MATRIX.csv"
    )
    (REPORTS_DIR / "02_TRAINING_METRICS.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    model.eval()
    softmax = nn.Softmax(dim=1)
    probabilities: list[list[float]] = []
    with torch.no_grad():
        for xb, _ in test_loader:
            probs = softmax(model(xb)).cpu().numpy().tolist()
            probabilities.extend(probs)

    prediction_rows: list[dict[str, object]] = []
    test_reset = test_df.reset_index(drop=True)
    for idx, row in test_reset.iterrows():
        true_idx = int(y_true[idx])
        pred_idx = int(y_pred[idx])
        prob = probabilities[idx]
        prediction_row: dict[str, object] = {
            "filename": row["filename"],
            "true_class": idx_to_class[true_idx],
            "predicted_class": idx_to_class[pred_idx],
            "confidence": float(max(prob)),
        }
        for class_index, class_name in idx_to_class.items():
            prediction_row[f"prob_{class_name}"] = float(prob[class_index])
        prediction_rows.append(prediction_row)

    pd.DataFrame(prediction_rows).to_csv(
        REPORTS_DIR / "02_SAMPLE_PREDICTIONS.csv",
        index=False,
    )

    save_plots(history_df, cm, EXPECTED_CLASSES)

    print("\nTraining complete.")
    print("=" * 48)
    print(f"Best epoch: {best_epoch}")
    print(f"Test accuracy: {test_acc:.4f}")
    print(f"Test macro F1: {test_f1:.4f}")
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved TorchScript model: {TORCHSCRIPT_PATH}")
    print(f"Saved metadata: {METADATA_PATH}")
    print(f"Saved reports folder: {REPORTS_DIR}")


if __name__ == "__main__":
    main()
