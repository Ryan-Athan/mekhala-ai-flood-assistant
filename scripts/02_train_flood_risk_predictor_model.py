from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT_DIR / "data" / "processed" / "flood_risk_clean_full.csv"
FALLBACK_DATA_PATH = ROOT_DIR / "data" / "processed" / "flood_risk_model_training_sample_50000.csv"
MODEL_DIR = ROOT_DIR / "models"
REPORT_DIR = ROOT_DIR / "reports"

FEATURES = [
    "rainfall",
    "land_drainage",
    "river_mgmt",
    "storm_freq",
    "dam_quality",
    "drainage",
    "coastal_risk",
]
TARGET = "flood_probability"


def risk_band(values):
    values = np.asarray(values)
    return np.where(values < 0.45, "Low Risk", np.where(values < 0.55, "Medium Risk", "High Risk"))


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if DATA_PATH.exists():
        data_path = DATA_PATH
    elif FALLBACK_DATA_PATH.exists():
        data_path = FALLBACK_DATA_PATH
    else:
        raise FileNotFoundError(
            "Could not find training data. Place Step 1 output at "
            "data/processed/flood_risk_clean_full.csv"
        )

    df = pd.read_csv(data_path, usecols=FEATURES + [TARGET])
    df = df.apply(pd.to_numeric, errors="coerce").dropna().drop_duplicates().reset_index(drop=True)

    # For very large data, this model is still fast. Keep all rows by default.
    X = df[FEATURES].astype("float32")
    y = df[TARGET].astype("float32")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Pipeline([
        ("polynomial_features", PolynomialFeatures(degree=2, include_bias=False)),
        ("ridge_regressor", Ridge(alpha=1.0)),
    ])

    model.fit(X_train, y_train)
    y_pred = np.clip(model.predict(X_test), 0.0, 1.0)

    true_band = risk_band(y_test)
    pred_band = risk_band(y_pred)

    metrics = {
        "created_at": datetime.utcnow().isoformat() + "Z",
        "data_path": str(data_path),
        "rows": int(len(df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "model_type": "PolynomialFeatures(degree=2) + Ridge Regression",
        "features": FEATURES,
        "target": TARGET,
        "regression": {
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "rmse": float(mean_squared_error(y_test, y_pred) ** 0.5),
            "r2_score": float(r2_score(y_test, y_pred)),
        },
        "risk_band_classification": {
            "accuracy": float(accuracy_score(true_band, pred_band)),
            "balanced_accuracy": float(balanced_accuracy_score(true_band, pred_band)),
            "macro_f1": float(f1_score(true_band, pred_band, average="macro")),
            "weighted_f1": float(f1_score(true_band, pred_band, average="weighted")),
        },
        "risk_band_thresholds": {
            "Low Risk": "flood_probability < 0.45",
            "Medium Risk": "0.45 <= flood_probability < 0.55",
            "High Risk": "flood_probability >= 0.55",
        },
    }

    joblib.dump(model, MODEL_DIR / "flood_risk_predictor_model.pkl")
    (MODEL_DIR / "flood_risk_predictor_metadata.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (REPORT_DIR / "02_MODEL_TRAINING_METRICS.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (REPORT_DIR / "02_RISK_BAND_CLASSIFICATION_REPORT.txt").write_text(
        classification_report(true_band, pred_band, labels=["Low Risk", "Medium Risk", "High Risk"], zero_division=0),
        encoding="utf-8",
    )
    pd.DataFrame(
        confusion_matrix(true_band, pred_band, labels=["Low Risk", "Medium Risk", "High Risk"]),
        index=["true_low", "true_medium", "true_high"],
        columns=["pred_low", "pred_medium", "pred_high"],
    ).to_csv(REPORT_DIR / "02_RISK_BAND_CONFUSION_MATRIX.csv")

    print("Flood risk predictor model trained successfully.")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
