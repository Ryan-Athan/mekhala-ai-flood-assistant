from __future__ import annotations

from pathlib import Path
import csv
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.translation_service import translate_user_message_to_english, translate_answer_from_english

TEST_FILE = PROJECT_ROOT / "data" / "multilingual_tests" / "multilingual_flood_questions.csv"
REPORT_FILE = PROJECT_ROOT / "reports" / "04_TRANSLATION_TEST_REPORT.csv"


def main() -> None:
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    rows = list(csv.DictReader(TEST_FILE.open("r", encoding="utf-8")))
    output_rows = []

    print(f"Testing {len(rows)} multilingual flood questions...")

    for row in rows:
        question = row["question"]
        expected_lang = row["language"]
        to_english = translate_user_message_to_english(question)
        back = translate_answer_from_english(
            "Move to higher ground and avoid floodwater.",
            target_language=to_english["source_language"],
        )

        output = {
            "expected_language": expected_lang,
            "detected_language": to_english["source_language"],
            "language_name": to_english["source_language_name"],
            "question": question,
            "translated_to_english": to_english["translated_text"],
            "translation_engine": to_english["engine"],
            "answer_back_to_language": back["translated_text"],
            "answer_translation_engine": back["engine"],
            "error": to_english.get("error") or back.get("error") or "",
        }
        output_rows.append(output)
        print(f"[{expected_lang} -> {output['detected_language']}] {question} => {to_english['translated_text']}")

    with REPORT_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"\nSaved report: {REPORT_FILE}")


if __name__ == "__main__":
    main()
