from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

try:
    from utils.flood_rag_retriever import load_default_retriever
    from utils.llm_client import OptionalLLMClient
except Exception:  # pragma: no cover
    from flood_rag_retriever import load_default_retriever
    from llm_client import OptionalLLMClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]


INTENT_KEYWORDS = {
    "flood_causes": ["cause", "reason", "why", "ဖြစ်", "အကြောင်း", "ဘာကြောင့်"],
    "during_flood": ["during", "happening", "now", "what should i do", "ရေကြီးရင်", "လုပ်ရမလဲ"],
    "weather_warning": ["warning", "sign", "alert", "watch", "သတိ", "လက္ခဏာ"],
    "emergency_kit": ["kit", "pack", "prepare", "items", "အိတ်", "ပြင်", "ဘာတွေထည့်"],
    "shelter_evacuation": ["evacuate", "leave", "shelter", "safe place", "ရွှေ့", "ထွက်", "ခိုလှုံ"],
    "road_transport": ["drive", "road", "car", "bridge", "ကား", "လမ်း", "တံတား"],
    "electricity_safety": ["electric", "power", "wire", "မီး", "လျှပ်စစ်"],
    "water_supply": ["water", "food", "drink", "ရေ", "အစား"],
    "medical_help": ["medical", "injury", "first aid", "doctor", "ဆေး", "ဒဏ်ရာ"],
    "after_flood_cleanup": ["after", "cleanup", "mold", "return home", "ပြီးနောက်", "သန့်ရှင်း", "မှို"],
    "protect_home": ["protect home", "house", "sandbag", "drain", "အိမ်", "ကာကွယ်", "သဲအိတ်"],
    "search_and_rescue": ["rescue", "trapped", "save", "ကယ်", "ပိတ်မိ"],
}


def _contains_burmese(text: str) -> bool:
    return bool(re.search(r"[\u1000-\u109F]", text))


def _simple_language(text: str) -> str:
    """Detect the user's language.

    The old version only detected Burmese and treated Japanese, Spanish,
    French, Chinese, etc. as English. That is why non-English questions
    received English answers.
    """
    try:
        from utils.translation_service import detect_language

        return detect_language(text) or "en"
    except Exception:
        if _contains_burmese(text):
            return "my"
        return "en"


def _translate_to_english_if_available(text: str, language: str) -> str:
    """Translate user input to English for the classifier/RAG retriever."""
    if language == "en":
        return text
    try:
        from utils.translation_service import translate_text

        result = translate_text(text, target_language="en", source_language=language)
        return result.translated_text or text
    except Exception:
        return text


def _translate_from_english_if_available(text: str, language: str) -> str:
    """Translate final English answer back to the user's language."""
    if language == "en":
        return text
    try:
        from utils.translation_service import translate_text

        result = translate_text(text, target_language=language, source_language="en")
        return result.translated_text or text
    except Exception:
        return text


def detect_intent(question_en: str, original_question: str = "") -> str:
    text = f"{question_en} {original_question}".lower()
    best_intent = "fallback"
    best_score = 0

    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword.lower() in text)
        if score > best_score:
            best_score = score
            best_intent = intent

    return best_intent


def _build_system_prompt(language: str) -> str:
    return (
        "You are FloodMind AI, a flood safety assistant for an early warning system. "
        "Answer only using the provided flood safety context. "
        "Be clear, practical, calm, and emergency-focused. "
        "Do not invent official warnings, phone numbers, locations, or weather facts. "
        "If the situation may be dangerous, recommend following local authorities and emergency services. "
        f"Respond in language code: {language}."
    )


def _build_user_prompt(question: str, intent: str, documents: list[dict[str, Any]], language: str) -> str:
    context_blocks = []
    for index, document in enumerate(documents, start=1):
        context_blocks.append(
            f"[Context {index}]\n"
            f"Intent: {document['intent']}\n"
            f"Title: {document['title']}\n"
            f"Content: {document['content_en']}\n"
            f"Source: {document['source_name']}"
        )

    context = "\n\n".join(context_blocks)
    return (
        f"User question: {question}\n"
        f"Detected intent: {intent}\n"
        f"Target language: {language}\n\n"
        f"Flood safety context:\n{context}\n\n"
        "Write a helpful answer in 4 to 7 short bullet points or compact paragraphs. "
        "Keep it specific to floods. Include what to do and what to avoid."
    )


def _fallback_compose(question: str, language: str, intent: str, documents: list[dict[str, Any]]) -> str:
    if not documents:
        if language == "my":
            return "မေးခွန်းကို ပိုရှင်းရှင်းပြောပေးပါ။ ရေကြီးမှုလုံခြုံရေး၊ ရွှေ့ပြောင်းခြင်း၊ အရေးပေါ်အိတ်၊ လမ်းအန္တရာယ်၊ လျှပ်စစ်အန္တရာယ် စတဲ့အကြောင်းတွေကို ကူညီဖြေနိုင်ပါတယ်။"
        return "Please ask your flood-safety question in more detail. I can help with flood safety, evacuation, emergency kits, road safety, electricity safety, and cleanup."

    primary = documents[0]
    if language == "my" and primary.get("content_my"):
        base = primary["content_my"]
        extra = "\n\nအရေးပေါ်အခြေအနေဖြစ်ပါက ဒေသခံအာဏာပိုင်များနှင့် အရေးပေါ်ဝန်ဆောင်မှုများ၏ ညွှန်ကြားချက်ကို လိုက်နာပါ။"
        return base + extra

    base = primary["content_en"]
    extra_points = []
    for document in documents[1:]:
        if document.get("intent") == "fallback":
            continue
        content = document.get("content_en", "")
        if content and content not in base and content not in extra_points:
            extra_points.append(content)
        if len(extra_points) >= 2:
            break

    response = base
    if extra_points:
        response += "\n\nRelated guidance:\n"
        for point in extra_points:
            response += f"- {point}\n"
    response += "\nIf this is an emergency, follow local authority instructions and contact emergency services."
    return response.strip()


def get_flood_assistant_response(user_message: str, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    history = history or []
    language = _simple_language(user_message)
    question_en = _translate_to_english_if_available(user_message, language)
    intent = detect_intent(question_en, user_message)

    retriever = load_default_retriever()
    retrieved = retriever.search(question_en, intent=intent, top_k=4)
    documents = [item.to_dict() for item in retrieved]

    llm = OptionalLLMClient()
    system_prompt = _build_system_prompt(language)
    prompt = _build_user_prompt(question_en, intent, documents, language)
    llm_result = llm.generate(prompt=prompt, system_prompt=system_prompt)

    if llm_result.ok and llm_result.text:
        answer = llm_result.text.strip()
        source = f"rag_llm:{llm_result.provider}"
    else:
        answer = _fallback_compose(user_message, language, intent, documents)
        source = "rag_template_fallback"

    # Final localization step.
    # LLM/RAG fallback normally generates English, except curated Burmese answers.
    # Translate the final answer back to the original user language.
    if language != "en":
        if language == "my":
            if not _contains_burmese(answer):
                answer = _translate_from_english_if_available(answer, language)
        else:
            answer = _translate_from_english_if_available(answer, language)

    return {
        "response": answer,
        "language": language,
        "intent": intent,
        "source": source,
        "retrieved_documents": documents,
    }


if __name__ == "__main__":
    samples = [
        "What are the main causes of floods?",
        "Can I drive through flood water?",
        "ရေကြီးရင် ဘာလုပ်ရမလဲ",
    ]
    for sample in samples:
        print("\nQ:", sample)
        result = get_flood_assistant_response(sample)
        print("Intent:", result["intent"], "Source:", result["source"])
        print(result["response"][:700])
