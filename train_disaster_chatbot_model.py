from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "disaster_response"
MODEL_DIR = PROJECT_ROOT / "models"

MESSAGES_FILE = DATA_DIR / "disaster_messages.csv"
CATEGORIES_FILE = DATA_DIR / "disaster_categories.csv"

MODEL_PATH = MODEL_DIR / "disaster_chatbot_model.pkl"
METADATA_PATH = MODEL_DIR / "disaster_chatbot_metadata.json"

SELECTED_LABELS = [
    "related",
    "request",
    "aid_related",
    "medical_help",
    "search_and_rescue",
    "water",
    "food",
    "shelter",
    "transport",
    "buildings",
    "electricity",
    "infrastructure_related",
    "weather_related",
    "floods",
    "storm",
    "fire",
    "earthquake",
    "direct_report",
]


def load_disaster_response_dataset() -> tuple[pd.Series, pd.DataFrame, list[str], int]:
    if not MESSAGES_FILE.exists() or not CATEGORIES_FILE.exists():
        raise FileNotFoundError(
            "Missing dataset files. Put disaster_messages.csv and disaster_categories.csv inside "
            "data/disaster_response/."
        )

    messages = pd.read_csv(MESSAGES_FILE)
    categories = pd.read_csv(CATEGORIES_FILE)

    df = messages.merge(categories, on="id", how="inner")
    df = df.drop_duplicates(subset=["id"]).reset_index(drop=True)

    split_categories = df["categories"].str.split(";", expand=True)
    parsed_categories: dict[str, pd.Series] = {}

    for column in split_categories.columns:
        parts = split_categories[column].str.rsplit("-", n=1)
        category_name = parts.str[0].iloc[0]
        values = parts.str[1].astype(int)

        # The original dataset sometimes has related-2. Treat it as related-1.
        if category_name == "related":
            values = values.replace(2, 1)

        parsed_categories[category_name] = values

    labels: list[str] = []
    for label in SELECTED_LABELS:
        if label not in parsed_categories:
            continue
        values = parsed_categories[label]
        if values.nunique() <= 1 or values.sum() == 0:
            continue
        df[label] = values
        labels.append(label)

    if not labels:
        raise ValueError("No usable labels found in disaster_categories.csv.")

    X = df["message"].fillna("").astype(str)
    y = df[labels].astype(int)
    return X, y, labels, len(df)


def build_model() -> Pipeline:
    # SGDClassifier with log_loss is fast for this multi-label text task.
    # The model is saved with YOUR local scikit-learn version, so it avoids pickle version errors.
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    stop_words="english",
                    ngram_range=(1, 2),
                    max_features=18000,
                    min_df=2,
                    sublinear_tf=True,
                    strip_accents="unicode",
                ),
            ),
            (
                "classifier",
                OneVsRestClassifier(
                    SGDClassifier(
                        loss="log_loss",
                        penalty="l2",
                        alpha=0.0001,
                        max_iter=1000,
                        tol=1e-3,
                        class_weight="balanced",
                        random_state=42,
                    ),
                    n_jobs=1,
                ),
            ),
        ]
    )


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    X, y, labels, num_messages = load_disaster_response_dataset()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = build_model()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    micro_f1 = f1_score(y_test, predictions, average="micro", zero_division=0)
    macro_f1 = f1_score(y_test, predictions, average="macro", zero_division=0)

    # Train final model on all available rows for app use.
    model.fit(X, y)
    joblib.dump(model, MODEL_PATH, compress=3)

    metadata = {
        "model_name": "FloodMind Disaster Response Chatbot Classifier",
        "dataset_source": "Kaggle Disaster Response Messages dataset",
        "dataset_files": [
            "data/disaster_response/disaster_messages.csv",
            "data/disaster_response/disaster_categories.csv",
        ],
        "num_messages": int(num_messages),
        "num_labels_trained": int(len(labels)),
        "trained_labels": labels,
        "algorithm": "TF-IDF vectorizer + One-vs-Rest SGD Logistic classifier",
        "input_column": "message",
        "metrics_holdout_20_percent": {
            "micro_f1": round(float(micro_f1), 4),
            "macro_f1": round(float(macro_f1), 4),
        },
        "note": "This pickle was generated locally. Re-run this script after changing scikit-learn versions.",
    }

    METADATA_PATH.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Training complete.")
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved metadata: {METADATA_PATH}")
    print(f"Micro F1: {micro_f1:.4f}")
    print(f"Macro F1: {macro_f1:.4f}")


if __name__ == "__main__":
    main()
