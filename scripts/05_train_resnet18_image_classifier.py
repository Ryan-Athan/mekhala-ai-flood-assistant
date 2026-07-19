from __future__ import annotations

"""
FloodMind Step 5 - ResNet18 Image Classifier Training
=====================================================

Purpose:
    Train a stronger 3-class image classifier for FloodMind Image Analysis using
    transfer learning with ResNet18 when pretrained weights are available.

Classes:
    Flood
    Non_Flood
    Unrelated

Input dataset folder:
    data/processed/image_dataset_balanced_224/
        Flood/
        Non_Flood/
        Unrelated/

Outputs saved for the existing Streamlit app:
    models/flood_image_classifier_cnn.pth
    models/flood_image_classifier_cnn_torchscript.pt
    models/flood_image_classifier_metadata.json

Extra reports:
    reports/05_RESNET18_TRAINING_METRICS.json
    reports/05_RESNET18_CLASSIFICATION_REPORT.txt
    reports/05_RESNET18_CONFUSION_MATRIX.csv
    reports/05_RESNET18_PREDICTIONS.csv
    reports/05_RESNET18_TRAINING_CURVE_ACCURACY.png
    reports/05_RESNET18_TRAINING_CURVE_LOSS.png

Run from project root:
    python scripts/05_train_resnet18_image_classifier.py
"""

import json
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from PIL import Image, ImageFile, UnidentifiedImageError
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
from tqdm import tqdm

ImageFile.LOAD_TRUNCATED_IMAGES = True

# ============================================================
# Configuration
# ============================================================

RANDOM_SEED = 42
IMAGE_SIZE = 224
BATCH_SIZE = 16
NUM_WORKERS = 0  # Windows-safe. Increase to 2 only if your PC handles it.

# Stage 1 trains only the final classifier head. Fast and stable on CPU.
HEAD_EPOCHS = 8

# Stage 2 fine-tunes layer4 + classifier. Improves accuracy, slower.
FINE_TUNE_EPOCHS = 8

LEARNING_RATE_HEAD = 1e-3
LEARNING_RATE_FINE = 1e-4
WEIGHT_DECAY = 1e-4
PATIENCE = 5

CLASS_NAMES = ["Flood", "Non_Flood", "Unrelated"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


@dataclass
class SplitData:
    train_paths: List[Path]
    train_labels: List[int]
    val_paths: List[Path]
    val_labels: List[int]
    test_paths: List[Path]
    test_labels: List[int]


# ============================================================
# Paths and utilities
# ============================================================


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def ensure_dirs(project_root: Path) -> Dict[str, Path]:
    paths = {
        "data_dir": project_root / "data" / "processed" / "image_dataset_balanced_224",
        "models_dir": project_root / "models",
        "reports_dir": project_root / "reports",
        "splits_dir": project_root / "data" / "splits",
    }
    for key in ["models_dir", "reports_dir", "splits_dir"]:
        paths[key].mkdir(parents=True, exist_ok=True)
    return paths


def list_image_paths(data_dir: Path) -> Tuple[List[Path], List[int]]:
    image_paths: List[Path] = []
    labels: List[int] = []

    if not data_dir.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {data_dir}\n"
            "Run first: python scripts/01_clean_check_image_dataset.py"
        )

    for class_index, class_name in enumerate(CLASS_NAMES):
        class_dir = data_dir / class_name
        if not class_dir.exists():
            raise FileNotFoundError(
                f"Missing class folder: {class_dir}\n"
                f"Expected class folders: {CLASS_NAMES}"
            )

        class_images = sorted(
            p for p in class_dir.rglob("*")
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
        )
        if len(class_images) == 0:
            raise RuntimeError(f"No images found in class folder: {class_dir}")

        image_paths.extend(class_images)
        labels.extend([class_index] * len(class_images))

    return image_paths, labels


def make_splits(paths: Sequence[Path], labels: Sequence[int]) -> SplitData:
    # 70% train, 15% validation, 15% test, stratified by class.
    path_strings = [str(p) for p in paths]
    labels_array = np.array(labels)

    train_paths, temp_paths, train_labels, temp_labels = train_test_split(
        path_strings,
        labels_array,
        test_size=0.30,
        random_state=RANDOM_SEED,
        stratify=labels_array,
    )

    val_paths, test_paths, val_labels, test_labels = train_test_split(
        temp_paths,
        temp_labels,
        test_size=0.50,
        random_state=RANDOM_SEED,
        stratify=temp_labels,
    )

    return SplitData(
        train_paths=[Path(p) for p in train_paths],
        train_labels=[int(x) for x in train_labels],
        val_paths=[Path(p) for p in val_paths],
        val_labels=[int(x) for x in val_labels],
        test_paths=[Path(p) for p in test_paths],
        test_labels=[int(x) for x in test_labels],
    )


def save_split_csv(split: SplitData, splits_dir: Path) -> None:
    rows = []
    for split_name, paths, labels in [
        ("train", split.train_paths, split.train_labels),
        ("validation", split.val_paths, split.val_labels),
        ("test", split.test_paths, split.test_labels),
    ]:
        for path, label in zip(paths, labels):
            rows.append(
                {
                    "split": split_name,
                    "path": str(path),
                    "class_index": label,
                    "class_name": CLASS_NAMES[label],
                    "filename": path.name,
                }
            )

    df = pd.DataFrame(rows)
    df[df["split"] == "train"].to_csv(splits_dir / "image_train_split.csv", index=False)
    df[df["split"] == "validation"].to_csv(splits_dir / "image_validation_split.csv", index=False)
    df[df["split"] == "test"].to_csv(splits_dir / "image_test_split.csv", index=False)


# ============================================================
# Dataset
# ============================================================


class FloodImageDataset(Dataset):
    def __init__(self, image_paths: Sequence[Path], labels: Sequence[int], transform=None):
        self.image_paths = list(image_paths)
        self.labels = list(labels)
        self.transform = transform

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, index: int):
        image_path = self.image_paths[index]
        label = self.labels[index]

        try:
            image = Image.open(image_path).convert("RGB")
        except (UnidentifiedImageError, OSError) as exc:
            raise RuntimeError(f"Cannot open image: {image_path}") from exc

        if self.transform is not None:
            image = self.transform(image)

        return image, torch.tensor(label, dtype=torch.long), str(image_path)


# ============================================================
# Transforms and model
# ============================================================


def build_transforms():
    train_transform = transforms.Compose(
        [
            transforms.RandomResizedCrop(IMAGE_SIZE, scale=(0.72, 1.0), ratio=(0.85, 1.18)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=10),
            transforms.ColorJitter(brightness=0.18, contrast=0.18, saturation=0.14, hue=0.03),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )

    eval_transform = transforms.Compose(
        [
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
        ]
    )

    return train_transform, eval_transform


def build_resnet18(num_classes: int) -> Tuple[nn.Module, str]:
    """Build ResNet18. Use pretrained weights when available; fallback gracefully."""
    weights_status = "none"

    try:
        # New torchvision API. This may download weights the first time.
        weights = models.ResNet18_Weights.DEFAULT
        model = models.resnet18(weights=weights)
        weights_status = "imagenet_pretrained"
    except Exception as exc:
        print()
        print("WARNING: Could not load/download pretrained ResNet18 weights.")
        print(f"Reason: {exc}")
        print("Training ResNet18 without pretrained weights instead.")
        print("Accuracy may be lower. Internet helps for pretrained weights.")
        print()
        model = models.resnet18(weights=None)
        weights_status = "random_init"

    in_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(p=0.25),
        nn.Linear(in_features, num_classes),
    )
    return model, weights_status


def freeze_backbone(model: nn.Module) -> None:
    for name, param in model.named_parameters():
        param.requires_grad = False
    for param in model.fc.parameters():
        param.requires_grad = True


def unfreeze_layer4_and_head(model: nn.Module) -> None:
    for name, param in model.named_parameters():
        param.requires_grad = False
    for param in model.layer4.parameters():
        param.requires_grad = True
    for param in model.fc.parameters():
        param.requires_grad = True


def count_trainable_params(model: nn.Module) -> int:
    return int(sum(p.numel() for p in model.parameters() if p.requires_grad))


# ============================================================
# Training and evaluation
# ============================================================


def run_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer | None,
    device: torch.device,
    train: bool,
) -> Dict[str, float]:
    if train:
        model.train()
    else:
        model.eval()

    all_true: List[int] = []
    all_pred: List[int] = []
    losses: List[float] = []

    progress = tqdm(loader, leave=False, ncols=90)
    for images, labels, _paths in progress:
        images = images.to(device)
        labels = labels.to(device)

        if train:
            optimizer.zero_grad(set_to_none=True)  # type: ignore[union-attr]
            logits = model(images)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()  # type: ignore[union-attr]
        else:
            with torch.no_grad():
                logits = model(images)
                loss = criterion(logits, labels)

        preds = torch.argmax(logits, dim=1)
        losses.append(float(loss.item()))
        all_true.extend(labels.detach().cpu().numpy().astype(int).tolist())
        all_pred.extend(preds.detach().cpu().numpy().astype(int).tolist())

    acc = accuracy_score(all_true, all_pred)
    macro_f1 = f1_score(all_true, all_pred, average="macro", zero_division=0)

    return {
        "loss": float(np.mean(losses)) if losses else math.nan,
        "accuracy": float(acc),
        "macro_f1": float(macro_f1),
    }


def predict_loader(model: nn.Module, loader: DataLoader, device: torch.device) -> pd.DataFrame:
    model.eval()
    rows = []

    with torch.no_grad():
        for images, labels, paths in tqdm(loader, ncols=90, desc="Testing"):
            images = images.to(device)
            logits = model(images)
            probs = torch.softmax(logits, dim=1)
            confs, preds = torch.max(probs, dim=1)

            for path, true_label, pred_label, confidence, prob_row in zip(
                paths,
                labels.cpu().numpy().astype(int).tolist(),
                preds.cpu().numpy().astype(int).tolist(),
                confs.cpu().numpy().tolist(),
                probs.cpu().numpy().tolist(),
            ):
                rows.append(
                    {
                        "path": path,
                        "filename": Path(path).name,
                        "true_index": true_label,
                        "true_class": CLASS_NAMES[true_label],
                        "pred_index": pred_label,
                        "predicted_class": CLASS_NAMES[pred_label],
                        "confidence": float(confidence),
                        "correct": bool(true_label == pred_label),
                        "prob_Flood": float(prob_row[0]),
                        "prob_Non_Flood": float(prob_row[1]),
                        "prob_Unrelated": float(prob_row[2]),
                    }
                )

    return pd.DataFrame(rows)


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    device: torch.device,
) -> Tuple[nn.Module, List[Dict[str, float]], int, float]:
    criterion = nn.CrossEntropyLoss()
    history: List[Dict[str, float]] = []

    best_state = None
    best_val_f1 = -1.0
    best_epoch = 0
    epochs_without_improvement = 0
    global_epoch = 0

    stages = [
        {
            "name": "head",
            "epochs": HEAD_EPOCHS,
            "lr": LEARNING_RATE_HEAD,
            "freeze_fn": freeze_backbone,
        },
        {
            "name": "fine_tune_layer4",
            "epochs": FINE_TUNE_EPOCHS,
            "lr": LEARNING_RATE_FINE,
            "freeze_fn": unfreeze_layer4_and_head,
        },
    ]

    for stage in stages:
        stage["freeze_fn"](model)
        trainable = count_trainable_params(model)
        optimizer = torch.optim.AdamW(
            [p for p in model.parameters() if p.requires_grad],
            lr=stage["lr"],
            weight_decay=WEIGHT_DECAY,
        )

        print()
        print(f"Stage: {stage['name']} | epochs={stage['epochs']} | trainable params={trainable:,}")

        for _ in range(stage["epochs"]):
            global_epoch += 1
            train_metrics = run_epoch(model, train_loader, criterion, optimizer, device, train=True)
            val_metrics = run_epoch(model, val_loader, criterion, None, device, train=False)

            row = {
                "epoch": global_epoch,
                "stage": stage["name"],
                "train_loss": train_metrics["loss"],
                "train_accuracy": train_metrics["accuracy"],
                "train_macro_f1": train_metrics["macro_f1"],
                "val_loss": val_metrics["loss"],
                "val_accuracy": val_metrics["accuracy"],
                "val_macro_f1": val_metrics["macro_f1"],
            }
            history.append(row)

            print(
                f"Epoch {global_epoch:02d} | "
                f"stage={stage['name']} | "
                f"train_acc={train_metrics['accuracy']:.4f} | "
                f"val_acc={val_metrics['accuracy']:.4f} | "
                f"val_f1={val_metrics['macro_f1']:.4f}"
            )

            if val_metrics["macro_f1"] > best_val_f1:
                best_val_f1 = val_metrics["macro_f1"]
                best_epoch = global_epoch
                best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
                epochs_without_improvement = 0
            else:
                epochs_without_improvement += 1

            if epochs_without_improvement >= PATIENCE:
                print("Early stopping triggered.")
                break

        if epochs_without_improvement >= PATIENCE:
            break

    if best_state is not None:
        model.load_state_dict(best_state)

    return model, history, best_epoch, best_val_f1


# ============================================================
# Saving outputs
# ============================================================


def save_plots(history: List[Dict[str, float]], reports_dir: Path) -> None:
    if not history:
        return

    df = pd.DataFrame(history)

    plt.figure(figsize=(8, 5))
    plt.plot(df["epoch"], df["train_accuracy"], marker="o", label="Train accuracy")
    plt.plot(df["epoch"], df["val_accuracy"], marker="o", label="Validation accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("ResNet18 Training Accuracy")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(reports_dir / "05_RESNET18_TRAINING_CURVE_ACCURACY.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(df["epoch"], df["train_loss"], marker="o", label="Train loss")
    plt.plot(df["epoch"], df["val_loss"], marker="o", label="Validation loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("ResNet18 Training Loss")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(reports_dir / "05_RESNET18_TRAINING_CURVE_LOSS.png", dpi=160)
    plt.close()


def save_model_outputs(
    model: nn.Module,
    metadata: Dict,
    models_dir: Path,
    device: torch.device,
) -> None:
    pth_path = models_dir / "flood_image_classifier_cnn.pth"
    torchscript_path = models_dir / "flood_image_classifier_cnn_torchscript.pt"
    metadata_path = models_dir / "flood_image_classifier_metadata.json"
    mapping_path = models_dir / "image_class_mapping.json"

    model_cpu = model.to("cpu")
    model_cpu.eval()

    torch.save(
        {
            "architecture": "resnet18",
            "model_state_dict": model_cpu.state_dict(),
            "class_names": CLASS_NAMES,
            "class_to_idx": {name: idx for idx, name in enumerate(CLASS_NAMES)},
            "image_size": IMAGE_SIZE,
            "metadata": metadata,
        },
        pth_path,
    )

    example_input = torch.randn(1, 3, IMAGE_SIZE, IMAGE_SIZE)
    with torch.no_grad():
        traced = torch.jit.trace(model_cpu, example_input)
        traced.save(str(torchscript_path))

    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    class_mapping = {
        "class_names": CLASS_NAMES,
        "class_to_idx": {name: idx for idx, name in enumerate(CLASS_NAMES)},
        "idx_to_class": {str(idx): name for idx, name in enumerate(CLASS_NAMES)},
    }
    with mapping_path.open("w", encoding="utf-8") as f:
        json.dump(class_mapping, f, indent=2, ensure_ascii=False)

    # Move back to the original device if needed after saving.
    model.to(device)

    print(f"Saved model: {pth_path}")
    print(f"Saved TorchScript model: {torchscript_path}")
    print(f"Saved metadata: {metadata_path}")
    print(f"Saved class mapping: {mapping_path}")


def save_reports(
    history: List[Dict[str, float]],
    predictions_df: pd.DataFrame,
    split: SplitData,
    reports_dir: Path,
    metadata: Dict,
) -> None:
    y_true = predictions_df["true_index"].astype(int).tolist()
    y_pred = predictions_df["pred_index"].astype(int).tolist()

    report_text = classification_report(
        y_true,
        y_pred,
        target_names=CLASS_NAMES,
        digits=4,
        zero_division=0,
    )
    (reports_dir / "05_RESNET18_CLASSIFICATION_REPORT.txt").write_text(report_text, encoding="utf-8")

    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(CLASS_NAMES))))
    cm_df = pd.DataFrame(cm, index=CLASS_NAMES, columns=CLASS_NAMES)
    cm_df.to_csv(reports_dir / "05_RESNET18_CONFUSION_MATRIX.csv")

    predictions_df.to_csv(reports_dir / "05_RESNET18_PREDICTIONS.csv", index=False)
    pd.DataFrame(history).to_csv(reports_dir / "05_RESNET18_TRAINING_HISTORY.csv", index=False)

    metrics = {
        **metadata,
        "classification_report": report_text,
        "confusion_matrix": cm_df.to_dict(),
        "split_sizes": {
            "train": len(split.train_paths),
            "validation": len(split.val_paths),
            "test": len(split.test_paths),
        },
        "class_summary_test": predictions_df.groupby("true_class")["correct"].agg(
            total="count", correct="sum", accuracy="mean"
        ).reset_index().to_dict(orient="records"),
    }

    with (reports_dir / "05_RESNET18_TRAINING_METRICS.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    save_plots(history, reports_dir)


# ============================================================
# Main
# ============================================================


def main() -> None:
    start_time = time.time()
    set_seed(RANDOM_SEED)

    project_root = get_project_root()
    paths = ensure_dirs(project_root)
    data_dir = paths["data_dir"]
    models_dir = paths["models_dir"]
    reports_dir = paths["reports_dir"]
    splits_dir = paths["splits_dir"]

    print()
    print("FloodMind Step 5 - ResNet18 Image Classifier Training")
    print("=" * 62)
    print(f"Project root: {project_root}")
    print(f"Training data: {data_dir}")

    image_paths, labels = list_image_paths(data_dir)

    class_counts = {name: labels.count(idx) for idx, name in enumerate(CLASS_NAMES)}
    print()
    print("Class counts:")
    for name in CLASS_NAMES:
        print(f"- {name}: {class_counts[name]}")

    split = make_splits(image_paths, labels)
    save_split_csv(split, splits_dir)

    print()
    print("Split sizes:")
    print(f"- Train:      {len(split.train_paths)}")
    print(f"- Validation: {len(split.val_paths)}")
    print(f"- Test:       {len(split.test_paths)}")

    train_transform, eval_transform = build_transforms()
    train_ds = FloodImageDataset(split.train_paths, split.train_labels, transform=train_transform)
    val_ds = FloodImageDataset(split.val_paths, split.val_labels, transform=eval_transform)
    test_ds = FloodImageDataset(split.test_paths, split.test_labels, transform=eval_transform)

    train_loader = DataLoader(
        train_ds,
        batch_size=BATCH_SIZE,
        shuffle=True,
        num_workers=NUM_WORKERS,
        pin_memory=torch.cuda.is_available(),
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=torch.cuda.is_available(),
    )
    test_loader = DataLoader(
        test_ds,
        batch_size=BATCH_SIZE,
        shuffle=False,
        num_workers=NUM_WORKERS,
        pin_memory=torch.cuda.is_available(),
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print()
    print(f"Device: {device}")

    model, weights_status = build_resnet18(num_classes=len(CLASS_NAMES))
    model = model.to(device)
    print(f"Architecture: ResNet18")
    print(f"Weights: {weights_status}")

    print()
    print("Training started...")
    model, history, best_epoch, best_val_f1 = train_model(model, train_loader, val_loader, device)

    print()
    print("Evaluating best model on test set...")
    predictions_df = predict_loader(model, test_loader, device)
    test_accuracy = accuracy_score(predictions_df["true_index"], predictions_df["pred_index"])
    test_macro_f1 = f1_score(
        predictions_df["true_index"],
        predictions_df["pred_index"],
        average="macro",
        zero_division=0,
    )

    elapsed_seconds = time.time() - start_time

    metadata = {
        "model_name": "FloodMind ResNet18 Image Classifier",
        "architecture": "resnet18",
        "framework": "pytorch",
        "weights_status": weights_status,
        "task": "3-class flood image classification",
        "class_names": CLASS_NAMES,
        "classes": CLASS_NAMES,
        "class_to_idx": {name: idx for idx, name in enumerate(CLASS_NAMES)},
        "idx_to_class": {str(idx): name for idx, name in enumerate(CLASS_NAMES)},
        "image_size": IMAGE_SIZE,
        "input_size": [IMAGE_SIZE, IMAGE_SIZE],
        "input_channels": 3,
        "normalization": {
            "mean": IMAGENET_MEAN,
            "std": IMAGENET_STD,
        },
        "random_seed": RANDOM_SEED,
        "batch_size": BATCH_SIZE,
        "head_epochs": HEAD_EPOCHS,
        "fine_tune_epochs": FINE_TUNE_EPOCHS,
        "best_epoch": best_epoch,
        "best_validation_macro_f1": float(best_val_f1),
        "test_accuracy": float(test_accuracy),
        "test_macro_f1": float(test_macro_f1),
        "class_counts_full_dataset": class_counts,
        "train_size": len(split.train_paths),
        "validation_size": len(split.val_paths),
        "test_size": len(split.test_paths),
        "trained_seconds": round(elapsed_seconds, 2),
        "saved_for_streamlit_app": True,
        "torch_version": torch.__version__,
        "torchvision_model": "torchvision.models.resnet18",
    }

    save_reports(history, predictions_df, split, reports_dir, metadata)
    save_model_outputs(model, metadata, models_dir, device)

    print()
    print("Training complete.")
    print("=" * 62)
    print(f"Best epoch: {best_epoch}")
    print(f"Best validation macro F1: {best_val_f1:.4f}")
    print(f"Test accuracy: {test_accuracy:.4f}")
    print(f"Test macro F1: {test_macro_f1:.4f}")
    print(f"Saved reports folder: {reports_dir}")
    print()
    print("Next command:")
    print("python scripts/04_test_image_result_calibration.py")


if __name__ == "__main__":
    main()
