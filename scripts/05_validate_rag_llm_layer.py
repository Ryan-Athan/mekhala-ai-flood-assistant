from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.flood_rag_retriever import load_default_retriever
from utils.rag_llm_chatbot_engine import get_flood_assistant_response

REPORT_PATH = PROJECT_ROOT / "reports" / "05_RAG_LLM_VALIDATION_REPORT.json"

TEST_CASES = [
    {"question": "What causes floods?", "expected_intent": "flood_causes"},
    {"question": "What should I do during a flood?", "expected_intent": "during_flood"},
    {"question": "What should I pack in emergency kit?", "expected_intent": "emergency_kit"},
    {"question": "Can I drive through floodwater?", "expected_intent": "road_transport"},
    {"question": "ရေကြီးရင် ဘာလုပ်ရမလဲ", "expected_intent": "during_flood"},
]


def main() -> None:
    retriever = load_default_retriever()
    results = []
    passed = 0

    for case in TEST_CASES:
        result = get_flood_assistant_response(case["question"])
        ok = bool(result.get("response")) and len(result.get("retrieved_documents", [])) > 0
        if ok:
            passed += 1
        results.append(
            {
                "question": case["question"],
                "expected_intent": case["expected_intent"],
                "predicted_intent": result.get("intent"),
                "source": result.get("source"),
                "language": result.get("language"),
                "has_response": bool(result.get("response")),
                "retrieved_count": len(result.get("retrieved_documents", [])),
                "passed": ok,
            }
        )

    report = {
        "step": "05_optional_rag_llm_layer",
        "status": "PASS" if passed == len(TEST_CASES) else "CHECK",
        "document_count": len(retriever.documents),
        "test_cases": len(TEST_CASES),
        "passed": passed,
        "results": results,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
