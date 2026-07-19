from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "models" / "disaster_chatbot_model.pkl"
KB_PATH = PROJECT_ROOT / "models" / "disaster_answer_kb.json"
METADATA_PATH = PROJECT_ROOT / "models" / "disaster_chatbot_metadata.json"

MYANMAR_RE = re.compile(r"[\u1000-\u109F]")
_LOAD_ERROR: str | None = None


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _is_burmese(text: str) -> bool:
    return bool(MYANMAR_RE.search(text or ""))


@lru_cache(maxsize=1)
def _load_model() -> Any | None:
    global _LOAD_ERROR

    if not MODEL_PATH.exists():
        _LOAD_ERROR = "Model file is missing. Run: python train_disaster_chatbot_model.py"
        return None

    try:
        _LOAD_ERROR = None
        return joblib.load(MODEL_PATH)
    except Exception as exc:
        _LOAD_ERROR = (
            "The saved chatbot model is not compatible with your current Python/scikit-learn environment. "
            "Delete models/disaster_chatbot_model.pkl and run: python train_disaster_chatbot_model.py. "
            f"Original error: {type(exc).__name__}: {exc}"
        )
        return None


@lru_cache(maxsize=1)
def _load_kb() -> dict[str, Any]:
    if KB_PATH.exists():
        return json.loads(KB_PATH.read_text(encoding="utf-8"))

    return {
        "english": {
            "fallback": "I can help with flood safety, evacuation, emergency kits, and flood warning signs."
        },
        "burmese": {
            "fallback": "ရေကြီးခြင်းဆိုင်ရာ ဘေးကင်းရေးမေးခွန်းတွေကို မေးနိုင်ပါတယ်။"
        },
        "label_to_answer": {},
    }


@lru_cache(maxsize=1)
def _load_metadata() -> dict[str, Any]:
    if METADATA_PATH.exists():
        try:
            return json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {"trained_labels": []}
    return {"trained_labels": []}


def _english_rule_intent(text: str) -> str | None:
    cleaned = _normalize(text)

    if _contains_any(cleaned, ["cause", "causes", "reason", "reasons", "why flood", "why do floods", "main reason"]):
        return "flood_causes"
    if _contains_any(cleaned, ["warning sign", "warning signs", "early warning", "flood alert", "how know flood", "signs of flood"]):
        return "warning_signs"
    if _contains_any(cleaned, ["emergency kit", "pack", "prepare", "supplies", "what should i prepare", "items do i need"]):
        return "emergency_kit"
    if _contains_any(cleaned, ["need water", "need food", "need shelter", "relief", "supplies after", "food and shelter", "water and food"]):
        return "relief_items"
    if _contains_any(cleaned, ["evacuate", "evacuation", "leave home", "move out", "safe place"]):
        return "evacuation"
    if _contains_any(cleaned, ["drive", "driving", "car", "vehicle", "road", "flooded road"]):
        return "driving_safety"
    if _contains_any(cleaned, ["electric", "electricity", "power line", "wire", "switch", "appliance"]):
        return "electricity_safety"
    if _contains_any(cleaned, ["protect my home", "protect home", "house", "sandbag", "before flood"]):
        return "protect_home"
    if _contains_any(cleaned, ["after flood", "after the flood", "cleanup", "clean up", "return home"]):
        return "after_flood"
    if _contains_any(cleaned, ["during flood", "flood is happening", "what should i do", "stay safe", "safety during flood"]):
        return "during_flood"

    return None


def _burmese_rule_intent(text: str) -> str:
    if _contains_any(text, ["ဘာကြောင့်", "အကြောင်း", "အကြောင်းရင်း", "ဖြစ်ရ", "ဘာလို့"]):
        return "flood_causes"
    if _contains_any(text, ["သတိပေး", "လက္ခဏာ", "ဘယ်လိုသိ", "ရေတက်"]):
        return "warning_signs"
    if _contains_any(text, ["အရေးပေါ်အိတ်", "အိတ်", "ပြင်ဆင်", "ထည့်", "ယူရမလဲ"]):
        return "emergency_kit"
    if _contains_any(text, ["ရွှေ့", "ရွှေ့ပြောင်း", "ထွက်", "ဘေးကင်းရာ", "စုရပ်"]):
        return "evacuation"
    if _contains_any(text, ["ကား", "မောင်း", "လမ်း", "ဖြတ်"]):
        return "driving_safety"
    if _contains_any(text, ["မီး", "လျှပ်စစ်", "ကြိုး", "မီးခလုတ်"]):
        return "electricity_safety"
    if _contains_any(text, ["အိမ်", "ကာကွယ်", "သဲအိတ်"]):
        return "protect_home"
    if _contains_any(text, ["ရေကျ", "ပြီးနောက်", "သန့်ရှင်း", "ပြန်ဝင်"]):
        return "after_flood"
    if _contains_any(text, ["ဘာလုပ်", "ရေကြီးရင်", "ရေကြီးနေ", "ဘေးကင်း"]):
        return "during_flood"
    return "fallback"


def _predict_dataset_labels(user_message: str) -> tuple[list[tuple[str, float]], str | None, str | None]:
    model = _load_model()
    metadata = _load_metadata()
    labels = metadata.get("trained_labels", [])

    if model is None or not labels:
        return [], None, _LOAD_ERROR

    try:
        probabilities = model.predict_proba([user_message])[0]
    except Exception:
        try:
            decision = model.decision_function([user_message])[0]
            probabilities = 1 / (1 + np.exp(-np.asarray(decision)))
        except Exception as exc:
            return [], None, f"Prediction failed: {type(exc).__name__}: {exc}"

    ranked = sorted(
        zip(labels, [float(value) for value in probabilities]),
        key=lambda item: item[1],
        reverse=True,
    )

    kb = _load_kb()
    label_to_answer = kb.get("label_to_answer", {})

    for label, score in ranked:
        if label in label_to_answer and score >= 0.30:
            return ranked[:5], label_to_answer[label], None

    if ranked and ranked[0][1] >= 0.22:
        top_label = ranked[0][0]
        return ranked[:5], label_to_answer.get(top_label, "fallback"), None

    return ranked[:5], None, None


def get_flood_assistant_response(
    user_message: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    del history
    kb = _load_kb()

    if not user_message or not user_message.strip():
        return {
            "response": kb["english"].get("fallback", "Please ask a flood-safety question."),
            "language": "en",
            "source": "empty_input",
            "intent": "fallback",
            "confidence": 0.0,
        }

    if _is_burmese(user_message):
        intent = _burmese_rule_intent(user_message)
        response = kb.get("burmese", {}).get(intent) or kb.get("burmese", {}).get("fallback")
        return {
            "response": response,
            "language": "my",
            "source": "burmese_knowledge_base",
            "intent": intent,
            "confidence": 1.0,
        }

    rule_intent = _english_rule_intent(user_message)
    if rule_intent:
        response = kb.get("english", {}).get(rule_intent) or kb.get("english", {}).get("fallback")
        return {
            "response": response,
            "language": "en",
            "source": "english_rule_plus_knowledge_base",
            "intent": rule_intent,
            "confidence": 1.0,
        }

    ranked_labels, mapped_intent, load_error = _predict_dataset_labels(user_message)

    if mapped_intent:
        response = kb.get("english", {}).get(mapped_intent) or kb.get("english", {}).get("fallback")
        confidence = ranked_labels[0][1] if ranked_labels else 0.0
        return {
            "response": response,
            "language": "en",
            "source": "kaggle_disaster_response_model",
            "intent": mapped_intent,
            "confidence": round(float(confidence), 4),
            "top_labels": ranked_labels,
        }

    response = kb.get("english", {}).get("fallback")
    result = {
        "response": response,
        "language": "en",
        "source": "fallback",
        "intent": "fallback",
        "confidence": 0.0,
        "top_labels": ranked_labels,
    }

    # Keep the app from crashing, but expose the model problem for debugging if needed.
    if load_error:
        result["debug_error"] = load_error

    return result


if __name__ == "__main__":
    test_questions = [
        "What are the main reasons for flood?",
        "I need food and shelter after heavy rain.",
        "Can I drive through flood water?",
        "ရေကြီးရင် ဘာလုပ်ရမလဲ",
        "ရေကြီးတာ ဘာကြောင့်ဖြစ်တာလဲ",
    ]

    for question in test_questions:
        print("Q:", question)
        result = get_flood_assistant_response(question)
        print(result["response"])
        if result.get("debug_error"):
            print("DEBUG:", result["debug_error"])
        print("-" * 80)
