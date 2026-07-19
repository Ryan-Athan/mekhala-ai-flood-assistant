from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.flood_risk_model_service import predict_flood_risk_from_ui, ui_inputs_to_feature_row

TEST_CASES = {
    "screenshot_default": {
        "rainfall": 2,
        "weather_worse": 1,
        "area_type": 2,
        "coast_distance": 3,
        "river_control": 3,
        "dam_condition": 1,
        "drainage_quality": 2,
    },
    "safer_conditions": {
        "rainfall": 0,
        "weather_worse": 0,
        "area_type": 2,
        "coast_distance": 0,
        "river_control": 2,
        "dam_condition": 2,
        "drainage_quality": 2,
    },
    "danger_conditions": {
        "rainfall": 3,
        "weather_worse": 2,
        "area_type": 0,
        "coast_distance": 2,
        "river_control": 0,
        "dam_condition": 0,
        "drainage_quality": 0,
    },
}


def main() -> None:
    print("FloodMind Flood Risk Predictor AI integration test")
    print("=" * 64)

    outputs = {}

    for name, ui_inputs in TEST_CASES.items():
        feature_row = ui_inputs_to_feature_row(ui_inputs)
        prediction = predict_flood_risk_from_ui(ui_inputs)
        outputs[name] = {
            "ui_inputs": ui_inputs,
            "model_features": feature_row.iloc[0].to_dict(),
            "prediction": prediction,
        }

        print(f"\nCASE: {name}")
        print("UI inputs:", ui_inputs)
        print("Model features:", feature_row.iloc[0].to_dict())
        print("Prediction:")
        print(json.dumps(prediction, indent=2, ensure_ascii=False))

    report_path = PROJECT_ROOT / "reports" / "03_APP_INTEGRATION_TEST_OUTPUT.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(outputs, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved integration output to: {report_path}")


if __name__ == "__main__":
    main()
