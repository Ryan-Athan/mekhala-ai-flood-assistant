from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.rag_llm_chatbot_engine import get_flood_assistant_response


TEST_QUESTIONS = [
    "What should I do during a flood?",
    "What are the main reasons for flooding?",
    "Can I drive through flood water?",
    "What should I pack in my emergency kit?",
    "ရေကြီးရင် ဘာလုပ်ရမလဲ",
    "ကားနဲ့ ရေမြုပ်လမ်း ဖြတ်လို့ရလား",
]


def main() -> None:
    for question in TEST_QUESTIONS:
        result = get_flood_assistant_response(question)
        print("=" * 80)
        print("QUESTION:", question)
        print("LANGUAGE:", result.get("language"))
        print("INTENT:", result.get("intent"))
        print("SOURCE:", result.get("source"))
        print("ANSWER:")
        print(result.get("response"))
        print()


if __name__ == "__main__":
    main()
