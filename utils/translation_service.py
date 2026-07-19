from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional
import json
import re


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_LANGUAGE_PATH = PROJECT_ROOT / "models" / "supported_languages.json"


@dataclass(frozen=True)
class TranslationResult:
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    source_language_name: str
    target_language_name: str
    translated: bool
    engine: str
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_text": self.original_text,
            "translated_text": self.translated_text,
            "source_language": self.source_language,
            "target_language": self.target_language,
            "source_language_name": self.source_language_name,
            "target_language_name": self.target_language_name,
            "translated": self.translated,
            "engine": self.engine,
            "error": self.error,
        }


@lru_cache(maxsize=1)
def load_supported_languages() -> dict[str, dict[str, str]]:
    if SUPPORTED_LANGUAGE_PATH.exists():
        return json.loads(SUPPORTED_LANGUAGE_PATH.read_text(encoding="utf-8"))
    return {
        "en": {"name": "English", "translator_code": "en"},
        "my": {"name": "Burmese", "translator_code": "my"},
    }


def _normalize_lang_code(code: str | None) -> str:
    if not code:
        return "en"
    code = str(code).strip()
    if code in {"zh", "zh-cn", "zh_CN", "zh-CN"}:
        return "zh-CN"
    if code in {"burmese", "mm", "mya", "myanmar"}:
        return "my"
    if code in {"iw"}:
        return "he"
    return code.split("_")[0].lower()


def _contains_range(text: str, start: int, end: int) -> bool:
    return any(start <= ord(ch) <= end for ch in text)


def _script_detect(text: str) -> str | None:
    """Fast Unicode-script detection for languages langdetect often struggles with."""
    if not text.strip():
        return "en"
    if _contains_range(text, 0x1000, 0x109F):
        return "my"
    if _contains_range(text, 0x0E00, 0x0E7F):
        return "th"
    if _contains_range(text, 0x0600, 0x06FF):
        return "ar"
    if _contains_range(text, 0x0900, 0x097F):
        return "hi"
    if _contains_range(text, 0x0980, 0x09FF):
        return "bn"
    if _contains_range(text, 0x3040, 0x30FF):
        return "ja"
    if _contains_range(text, 0xAC00, 0xD7AF):
        return "ko"
    if _contains_range(text, 0x4E00, 0x9FFF):
        return "zh-CN"
    return None


def detect_language(text: str) -> str:
    """Detect user language. Uses script rules first, then langdetect if installed."""
    text = text or ""
    script_lang = _script_detect(text)
    if script_lang:
        return script_lang

    try:
        from langdetect import detect  # type: ignore
        detected = _normalize_lang_code(detect(text))
        supported = load_supported_languages()
        return detected if detected in supported else "en"
    except Exception:
        # Safe fallback for English/Latin text when langdetect is not installed.
        return "en"


def get_language_name(code: str) -> str:
    supported = load_supported_languages()
    code = _normalize_lang_code(code)
    return supported.get(code, supported.get("en", {})).get("name", code)


def get_translator_code(code: str) -> str:
    supported = load_supported_languages()
    code = _normalize_lang_code(code)
    return supported.get(code, {}).get("translator_code", code)


def is_supported_language(code: str) -> bool:
    return _normalize_lang_code(code) in load_supported_languages()


def _clean_translation_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


def translate_text(text: str, target_language: str = "en", source_language: str | None = None) -> TranslationResult:
    """
    Translate text using deep-translator GoogleTranslator when available.

    Notes:
    - Requires internet connection for real translation.
    - If the library/internet is unavailable, it returns the original text safely.
    - This avoids crashing the Streamlit app during demonstrations.
    """
    text = text or ""
    source_language = _normalize_lang_code(source_language or detect_language(text))
    target_language = _normalize_lang_code(target_language)

    if not text.strip():
        return TranslationResult(text, text, source_language, target_language, get_language_name(source_language), get_language_name(target_language), False, "none")

    if source_language == target_language:
        return TranslationResult(text, text, source_language, target_language, get_language_name(source_language), get_language_name(target_language), False, "none")

    try:
        from deep_translator import GoogleTranslator  # type: ignore
        translated = GoogleTranslator(
            source=get_translator_code(source_language),
            target=get_translator_code(target_language),
        ).translate(text)
        translated = _clean_translation_text(translated)
        if not translated:
            raise RuntimeError("empty translation result")
        return TranslationResult(text, translated, source_language, target_language, get_language_name(source_language), get_language_name(target_language), True, "deep_translator_google")
    except Exception as error:
        return TranslationResult(text, text, source_language, target_language, get_language_name(source_language), get_language_name(target_language), False, "fallback_original", str(error))


def translate_user_message_to_english(user_message: str) -> dict[str, Any]:
    """Prepare any-language user text for the English dataset-trained classifier."""
    result = translate_text(user_message, target_language="en")
    return result.to_dict()


def translate_answer_from_english(answer_en: str, target_language: str) -> dict[str, Any]:
    """Translate English answer back to the user's language."""
    result = translate_text(answer_en, target_language=target_language, source_language="en")
    return result.to_dict()


def format_translation_note(language_code: str, engine: str, translated: bool) -> str:
    if language_code == "en":
        return ""
    lang_name = get_language_name(language_code)
    if translated:
        return f"\n\n_Translated to {lang_name} using {engine}._"
    return f"\n\n_Note: {lang_name} was detected, but online translation was unavailable, so the safest available answer is shown._"


if __name__ == "__main__":
    examples = [
        "What should I do during a flood?",
        "ရေကြီးရင် ဘာလုပ်ရမလဲ",
        "¿Qué debo hacer durante una inundación?",
        "Que dois-je faire pendant une inondation?",
        "น้ำท่วมควรทำอย่างไร",
        "洪水时我应该怎么办？",
    ]
    for example in examples:
        result = translate_user_message_to_english(example)
        print("INPUT:", example)
        print("DETECTED:", result["source_language"], result["source_language_name"])
        print("ENGLISH:", result["translated_text"])
        print("ENGINE:", result["engine"], "ERROR:", result.get("error"))
        print("-" * 60)
