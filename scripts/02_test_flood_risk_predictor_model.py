from __future__ import annotations

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from utils.flood_risk_model_service import predict_flood_risk_from_ui

TEST_CASES = [
    {
        "name": "Default UI values",
        "values": {
            "rainfall": 2,
            "weather_worse": 1,
            "area_type": 2,
            "coast_distance": 3,
            "river_control": 3,
            "dam_condition": 1,
            "drainage_quality": 2,
        },
    },
    {
        "name": "Safer conditions",
        "values": {
            "rainfall": 0,
            "weather_worse": 0,
            "area_type": 2,
            "coast_distance": 0,
            "river_control": 2,
            "dam_condition": 2,
            "drainage_quality": 2,
        },
    },
    {
        "name": "High-risk conditions",
        "values": {
            "rainfall": 3,
            "weather_worse": 2,
            "area_type": 0,
            "coast_distance": 2,
            "river_control": 0,
            "dam_condition": 0,
            "drainage_quality": 0,
        },
    },
]

for case in TEST_CASES:
    print("=" * 80)
    print(case["name"])
    print(predict_flood_risk_from_ui(case["values"]))
