from __future__ import annotations

"""
Step 2: Train Flood/Disaster Intent Classifier

This script trains the AI Flood Assistant intent classifier using the cleaned
Kaggle Disaster Response Messages dataset from Step 1.

Input:
    data/processed/clean_flood_disaster_chatbot_messages.csv

Outputs:
    data/processed/flood_intent_training_data.csv
    data/processed/flood_intent_label_summary.csv
    models/flood_disaster_intent_classifier.pkl
    models/flood_disaster_intent_metadata.json
    models/intent_mapping.json
    reports/02_CLASSIFICATION_REPORT.txt
    reports/02_TRAINING_METRICS.json
    reports/02_CONFUSION_MATRIX.csv
    reports/02_SAMPLE_PREDICTIONS.csv
    reports/02_TOP_FEATURES.csv
"""

import json
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "processed" / "clean_flood_disaster_chatbot_messages.csv"
OUTPUT_TRAINING_DATA = BASE_DIR / "data" / "processed" / "flood_intent_training_data.csv"
OUTPUT_LABEL_SUMMARY = BASE_DIR / "data" / "processed" / "flood_intent_label_summary.csv"
MODEL_PATH = BASE_DIR / "models" / "flood_disaster_intent_classifier.pkl"
METADATA_PATH = BASE_DIR / "models" / "flood_disaster_intent_metadata.json"
MAPPING_PATH = BASE_DIR / "models" / "intent_mapping.json"
REPORT_PATH = BASE_DIR / "reports" / "02_CLASSIFICATION_REPORT.txt"
METRICS_PATH = BASE_DIR / "reports" / "02_TRAINING_METRICS.json"
CONFUSION_PATH = BASE_DIR / "reports" / "02_CONFUSION_MATRIX.csv"
SAMPLE_PREDICTIONS_PATH = BASE_DIR / "reports" / "02_SAMPLE_PREDICTIONS.csv"
TOP_FEATURES_PATH = BASE_DIR / "reports" / "02_TOP_FEATURES.csv"


# Priority-based mapping from multi-label disaster categories to one chatbot intent.
# The dataset is multi-label, but a chatbot usually needs one routing intent for the answer engine.
INTENT_RULES = [
    {
        "intent": "search_and_rescue",
        "description": "Search, rescue, missing people, trapped people, and urgent rescue support.",
        "dataset_labels": ["search_and_rescue", "missing_people"],
    },
    {
        "intent": "medical_help",
        "description": "Medical help, medicine, hospital access, injury, death, and health-related needs.",
        "dataset_labels": ["medical_help", "medical_products", "hospitals", "death"],
    },
    {
        "intent": "water_supply",
        "description": "Requests or reports about clean water, drinking water, and sanitation needs.",
        "dataset_labels": ["water"],
    },
    {
        "intent": "food_supply",
        "description": "Food shortage, food aid, and basic nutrition support messages.",
        "dataset_labels": ["food"],
    },
    {
        "intent": "shelter_evacuation",
        "description": "Shelter, temporary housing, displacement, evacuation, and refugee support.",
        "dataset_labels": ["shelter", "refugees"],
    },
    {
        "intent": "road_transport",
        "description": "Transport disruption, road access, blocked roads, vehicles, and route safety.",
        "dataset_labels": ["transport"],
    },
    {
        "intent": "infrastructure_damage",
        "description": "Damage to buildings, drainage, bridges, electricity, and infrastructure systems.",
        "dataset_labels": ["buildings", "electricity", "infrastructure_related", "other_infrastructure"],
    },
    {
        "intent": "security_services",
        "description": "Security, military, aid centers, shops, tools, and public service coordination.",
        "dataset_labels": ["security", "military", "aid_centers", "shops", "tools"],
    },
    {
        "intent": "flood_event",
        "description": "Flood-specific messages, flood impact, river overflow, and water inundation reports.",
        "dataset_labels": ["floods"],
    },
    {
        "intent": "storm_weather",
        "description": "Storm, hurricane, cyclone, and severe weather event messages.",
        "dataset_labels": ["storm"],
    },
    {
        "intent": "weather_warning",
        "description": "General weather hazard, earthquake, cold, fire, or other weather-related alerts.",
        "dataset_labels": ["weather_related", "other_weather", "cold", "fire", "earthquake"],
    },
    {
        "intent": "general_aid_request",
        "description": "General help requests, aid-related reports, and direct disaster reports.",
        "dataset_labels": ["request", "aid_related", "other_aid", "direct_report", "related"],
    },
]

def assign_primary_intent(row: pd.Series) -> str:
    """Convert multi-label disaster categories into one chatbot intent using priority rules."""
    for rule in INTENT_RULES:
        for label in rule["dataset_labels"]:
            if label in row.index and int(row.get(label, 0)) == 1:
                return rule["intent"]
    return "general_aid_request"


def build_training_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "message_clean" not in df.columns:
        raise ValueError("Expected column 'message_clean' not found. Run Step 1 cleaning first.")

    df["message_clean"] = df["message_clean"].fillna("").astype(str).str.strip()
    df = df[df["message_clean"].str.len() > 0].copy()

    df["primary_intent"] = df.apply(assign_primary_intent, axis=1)

    keep_columns = [
        "id",
        "message_clean",
        "message_clean_lower",
        "genre",
        "message_word_count",
        "active_label_count",
        "active_labels",
        "primary_intent",
    ]

    label_columns = sorted({label for rule in INTENT_RULES for label in rule["dataset_labels"] if label in df.columns})
    keep_columns += label_columns
    keep_columns = [col for col in keep_columns if col in df.columns]

    return df[keep_columns].copy()


def create_pipeline() -> Pipeline:
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.95,
                    max_features=30000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LinearSVC(
                    class_weight="balanced",
                    random_state=42,
                    max_iter=5000,
                ),
            ),
        ]
    )


def get_top_features(model: Pipeline, class_names: list[str], top_n: int = 15) -> pd.DataFrame:
    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]
    feature_names = np.array(vectorizer.get_feature_names_out())

    rows = []
    for class_index, class_name in enumerate(class_names):
        coefficients = classifier.coef_[class_index]
        top_indices = np.argsort(coefficients)[-top_n:][::-1]
        for rank, feature_index in enumerate(top_indices, start=1):
            rows.append(
                {
                    "intent": class_name,
                    "rank": rank,
                    "feature": feature_names[feature_index],
                    "coefficient": float(coefficients[feature_index]),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    for path in [OUTPUT_TRAINING_DATA.parent, MODEL_PATH.parent, REPORT_PATH.parent]:
        path.mkdir(parents=True, exist_ok=True)

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Missing cleaned dataset: {DATA_PATH}")

    raw_df = pd.read_csv(DATA_PATH)
    training_df = build_training_data(raw_df)
    training_df.to_csv(OUTPUT_TRAINING_DATA, index=False)

    label_summary = (
        training_df["primary_intent"]
        .value_counts()
        .rename_axis("intent")
        .reset_index(name="message_count")
    )
    label_summary["percentage"] = (label_summary["message_count"] / len(training_df) * 100).round(2)
    label_summary.to_csv(OUTPUT_LABEL_SUMMARY, index=False)

    X = training_df["message_clean"].astype(str)
    y = training_df["primary_intent"].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    model = create_pipeline()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    labels = sorted(y.unique())
    accuracy = accuracy_score(y_test, y_pred)
    balanced_accuracy = balanced_accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    weighted_f1 = f1_score(y_test, y_pred, average="weighted")

    precision, recall, f1, support = precision_recall_fscore_support(
        y_test,
        y_pred,
        labels=labels,
        zero_division=0,
    )

    per_class_rows = []
    for label, p, r, f, s in zip(labels, precision, recall, f1, support):
        per_class_rows.append(
            {
                "intent": label,
                "precision": round(float(p), 4),
                "recall": round(float(r), 4),
                "f1_score": round(float(f), 4),
                "support": int(s),
            }
        )

    report_text = classification_report(y_test, y_pred, labels=labels, zero_division=0)
    REPORT_PATH.write_text(report_text, encoding="utf-8")

    cm = confusion_matrix(y_test, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    cm_df.to_csv(CONFUSION_PATH)

    sample_predictions = pd.DataFrame(
        {
            "message": X_test.reset_index(drop=True),
            "actual_intent": y_test.reset_index(drop=True),
            "predicted_intent": pd.Series(y_pred),
        }
    ).head(120)
    sample_predictions.to_csv(SAMPLE_PREDICTIONS_PATH, index=False)

    top_features = get_top_features(model, labels, top_n=15)
    top_features.to_csv(TOP_FEATURES_PATH, index=False)

    joblib.dump(model, MODEL_PATH)

    metadata = {
        "project": "FloodMind / AI Flood Assistant",
        "step": "Step 2 - Flood/Disaster Intent Classifier Training",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "dataset_source": "Kaggle Disaster Response Messages dataset after Step 1 cleaning",
        "training_data": str(OUTPUT_TRAINING_DATA.as_posix()),
        "input_column": "message_clean",
        "target_column": "primary_intent",
        "model_type": "TF-IDF + LinearSVC intent classifier",
        "vectorizer": "TfidfVectorizer with 1-2 word ngrams, max_features=30000, sublinear_tf=True",
        "classifier": "LinearSVC(class_weight='balanced', max_iter=5000)",
        "total_rows": int(len(training_df)),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "intent_count": int(y.nunique()),
        "intents": labels,
        "metrics": {
            "accuracy": round(float(accuracy), 4),
            "balanced_accuracy": round(float(balanced_accuracy), 4),
            "macro_f1": round(float(macro_f1), 4),
            "weighted_f1": round(float(weighted_f1), 4),
        },
        "per_class_metrics": per_class_rows,
        "important_note": "The original dataset is multi-label. This classifier uses priority rules to convert multi-label disaster categories into one chatbot routing intent.",
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    mapping_payload = {
        "mapping_type": "priority-based multi-label to single chatbot intent mapping",
        "intent_rules": INTENT_RULES,
        "fallback_intent": "general_aid_request",
    }
    MAPPING_PATH.write_text(json.dumps(mapping_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Step 2 training complete.")
    print(f"Rows: {len(training_df):,}")
    print(f"Intents: {y.nunique()}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")
    print(f"Saved model: {MODEL_PATH}")


if __name__ == "__main__":
    main()
