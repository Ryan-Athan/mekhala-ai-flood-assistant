from __future__ import annotations

import json
from pathlib import Path

from utils.image_model_service import predict_image_path, analyze_uploaded_image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed" / "image_dataset_balanced_224"
REPORTS_DIR = PROJECT_ROOT / "reports"
CLASSES = ["Flood", "Non_Flood", "Unrelated"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def find_sample_image(class_name: str) -> Path:
    folder = DATA_DIR / class_name
    if not folder.exists():
        raise FileNotFoundError(f"Missing folder: {folder}")

    images = sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )

    if not images:
        raise FileNotFoundError(f"No images found in: {folder}")

    return images[0]


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("\nFloodMind Step 3 Image App Integration Test")
    print("=" * 52)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Dataset folder: {DATA_DIR}")

    results = []

    for class_name in CLASSES:
        sample_path = find_sample_image(class_name)
        prediction = predict_image_path(sample_path)

        with sample_path.open("rb") as file_obj:
            app_result = analyze_uploaded_image(
                uploaded_file=file_obj,
                file_name=sample_path.name,
            )

        row = {
            "sample_class_folder": class_name,
            "sample_file": str(sample_path),
            "predicted_class": prediction.get("predicted_class"),
            "confidence": prediction.get("confidence"),
            "app_flood_detected": app_result.get("flood_detected"),
            "app_risk_level": app_result.get("risk_level"),
            "app_model": app_result.get("model"),
        }
        results.append(row)

        print("\nSample:", class_name)
        print("File:", sample_path.name)
        print("Predicted class:", row["predicted_class"])
        print("Confidence:", f'{row["confidence"]}%')
        print("UI flood detected:", row["app_flood_detected"])
        print("UI risk level:", row["app_risk_level"])

    output_path = REPORTS_DIR / "03_IMAGE_APP_INTEGRATION_TEST.json"
    output_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    print("\nStep 3 integration test complete.")
    print(f"Saved report: {output_path}")


if __name__ == "__main__":
    main()
