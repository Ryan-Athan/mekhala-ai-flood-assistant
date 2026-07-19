# FloodMind Project Log

## Step 1 — Dataset Cleaning

Dataset: Kaggle Disaster Response Messages

Actions completed:

- Loaded `disaster_messages.csv`
- Loaded `disaster_categories.csv`
- Merged messages and categories
- Cleaned category labels
- Removed duplicates and empty messages
- Created flood/disaster chatbot subset

Main outputs:

- `data/processed/clean_disaster_messages_full.csv`
- `data/processed/clean_flood_disaster_chatbot_messages.csv`

## Step 2 — Intent Classifier Training

Goal: Train a flood/disaster intent classifier from the cleaned dataset.

Model:

- TF-IDF vectorizer
- LinearSVC classifier

Intent classes:

- flood_event
- storm_weather
- weather_warning
- water_supply
- food_supply
- shelter_evacuation
- medical_help
- search_and_rescue
- road_transport
- infrastructure_damage
- security_services
- general_aid_request

Main outputs:

- `models/flood_disaster_intent_classifier.pkl`
- `models/flood_disaster_intent_metadata.json`
- `models/intent_mapping.json`

## Step 3 — Flood-Safety Knowledge Base

Goal: Build a structured answer knowledge base for AI Flood Assistant.

Actions completed:

- Created official-source-informed flood safety responses
- Added English answers
- Added Burmese localized answers
- Added action steps and avoid warnings
- Mapped Step 2 predicted labels to knowledge-base intents
- Added source catalog
- Added validation script and report

Main outputs:

- `models/flood_safety_knowledge_base.json`
- `models/intent_to_kb_mapping.json`
- `models/disaster_answer_kb.json`
- `utils/flood_knowledge_base.py`
- `reports/03_KB_VALIDATION_REPORT.md`

Validation status: PASS.

## Next Step

Step 4: Add translation layer for Burmese and other languages.
