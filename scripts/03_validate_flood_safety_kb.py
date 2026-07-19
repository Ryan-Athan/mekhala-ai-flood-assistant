from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KB_PATH = PROJECT_ROOT / "models" / "flood_safety_knowledge_base.json"
MAPPING_PATH = PROJECT_ROOT / "models" / "intent_to_kb_mapping.json"


def main() -> None:
    kb = json.loads(KB_PATH.read_text(encoding="utf-8"))
    mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))

    intents = kb.get("intents", {})
    errors = []

    for step2_intent, kb_intent in mapping.items():
        if kb_intent not in intents:
            errors.append(f"Mapping error: {step2_intent} -> {kb_intent} not found in KB.")

    for intent, entry in intents.items():
        if not entry.get("answer_templates", {}).get("en"):
            errors.append(f"{intent}: missing English answer")
        if not entry.get("answer_templates", {}).get("my"):
            errors.append(f"{intent}: missing Burmese answer")
        if not entry.get("source_ids"):
            errors.append(f"{intent}: missing source_ids")

    if errors:
        print("Knowledge base validation FAILED")
        for error in errors:
            print("-", error)
        raise SystemExit(1)

    print("Knowledge base validation PASSED")
    print(f"Intent entries: {len(intents)}")
    print(f"Mappings: {len(mapping)}")
    print(f"Languages: {', '.join(kb.get('metadata', {}).get('languages_included', []))}")


if __name__ == "__main__":
    main()
