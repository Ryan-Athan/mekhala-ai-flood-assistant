# Step 3 — Flood-Safety Knowledge Base Report

## Objective

Step 3 builds the response knowledge base for the AI Flood Assistant. Step 2 trained a disaster/flood intent classifier, but the classifier only predicts the topic. It does not generate complete safety answers. This step creates a structured knowledge base that maps predicted intents to practical flood-safety guidance.

## Output Files

- `models/flood_safety_knowledge_base.json` — main structured flood safety KB
- `models/intent_to_kb_mapping.json` — maps Step 2 classifier labels to KB entries
- `models/disaster_answer_kb.json` — simplified compatibility KB for chatbot engines
- `data/knowledge_base/flood_safety_sources.csv` — source catalog
- `data/knowledge_base/knowledge_base_intent_summary.csv` — intent summary table
- `utils/flood_knowledge_base.py` — Python helper for retrieving formatted answers
- `scripts/03_build_flood_safety_kb.py` — rebuild script
- `scripts/03_validate_flood_safety_kb.py` — validation script
- `reports/03_KB_VALIDATION_REPORT.md` and `.json` — validation report

## Knowledge Base Design

Each intent entry contains:

- display name
- urgency level
- short summary
- keywords
- English answer
- Burmese answer
- action steps in English and Burmese
- avoid/do-not-do safety warnings
- official source IDs

This structure lets the chatbot provide more useful answers than a raw classifier response.

## Intent Coverage

The KB contains 17 response intents:

1. flood_event
2. flood_causes
3. weather_warning
4. storm_weather
5. water_supply
6. food_supply
7. shelter_evacuation
8. medical_help
9. search_and_rescue
10. road_transport
11. infrastructure_damage
12. electricity_safety
13. after_flood_cleanup
14. protect_home
15. security_services
16. general_aid_request
17. fallback

## Mapping from Step 2

The Step 2 classifier predicts one of 12 dataset-derived labels. This step maps those labels to knowledge-base responses.

Examples:

| Step 2 Predicted Intent | Step 3 KB Intent |
|---|---|
| flood_event | flood_event |
| storm_weather | storm_weather |
| weather_warning | weather_warning |
| water_supply | water_supply |
| food_supply | food_supply |
| shelter_evacuation | shelter_evacuation |
| medical_help | medical_help |
| search_and_rescue | search_and_rescue |
| road_transport | road_transport |
| infrastructure_damage | infrastructure_damage |
| security_services | security_services |
| general_aid_request | general_aid_request |

Extra direct intents were also added for better chatbot behavior, such as flood_causes, electricity_safety, after_flood_cleanup, and protect_home.

## Sources Used

The knowledge base is based on official flood safety and public health guidance from:

- Ready.gov / FEMA
- NOAA National Weather Service
- CDC
- EPA

The response text is paraphrased and adapted for the FloodMind project.

## Validation

The validation script checks:

- required intents exist
- English and Burmese answers are present
- source IDs are valid
- mapping entries point to valid KB intents
- each intent has actionable guidance

Validation result: PASS.

## How This Supports the Chatbot

The chatbot pipeline after Step 3 becomes:

```text
User message
↓
Step 2 classifier predicts intent
↓
Step 3 maps intent to knowledge base entry
↓
Chatbot returns practical flood safety answer
```

## Limitation

This is still not a full ChatGPT-style language model. It is a knowledge-based response system connected to a trained disaster-intent classifier. Natural answer generation and multilingual translation will be added in later steps.

## Recommended Report Wording

> The AI Flood Assistant uses a trained disaster-intent classifier to identify the user's flood-related topic. The predicted intent is then mapped to a structured flood-safety knowledge base containing official-source-informed safety guidance, emergency actions, and Burmese localized responses.
