from __future__ import annotations

import json
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


# ============================================================
# FloodMind - Step 3 Image Model Service
# Connects trained Step 2 image model to Streamlit Image Analysis UI.
#
# Expected model files:
#   models/flood_image_classifier_cnn.pth
#   models/flood_image_classifier_metadata.json
#   models/image_class_mapping.json
#
# Main app function:
#   analyze_uploaded_image(uploaded_file=..., file_name=...)
# ============================================================

PROJECT_ROOT = Path(__file__).parents[1]
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "flood_image_classifier_cnn.pth"
TORCHSCRIPT_PATH = MODELS_DIR / "flood_image_classifier_cnn_torchscript.pt"
METADATA_PATH = MODELS_DIR / "flood_image_classifier_metadata.json"
CLASS_MAPPING_PATH = MODELS_DIR / "image_class_mapping.json"

DEFAULT_CLASSES = ["Flood", "Non_Flood", "Unrelated"]
DEFAULT_IMAGE_SIZE = 224
NORMALIZE_MEAN = np.array([0.485, 0.456, 0.406], dtype="float32")
NORMALIZE_STD = np.array([0.229, 0.224, 0.225], dtype="float32")


def _import_torch():
    try:
        import torch
        import torch.nn as nn
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "PyTorch is not installed in this virtual environment. "
            "Install it with: python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu"
        ) from exc

    # Safer on some Windows CPU environments.
    try:
        torch.backends.mkldnn.enabled = False
    except Exception:
        pass

    try:
        torch.set_num_threads(1)
    except Exception:
        pass

    return torch, nn


class FastCNN(_import_torch()[1].Module):
    """Same architecture used in scripts/02_train_3class_image_classifier.py."""

    def __init__(self, n_classes: int = 3):
        super().__init__()
        _, nn = _import_torch()
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

    def forward(self, x):
        return self.net(x)


def _read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _classes_from_payload(payload: dict[str, Any] | None) -> list[str]:
    if not payload:
        return DEFAULT_CLASSES

    classes = payload.get("classes")
    if isinstance(classes, list) and classes:
        return [str(item) for item in classes]

    idx_to_class = payload.get("idx_to_class")
    if isinstance(idx_to_class, dict) and idx_to_class:
        pairs = sorted((int(k), str(v)) for k, v in idx_to_class.items())
        return [value for _, value in pairs]

    class_to_idx = payload.get("class_to_idx")
    if isinstance(class_to_idx, dict) and class_to_idx:
        pairs = sorted((int(v), str(k)) for k, v in class_to_idx.items())
        return [value for _, value in pairs]

    return DEFAULT_CLASSES


def _coerce_image_size(value: Any, default: int = DEFAULT_IMAGE_SIZE) -> int:
    """Return a single integer image size from metadata.

    Supports old CNN metadata like 48 and new ResNet metadata like [224, 224].
    """
    if value is None:
        return int(default)

    if isinstance(value, (list, tuple)) and len(value) > 0:
        # input_size may be [224, 224] or [3, 224, 224]. Use the last spatial value.
        numeric_values = []
        for item in value:
            try:
                numeric_values.append(int(item))
            except Exception:
                continue
        if numeric_values:
            return int(numeric_values[-1])
        return int(default)

    if isinstance(value, dict):
        for key in ("height", "width", "size", "image_size"):
            if key in value:
                try:
                    return int(value[key])
                except Exception:
                    pass
        return int(default)

    try:
        return int(value)
    except Exception:
        return int(default)


def _load_metadata() -> dict[str, Any]:
    metadata = _read_json(METADATA_PATH, {})
    mapping = _read_json(CLASS_MAPPING_PATH, {})

    if "classes" not in metadata:
        metadata["classes"] = _classes_from_payload(mapping or metadata)

    return metadata


@lru_cache(maxsize=1)
def _load_model_cached():
    torch, _ = _import_torch()
    metadata = _load_metadata()
    classes = _classes_from_payload(metadata)
    image_size = _coerce_image_size(
        metadata.get("input_size", metadata.get("image_size", DEFAULT_IMAGE_SIZE)),
        DEFAULT_IMAGE_SIZE,
    )
    architecture = str(metadata.get("architecture", "")).lower()

    # ResNet18 Step 5 saves a TorchScript model. Use TorchScript first for ResNet,
    # because the .pth checkpoint state_dict is not compatible with the old FastCNN class.
    if TORCHSCRIPT_PATH.exists() and "resnet" in architecture:
        model = torch.jit.load(str(TORCHSCRIPT_PATH), map_location="cpu")
        model.eval()
        return model, metadata, classes, image_size, "torchscript_resnet18"

    # Old Step 2 CNN checkpoint support.
    if MODEL_PATH.exists():
        checkpoint = torch.load(str(MODEL_PATH), map_location="cpu")

        if isinstance(checkpoint, dict):
            checkpoint_architecture = str(checkpoint.get("architecture", "")).lower()

            # If the checkpoint is ResNet, avoid loading it into FastCNN.
            # Fall back to TorchScript, which is architecture-independent for inference.
            if "resnet" in checkpoint_architecture and TORCHSCRIPT_PATH.exists():
                checkpoint_metadata = checkpoint.get("metadata")
                if isinstance(checkpoint_metadata, dict):
                    metadata.update(checkpoint_metadata)
                classes = _classes_from_payload(checkpoint) or classes
                image_size = _coerce_image_size(
                    checkpoint.get("image_size", metadata.get("input_size", image_size)),
                    image_size,
                )
                model = torch.jit.load(str(TORCHSCRIPT_PATH), map_location="cpu")
                model.eval()
                return model, metadata, classes, image_size, "torchscript_resnet18"

            checkpoint_classes = _classes_from_payload(checkpoint)
            if checkpoint_classes:
                classes = checkpoint_classes
            image_size = _coerce_image_size(
                checkpoint.get("input_size", checkpoint.get("image_size", image_size)),
                image_size,
            )
            state_dict = checkpoint.get("model_state_dict", checkpoint)
        else:
            state_dict = checkpoint

        model = FastCNN(n_classes=len(classes))
        model.load_state_dict(state_dict)
        model.eval()
        return model, metadata, classes, image_size, "checkpoint_fastcnn"

    if TORCHSCRIPT_PATH.exists():
        model = torch.jit.load(str(TORCHSCRIPT_PATH), map_location="cpu")
        model.eval()
        return model, metadata, classes, image_size, "torchscript"

    raise FileNotFoundError(
        "Image model file was not found. Expected one of:\n"
        f"- {MODEL_PATH}\n"
        f"- {TORCHSCRIPT_PATH}\n\n"
        "Run Step 2 or Step 5 first."
    )


def _uploaded_file_to_bytes(uploaded_file: Any) -> bytes:
    if uploaded_file is None:
        raise ValueError("No uploaded image was provided.")

    if isinstance(uploaded_file, (str, Path)):
        return Path(uploaded_file).read_bytes()

    if hasattr(uploaded_file, "getvalue"):
        return bytes(uploaded_file.getvalue())

    if hasattr(uploaded_file, "read"):
        try:
            uploaded_file.seek(0)
        except Exception:
            pass
        data = uploaded_file.read()
        try:
            uploaded_file.seek(0)
        except Exception:
            pass
        return bytes(data)

    raise TypeError("Unsupported uploaded_file object. Expected Streamlit upload, file object, bytes path, or Path.")


def _preprocess_image_bytes(image_bytes: bytes, image_size: int):
    torch, _ = _import_torch()

    try:
        with Image.open(BytesIO(image_bytes)) as img:
            img = ImageOps.exif_transpose(img)
            img = img.convert("RGB")
            img = img.resize((image_size, image_size), Image.Resampling.LANCZOS)
            arr = np.asarray(img).astype("float32") / 255.0
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError(f"Uploaded file is not a readable image: {exc}") from exc

    arr = (arr - NORMALIZE_MEAN) / NORMALIZE_STD
    arr = np.transpose(arr, (2, 0, 1))
    tensor = torch.tensor(arr, dtype=torch.float32).unsqueeze(0)
    return tensor


def _format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def _model_accuracy_text(metadata: dict[str, Any]) -> str:
    accuracy = metadata.get("test_accuracy")
    if isinstance(accuracy, (int, float)):
        return _format_percent(float(accuracy))
    return "Model trained"


def _data_analyzed_text(metadata: dict[str, Any]) -> str:
    train_rows = int(metadata.get("train_rows", 0) or 0)
    validation_rows = int(metadata.get("validation_rows", 0) or 0)
    test_rows = int(metadata.get("test_rows", 0) or 0)
    total = train_rows + validation_rows + test_rows
    if total > 0:
        return f"{total} balanced training images"
    return "Flood / Non-Flood / Unrelated classes"


def _risk_from_prediction(predicted_class: str, confidence: float) -> tuple[str, str, int, str, list[str]]:
    """Convert raw model output into the UI fields expected by tabs/image_analysis.py.

    Step 4 adds safer decision calibration:
    - Very low confidence predictions are treated as "uncertain", not as a confirmed flood.
    - Flood is shown as Medium/High only when the confidence is strong enough.
    - Unrelated images are rejected clearly.
    """
    label = str(predicted_class or "").strip()
    conf_pct = int(round(float(confidence) * 100))

    # Calibration thresholds. These are intentionally simple and easy to explain in the report.
    MIN_CONFIRMED_CONFIDENCE = 0.55
    FLOOD_MEDIUM_CONFIDENCE = 0.60
    FLOOD_HIGH_CONFIDENCE = 0.80

    if label == "Unrelated":
        return (
            "No",
            "Low",
            0,
            "The uploaded image appears unrelated to flood analysis. Please upload a clear outdoor photo of roads, ground, drainage, rivers, or flooded areas.",
            [
                "Upload a flood-related image",
                "Use a clear JPG, PNG, or JPEG photo",
                "Avoid random objects, documents, screenshots, or unrelated photos",
            ],
        )

    if float(confidence) < MIN_CONFIRMED_CONFIDENCE:
        return (
            "No",
            "Low",
            0,
            f"The model is not confident enough to make a confirmed flood decision. It predicted {label} with {conf_pct}% confidence, so this result should be treated as uncertain.",
            [
                "Upload a clearer outdoor image",
                "Make sure water, road, ground, drain, or river areas are visible",
                "Do not rely on this low-confidence result for emergency decisions",
            ],
        )

    if label == "Flood":
        if float(confidence) >= FLOOD_HIGH_CONFIDENCE:
            return (
                "Yes",
                "High",
                38,
                "The image appears to show clear flood conditions. Water may be covering roads, ground areas, or access routes, so movement can be unsafe.",
                [
                    "Do not drive through floodwater",
                    "Move to higher ground if the water is rising",
                    "Follow local flood warnings and emergency guidance",
                ],
            )

        if float(confidence) >= FLOOD_MEDIUM_CONFIDENCE:
            return (
                "Yes",
                "Medium",
                25,
                "The model detected possible flood conditions with moderate confidence. Continue checking the area carefully and monitor rainfall.",
                [
                    "Avoid low-lying roads",
                    "Prepare emergency supplies",
                    "Monitor official flood updates",
                ],
            )

        return (
            "No",
            "Low",
            0,
            f"The model weakly predicted Flood with only {conf_pct}% confidence. This is not strong enough to confirm flooding.",
            [
                "Upload a clearer image of the affected area",
                "Check official local flood warnings",
                "Use the Flood Risk Predictor page for environmental risk input",
            ],
        )

    if label == "Non_Flood":
        return (
            "No",
            "Low",
            6,
            "The image does not show strong flood indicators. The area appears mostly non-flooded in the uploaded photo.",
            [
                "Continue monitoring rainfall",
                "Keep nearby drains clear",
                "Stay alert if weather conditions worsen",
            ],
        )

    # Unknown/fallback label.
    return (
        "No",
        "Low",
        0,
        f"The model returned an unexpected class: {label}. Please upload a clearer flood-related image and test again.",
        [
            "Check the image class mapping file in models/",
            "Run python scripts/04_test_image_result_calibration.py",
            "Retrain the model if class labels are incorrect",
        ],
    )

def predict_uploaded_image(uploaded_file: Any) -> dict[str, Any]:
    torch, _ = _import_torch()
    model, metadata, classes, image_size, source = _load_model_cached()

    image_bytes = _uploaded_file_to_bytes(uploaded_file)
    tensor = _preprocess_image_bytes(image_bytes, image_size)

    with torch.no_grad():
        logits = model(tensor)
        probabilities_tensor = torch.softmax(logits, dim=1)[0]
        probabilities = probabilities_tensor.cpu().numpy().astype(float).tolist()

    predicted_idx = int(np.argmax(probabilities))
    predicted_class = classes[predicted_idx] if predicted_idx < len(classes) else str(predicted_idx)
    confidence = float(probabilities[predicted_idx])

    return {
        "predicted_class": predicted_class,
        "confidence_float": confidence,
        "confidence": int(round(confidence * 100)),
        "probabilities": {
            classes[index]: round(float(prob), 4)
            for index, prob in enumerate(probabilities)
            if index < len(classes)
        },
        "model_source": source,
        "metadata": metadata,
    }


def predict_image_path(image_path: str | Path) -> dict[str, Any]:
    return predict_uploaded_image(Path(image_path))


def analyze_uploaded_image(
    uploaded_file: Any = None,
    file_name: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    """Return the result shape expected by tabs/image_analysis.py."""
    detected_file_name = str(file_name or "").strip()

    if uploaded_file is not None and not detected_file_name:
        detected_file_name = str(getattr(uploaded_file, "name", "") or "").strip()

    if not detected_file_name:
        detected_file_name = str(kwargs.get("name", "") or kwargs.get("filename", "") or "Uploaded image")

    try:
        prediction = predict_uploaded_image(uploaded_file)
        predicted_class = str(prediction["predicted_class"])
        confidence = float(prediction["confidence_float"])
        metadata = dict(prediction.get("metadata", {}) or {})

        flood_detected, risk_level, water_coverage, context, recommendations = _risk_from_prediction(
            predicted_class=predicted_class,
            confidence=confidence,
        )

        return {
            "file_name": detected_file_name,
            "flood_detected": flood_detected,
            "risk_level": risk_level,
            "confidence": int(round(confidence * 100)),
            "water_coverage": water_coverage,
            "context": context,
            "recommendations": recommendations,
            "model": metadata.get("model_name", "FloodMind Image Classifier"),
            "model_name": metadata.get("model_name", "FloodMind Image Classifier"),
            "accuracy": _model_accuracy_text(metadata),
            "data_analyzed": _data_analyzed_text(metadata),
            "predicted_class": predicted_class,
            "probabilities": prediction.get("probabilities", {}),
        }

    except Exception as error:
        return {
            "file_name": detected_file_name,
            "flood_detected": "No",
            "risk_level": "Low",
            "confidence": 0,
            "water_coverage": 0,
            "context": f"The image AI model could not run. Technical error: {error}",
            "recommendations": [
                "Check that Step 2 model files exist inside models/",
                "Check that PyTorch is installed in the active virtual environment",
                "Run python scripts/03_test_image_app_integration.py",
            ],
            "model": metadata.get("model_name", "FloodMind Image Classifier"),
            "model_name": metadata.get("model_name", "FloodMind Image Classifier"),
            "accuracy": "Unavailable",
            "data_analyzed": "Unavailable",
        }
