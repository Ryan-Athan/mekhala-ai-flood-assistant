from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KB_PATH = PROJECT_ROOT / "models" / "flood_safety_knowledge_base.json"
MAPPING_PATH = PROJECT_ROOT / "models" / "intent_to_kb_mapping.json"


def _safe_language(language: str | None) -> str:
    if not language:
        return "en"
    language = language.lower().strip()
    if language in {"my", "burmese", "mm", "mya"}:
        return "my"
    return "en"


@lru_cache(maxsize=1)
def load_knowledge_base() -> dict[str, Any]:
    if not KB_PATH.exists():
        raise FileNotFoundError(f"Knowledge base not found: {KB_PATH}")
    return json.loads(KB_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_intent_mapping() -> dict[str, str]:
    if not MAPPING_PATH.exists():
        return {}
    return json.loads(MAPPING_PATH.read_text(encoding="utf-8"))


def get_kb_intent(predicted_intent: str | None) -> str:
    if not predicted_intent:
        return "fallback"
    mapping = load_intent_mapping()
    return mapping.get(predicted_intent, predicted_intent if predicted_intent in load_knowledge_base().get("intents", {}) else "fallback")


def get_knowledge_entry(predicted_intent: str | None) -> dict[str, Any]:
    kb = load_knowledge_base()
    kb_intent = get_kb_intent(predicted_intent)
    return kb.get("intents", {}).get(kb_intent, kb.get("intents", {}).get("fallback", {}))


def format_flood_answer(
    predicted_intent: str | None,
    language: str = "en",
    include_steps: bool = True,
    include_avoid: bool = True,
    include_sources: bool = False,
) -> dict[str, Any]:
    """
    Returns a response object for AI Flood Assistant.

    predicted_intent comes from Step 2 classifier, keyword routing, or future RAG/LLM router.
    language currently supports 'en' and 'my'. Other languages should be handled by the
    Step 4 translation layer.
    """
    lang = _safe_language(language)
    kb = load_knowledge_base()
    entry = get_knowledge_entry(predicted_intent)

    answer = entry.get("answer_templates", {}).get(lang) or entry.get("answer_templates", {}).get("en", "")
    steps = entry.get("action_steps", {}).get(lang) or entry.get("action_steps", {}).get("en", [])
    avoid = entry.get("avoid", {}).get(lang) or entry.get("avoid", {}).get("en", [])

    parts = [answer.strip()]

    if include_steps and steps:
        heading = "Recommended actions:" if lang == "en" else "လုပ်သင့်သည့်အချက်များ:"
        parts.append(heading)
        parts.extend([f"{index + 1}. {step}" for index, step in enumerate(steps)])

    if include_avoid and avoid:
        heading = "Avoid:" if lang == "en" else "ရှောင်ရန်:"
        parts.append(heading)
        parts.extend([f"- {item}" for item in avoid])

    source_details = []
    if include_sources:
        for source_id in entry.get("source_ids", []):
            source = kb.get("source_catalog", {}).get(source_id)
            if source:
                source_details.append({"source_id": source_id, **source})

    return {
        "intent": get_kb_intent(predicted_intent),
        "display_name": entry.get("display_name", "Fallback"),
        "urgency": entry.get("urgency", "low"),
        "language": lang,
        "response": "\n".join(parts).strip(),
        "sources": source_details,
    }


if __name__ == "__main__":
    samples = ["flood_event", "road_transport", "flood_causes", "after_flood_cleanup", "unknown"]
    for sample in samples:
        result = format_flood_answer(sample, language="en", include_sources=True)
        print("=" * 80)
        print(result["intent"], result["display_name"], result["urgency"])
        print(result["response"][:500])
