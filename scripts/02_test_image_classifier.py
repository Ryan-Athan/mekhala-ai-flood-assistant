from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "flood_image_classifier_cnn.pth"


class FastCNN(nn.Module):
    def __init__(self, n: int = 3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 12, 3, padding=1), nn.BatchNorm2d(12), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(12, 24, 3, padding=1), nn.BatchNorm2d(24), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(24, 48, 3, padding=1), nn.BatchNorm2d(48), nn.ReLU(), nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(), nn.Dropout(0.2), nn.Linear(48, n),
        )

    def forward(self, x):
        return self.net(x)


def preprocess_image(path: Path, input_size: int) -> torch.Tensor:
    img = Image.open(path).convert("RGB").resize((input_size, input_size))
    arr = np.asarray(img).astype("float32") / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype="float32")
    std = np.array([0.229, 0.224, 0.225], dtype="float32")
    arr = (arr - mean) / std
    arr = np.transpose(arr, (2, 0, 1))
    return torch.tensor(arr, dtype=torch.float32).unsqueeze(0)


def predict(path: str) -> dict:
    payload = torch.load(MODEL_PATH, map_location="cpu")
    idx_to_class = {int(k): v for k, v in payload["idx_to_class"].items()} if isinstance(next(iter(payload["idx_to_class"].keys())), str) else payload["idx_to_class"]
    input_size = int(payload.get("input_size", 48))
    model = FastCNN(len(idx_to_class))
    model.load_state_dict(payload["model_state_dict"])
    model.eval()

    x = preprocess_image(Path(path), input_size)
    with torch.no_grad():
        probs = torch.softmax(model(x), dim=1)[0].numpy()
    pred_idx = int(np.argmax(probs))
    return {
        "predicted_class": idx_to_class[pred_idx],
        "confidence": float(probs[pred_idx]),
        "probabilities": {idx_to_class[i]: float(probs[i]) for i in range(len(probs))},
    }


if __name__ == "__main__":
    sample_dir = ROOT / "data" / "processed" / "image_dataset_balanced_224"
    sample_files = list(sample_dir.glob("*/*"))[:6]
    for sample in sample_files:
        print("IMAGE:", sample)
        print(json.dumps(predict(str(sample)), indent=2))
