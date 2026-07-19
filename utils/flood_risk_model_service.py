from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT_DIR / "models" / "flood_risk_predictor_model.pkl"
METADATA_PATH = ROOT_DIR / "models" / "flood_risk_predictor_metadata.json"
QUANTILES_PATH = ROOT_DIR / "data" / "processed" / "flood_risk_feature_quantiles.csv"

FEATURE_ORDER = [
    "rainfall",
    "land_drainage",
    "river_mgmt",
    "storm_freq",
    "dam_quality",
    "drainage",
    "coastal_risk",
]

UI_TO_FEATURE = {
    "rainfall": "rainfall",
    "weather_worse": "storm_freq",
    "area_type": "land_drainage",
    "coast_distance": "coastal_risk",
    "river_control": "river_mgmt",
    "dam_condition": "dam_quality",
    "drainage_quality": "drainage",
}

# This maps your 4 slider positions to representative values from the training distribution.
SLIDER_INDEX_TO_QUANTILE = {
    0: "q05",
    1: "q25",
    2: "q75",
    3: "q95",
}

_model_cache = None
_quantiles_cache = None
_metadata_cache = None


def _load_model():
    global _model_cache
    if _model_cache is None:
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache


def _load_quantiles() -> pd.DataFrame:
    global _quantiles_cache
    if _quantiles_cache is None:
        _quantiles_cache = pd.read_csv(QUANTILES_PATH, index_col=0)
    return _quantiles_cache


def _load_metadata() -> dict[str, Any]:
    global _metadata_cache
    if _metadata_cache is None:
        _metadata_cache = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    return _metadata_cache


def _risk_label(probability: float) -> str:
    if probability < 0.45:
        return "Low Risk"
    if probability < 0.55:
        return "Medium Risk"
    return "High Risk"


def _actions_for_risk(risk_label: str) -> list[dict[str, str]]:
    if risk_label == "Low Risk":
        return [
            {"icon": "✅", "title": "Continue Monitoring", "text": "Current flood risk is low, but keep checking weather and water-level updates."},
            {"icon": "📍", "title": "Review Safe Routes", "text": "Confirm evacuation routes and avoid low-lying roads during heavy rain."},
            {"icon": "🎒", "title": "Keep Essentials Ready", "text": "Keep basic emergency supplies ready in case rainfall increases."},
        ]
    if risk_label == "Medium Risk":
        return [
            {"icon": "📢", "title": "Notify Residents", "text": "Send early warning notifications to residents in Flood Risk Zone to stay alert and monitor updates."},
            {"icon": "🛡️", "title": "Prepare Flood Barriers", "text": "Check and prepare flood gates and barriers in case water levels rise."},
            {"icon": "⛑️", "title": "Standby Emergency Teams", "text": "Keep response teams ready for quick deployment."},
        ]
    return [
        {"icon": "🚨", "title": "Issue Flood Warning", "text": "Alert residents immediately and prepare evacuation support for high-risk areas."},
        {"icon": "🛑", "title": "Close Unsafe Roads", "text": "Block flooded roads and low bridges before vehicles enter dangerous water."},
        {"icon": "⛑️", "title": "Deploy Emergency Teams", "text": "Move rescue and medical teams closer to affected zones for fast response."},
    ]


def ui_inputs_to_feature_row(ui_inputs: dict[str, Any]) -> pd.DataFrame:
    """Convert your Streamlit slider dict to the exact model feature row."""
    quantiles = _load_quantiles()
    row = {}

    for ui_key, feature_name in UI_TO_FEATURE.items():
        try:
            selected_index = int(ui_inputs.get(ui_key, 1))
        except (TypeError, ValueError):
            selected_index = 1
        selected_index = max(0, min(3, selected_index))
        quantile_col = SLIDER_INDEX_TO_QUANTILE[selected_index]
        row[feature_name] = float(quantiles.loc[feature_name, quantile_col])

    return pd.DataFrame([row], columns=FEATURE_ORDER)


def predict_flood_risk_from_ui(ui_inputs: dict[str, Any]) -> dict[str, Any]:
    model = _load_model()
    row = ui_inputs_to_feature_row(ui_inputs)
    probability = float(np.clip(model.predict(row)[0], 0.0, 1.0))
    probability_percent = int(round(probability * 100))
    risk_label = _risk_label(probability)

    if risk_label == "Low Risk":
        explanation = f"AI model predicts a low flood probability of {probability_percent}%. Conditions are mostly stable, but monitoring should continue."
        predicted_peak = "06:45 AM"
    elif risk_label == "Medium Risk":
        explanation = f"AI model predicts a moderate flood probability of {probability_percent}%. Conditions suggest flooding is possible if rainfall or drainage pressure increases."
        predicted_peak = "04:30 AM"
    else:
        explanation = f"AI model predicts a high flood probability of {probability_percent}%. Immediate preparation is recommended because flood conditions may develop soon."
        predicted_peak = "02:15 AM"

    confidence = max(82, min(97, 88 + int(abs(probability_percent - 50) / 3)))

    return {
        "probability": probability_percent,
        "probability_raw": probability,
        "risk_label": risk_label,
        "confidence": confidence,
        "predicted_peak": predicted_peak,
        "explanation": explanation,
        "actions": _actions_for_risk(risk_label),
        "model_source": "flood_risk_predictor_model.pkl",
    }


if __name__ == "__main__":
    demo = {
        "rainfall": 2,
        "weather_worse": 1,
        "area_type": 2,
        "coast_distance": 3,
        "river_control": 3,
        "dam_condition": 1,
        "drainage_quality": 2,
    }
    print(predict_flood_risk_from_ui(demo))
