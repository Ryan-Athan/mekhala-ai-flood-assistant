from __future__ import annotations

from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.translation_service import load_supported_languages, detect_language

REPORT_FILE = PROJECT_ROOT / "reports" / "04_TRANSLATION_LAYER_VALIDATION.json"


def main() -> None:
    supported = load_supported_languages()
    errors = []

    if len(supported) < 15:
        errors.append(f"Expected at least 15 supported languages, got {len(supported)}")

    required = ["en", "my", "th", "zh-CN", "hi", "bn", "id", "vi", "ja", "ko", "fr", "es", "ar", "de", "ms"]
    for code in required:
        if code not in supported:
            errors.append(f"Missing language: {code}")

    detection_tests = {
        "ရေကြီးရင် ဘာလုပ်ရမလဲ": "my",
        "น้ำท่วมควรทำอย่างไร": "th",
        "洪水时我应该怎么办？": "zh-CN",
        "बाढ़ में क्या करना चाहिए": "hi",
        "বন্যার সময় কী করতে হবে": "bn",
        "ماذا أفعل أثناء الفيضان؟": "ar",
        "洪水の時はどうすればいいですか": "ja",
        "홍수 때 어떻게 해야 하나요": "ko",
    }
    detected = {}
    for text, expected in detection_tests.items():
        lang = detect_language(text)
        detected[text] = lang
        if lang != expected:
            errors.append(f"Detection mismatch: expected {expected}, got {lang} for {text}")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "supported_language_count": len(supported),
        "supported_languages": list(supported.keys()),
        "script_detection_results": detected,
        "errors": errors,
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
