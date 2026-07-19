from __future__ import annotations

from pathlib import Path
import sys
import joblib

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "models" / "flood_disaster_intent_classifier.pkl"

SAMPLE_QUESTIONS = [
    "What should I do during a flood?",
    "The road is blocked by flood water, can I drive?",
    "We need clean drinking water after the flood.",
    "People are trapped and need rescue.",
    "Our house is damaged and we need shelter.",
    "There is a storm warning tonight.",
]


def main() -> None:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}. Run scripts/02_train_flood_disaster_intent_classifier.py first.")

    model = joblib.load(MODEL_PATH)

    questions = sys.argv[1:] if len(sys.argv) > 1 else SAMPLE_QUESTIONS

    for question in questions:
        predicted_intent = model.predict([question])[0]
        print(f"Question: {question}")
        print(f"Predicted intent: {predicted_intent}")
        print("-" * 70)


if __name__ == "__main__":
    main()
