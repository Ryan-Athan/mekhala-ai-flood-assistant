# Step 2 Model Training Report — Flood/Disaster Intent Classifier

## Objective

Train a dataset-based intent classifier for the **AI Flood Assistant** using the cleaned Kaggle Disaster Response Messages dataset from Step 1.

The classifier detects the user's flood/disaster topic so the chatbot can later return an answer from a flood-safety knowledge base.

## Input Dataset

```text
data/processed/clean_flood_disaster_chatbot_messages.csv
```

This file was produced in Step 1 after cleaning, merging, parsing labels, removing duplicates, and selecting flood/disaster-chatbot-relevant rows.

## Why an Intent Mapping Was Needed

The original Disaster Response dataset is **multi-label**. A single message can have many labels, such as:

```text
related;request;aid_related;water;shelter;direct_report
```

A chatbot response engine usually needs one routing intent. Therefore, Step 2 creates a derived `primary_intent` using priority-based rules. Human-need categories such as rescue, medical, water, food, and shelter are prioritized before general weather/hazard labels because they are more useful for chatbot response routing.

## Intent Mapping

| Chatbot Intent | Dataset Labels Used | Meaning |
|---|---|---|
| search_and_rescue | search_and_rescue, missing_people | Search, rescue, missing people, trapped people, and urgent rescue support. |
| medical_help | medical_help, medical_products, hospitals, death | Medical help, medicine, hospital access, injury, death, and health-related needs. |
| water_supply | water | Requests or reports about clean water, drinking water, and sanitation needs. |
| food_supply | food | Food shortage, food aid, and basic nutrition support messages. |
| shelter_evacuation | shelter, refugees | Shelter, temporary housing, displacement, evacuation, and refugee support. |
| road_transport | transport | Transport disruption, road access, blocked roads, vehicles, and route safety. |
| infrastructure_damage | buildings, electricity, infrastructure_related, other_infrastructure | Damage to buildings, drainage, bridges, electricity, and infrastructure systems. |
| security_services | security, military, aid_centers, shops, tools | Security, military, aid centers, shops, tools, and public service coordination. |
| flood_event | floods | Flood-specific messages, flood impact, river overflow, and water inundation reports. |
| storm_weather | storm | Storm, hurricane, cyclone, and severe weather event messages. |
| weather_warning | weather_related, other_weather, cold, fire, earthquake | General weather hazard, earthquake, cold, fire, or other weather-related alerts. |
| general_aid_request | request, aid_related, other_aid, direct_report, related | General help requests, aid-related reports, and direct disaster reports. |

## Training Data Output

```text
data/processed/flood_intent_training_data.csv
```

Rows used: **15,854**

## Intent Distribution

| Intent | Message Count | Percentage |
|---|---:|---:|
| medical_help | 3,331 | 21.01% |
| general_aid_request | 2,644 | 16.68% |
| weather_warning | 1,670 | 10.53% |
| food_supply | 1,576 | 9.94% |
| shelter_evacuation | 1,327 | 8.37% |
| water_supply | 1,008 | 6.36% |
| infrastructure_damage | 974 | 6.14% |
| storm_weather | 917 | 5.78% |
| search_and_rescue | 910 | 5.74% |
| security_services | 551 | 3.48% |
| flood_event | 537 | 3.39% |
| road_transport | 409 | 2.58% |

## Model

```text
TF-IDF + LinearSVC intent classifier
```

Vectorization:

```text
TfidfVectorizer with 1-2 word ngrams, max_features=30000, sublinear_tf=True
```

Classifier:

```text
LinearSVC(class_weight='balanced', max_iter=5000)
```

## Train/Test Split

```text
Train rows: 12,683
Test rows: 3,171
Test size: 20%
Stratified split: Yes
Random state: 42
```

## Evaluation Metrics

| Metric | Score |
|---|---:|
| Accuracy | 0.5661 |
| Balanced Accuracy | 0.5582 |
| Macro F1 | 0.5384 |
| Weighted F1 | 0.5621 |

## Per-Class Metrics

| Intent | Precision | Recall | F1 Score | Support |
|---|---:|---:|---:|---:|
| flood_event | 0.4186 | 0.5047 | 0.4576 | 107 |
| food_supply | 0.7195 | 0.7492 | 0.7341 | 315 |
| general_aid_request | 0.5453 | 0.5009 | 0.5222 | 529 |
| infrastructure_damage | 0.3394 | 0.2872 | 0.3111 | 195 |
| medical_help | 0.6692 | 0.5315 | 0.5925 | 666 |
| road_transport | 0.5222 | 0.5732 | 0.5465 | 82 |
| search_and_rescue | 0.4400 | 0.3022 | 0.3583 | 182 |
| security_services | 0.5000 | 0.5727 | 0.5339 | 110 |
| shelter_evacuation | 0.5162 | 0.5977 | 0.5540 | 266 |
| storm_weather | 0.5078 | 0.7104 | 0.5923 | 183 |
| water_supply | 0.5188 | 0.6139 | 0.5624 | 202 |
| weather_warning | 0.6462 | 0.7545 | 0.6961 | 334 |

## Generated Files

```text
models/flood_disaster_intent_classifier.pkl
models/flood_disaster_intent_metadata.json
models/intent_mapping.json
reports/02_CLASSIFICATION_REPORT.txt
reports/02_TRAINING_METRICS.json
reports/02_CONFUSION_MATRIX.csv
reports/02_CONFUSION_MATRIX.png
reports/02_SAMPLE_PREDICTIONS.csv
reports/02_TOP_FEATURES.csv
```

## Interpretation

This model is usable for first-stage chatbot routing. It is trained on real disaster-response data, but it is not yet a full ChatGPT-style generative model. The next steps will improve the user-facing answers.

## Limitation

- The dataset is not a Q&A conversation dataset.
- The model predicts intent only; it does not write the final answer.
- Some classes are harder because similar disaster messages may share many labels.
- Natural answers will be handled in later steps:

```text
Step 3: Flood-safety knowledge base
Step 4: Translation layer
Step 5: Optional LLM/RAG natural answer generation
```
