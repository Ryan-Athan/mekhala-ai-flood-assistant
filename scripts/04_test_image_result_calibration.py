from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.image_model_service import analyze_uploaded_image, predict_image_path

DATA_DIR = PROJECT_ROOT / "data" / "processed" / "image_dataset_balanced_224"
REPORTS_DIR = PROJECT_ROOT / "reports"
CLASSES = ["Flood", "Non_Flood", "Unrelated"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def list_images(class_name: str) -> list[Path]:
    folder = DATA_DIR / class_name
    if not folder.exists():
        raise FileNotFoundError(f"Missing dataset class folder: {folder}")
    images = sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )
    if not images:
        raise FileNotFoundError(f"No images found for class {class_name}: {folder}")
    return images


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("\nFloodMind Step 4 Image Result Calibration Test")
    print("=" * 58)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Dataset folder: {DATA_DIR}")

    rows: list[dict[str, object]] = []
    confusion: dict[str, Counter] = defaultdict(Counter)

    for true_class in CLASSES:
        images = list_images(true_class)
        print(f"\nTesting {true_class}: {len(images)} images")

        for image_path in images:
            raw_pred = predict_image_path(image_path)

            with image_path.open("rb") as file_obj:
                app_result = analyze_uploaded_image(file_obj, file_name=image_path.name)

            predicted_class = str(raw_pred.get("predicted_class", ""))
            confusion[true_class][predicted_class] += 1

            rows.append(
                {
                    "true_class": true_class,
                    "file_name": image_path.name,
                    "predicted_class": predicted_class,
                    "confidence": raw_pred.get("confidence"),
                    "probabilities": json.dumps(raw_pred.get("probabilities", {}), ensure_ascii=False),
                    "ui_flood_detected": app_result.get("flood_detected"),
                    "ui_risk_level": app_result.get("risk_level"),
                    "ui_context": app_result.get("context"),
                }
            )

    total = len(rows)
    correct = sum(1 for row in rows if row["true_class"] == row["predicted_class"])
    accuracy = correct / total if total else 0.0

    by_class = {}
    for class_name in CLASSES:
        class_rows = [row for row in rows if row["true_class"] == class_name]
        class_correct = sum(1 for row in class_rows if row["true_class"] == row["predicted_class"])
        by_class[class_name] = {
            "count": len(class_rows),
            "correct": class_correct,
            "accuracy": round(class_correct / len(class_rows), 4) if class_rows else 0,
            "predicted_distribution": dict(confusion[class_name]),
        }

    summary = {
        "total_images_tested": total,
        "correct_predictions": correct,
        "raw_model_accuracy": round(accuracy, 4),
        "raw_model_accuracy_percent": round(accuracy * 100, 2),
        "class_summary": by_class,
        "ui_policy": {
            "low_confidence_below_percent": 55,
            "flood_medium_from_percent": 60,
            "flood_high_from_percent": 80,
            "unrelated_images": "Rejected as not flood-related",
        },
    }

    json_path = REPORTS_DIR / "04_IMAGE_RESULT_CALIBRATION_TEST.json"
    csv_path = REPORTS_DIR / "04_IMAGE_RESULT_CALIBRATION_PREDICTIONS.csv"

    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print("\nStep 4 result calibration test complete.")
    print(f"Total images tested: {total}")
    print(f"Raw model accuracy: {accuracy * 100:.2f}%")
    print("\nClass summary:")
    for class_name, data in by_class.items():
        print(f"- {class_name}: {data['correct']}/{data['count']} correct | accuracy={data['accuracy']}")
        print(f"  Predicted distribution: {data['predicted_distribution']}")

    print(f"\nSaved summary: {json_path}")
    print(f"Saved predictions: {csv_path}")


if __name__ == "__main__":
    main()
