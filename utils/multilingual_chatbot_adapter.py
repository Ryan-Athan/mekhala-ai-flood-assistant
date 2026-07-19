from __future__ import annotations

from typing import Any

from utils.translation_service import (
    detect_language,
    translate_answer_from_english,
    translate_user_message_to_english,
    format_translation_note,
)


def prepare_multilingual_query(user_message: str) -> dict[str, Any]:
    """
    Convert a user's message into English for the dataset-trained classifier.

    Use this before Step 2 classifier prediction:
        prepared = prepare_multilingual_query(user_message)
        english_message = prepared["english_text"]
    """
    translation = translate_user_message_to_english(user_message)
    return {
        "original_text": user_message,
        "english_text": translation["translated_text"],
        "language": translation["source_language"],
        "language_name": translation["source_language_name"],
        "translation_engine": translation["engine"],
        "translated_to_english": translation["translated"],
        "translation_error": translation.get("error"),
    }


def localize_chatbot_answer(answer_en: str, language: str) -> dict[str, Any]:
    """
    Convert an English flood-safety answer to the user's language.

    For Burmese, Step 3 knowledge base already contains curated Burmese answers.
    Prefer those curated answers when available. Use this function when only English text is available.
    """
    translated = translate_answer_from_english(answer_en, language)
    note = format_translation_note(language, translated["engine"], translated["translated"])
    return {
        "answer": translated["translated_text"] + note,
        "language": translated["target_language"],
        "language_name": translated["target_language_name"],
        "translation_engine": translated["engine"],
        "translated_from_english": translated["translated"],
        "translation_error": translated.get("error"),
    }


def demo_pipeline(user_message: str, english_answer: str) -> dict[str, Any]:
    prepared = prepare_multilingual_query(user_message)
    localized = localize_chatbot_answer(english_answer, prepared["language"])
    return {
        "prepared_query": prepared,
        "localized_answer": localized,
    }


if __name__ == "__main__":
    answer = "Move to higher ground immediately. Avoid walking or driving through floodwater. Follow local evacuation instructions."
    tests = [
        "What should I do during a flood?",
        "ရေကြီးရင် ဘာလုပ်ရမလဲ",
        "¿Qué debo hacer durante una inundación?",
        "Que dois-je faire pendant une inondation?",
    ]
    for text in tests:
        print(demo_pipeline(text, answer))
        print("-" * 80)
