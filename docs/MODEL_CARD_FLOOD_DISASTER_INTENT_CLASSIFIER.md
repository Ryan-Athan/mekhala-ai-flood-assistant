# Model Card — Flood Disaster Intent Classifier

## Model Name

`flood_disaster_intent_classifier.pkl`

## Project

FloodMind / AI Flood Assistant

## Model Type

TF-IDF + LinearSVC intent classifier

## Intended Use

This model predicts the user's disaster/flood-related intent from a short message or question. It is used as the routing model for the AI Flood Assistant.

## Input

Plain text user message.

Example:

```text
We need clean water after the flood.
```

## Output

One of 12 intent labels:

```text
flood_event, food_supply, general_aid_request, infrastructure_damage, medical_help, road_transport, search_and_rescue, security_services, shelter_evacuation, storm_weather, water_supply, weather_warning
```

## Training Dataset

Kaggle Disaster Response Messages dataset after Step 1 cleaning.

Training rows: 12,683  
Testing rows: 3,171  
Total rows: 15,854

## Metrics

| Metric | Score |
|---|---:|
| Accuracy | 0.5661 |
| Balanced Accuracy | 0.5582 |
| Macro F1 | 0.5384 |
| Weighted F1 | 0.5621 |

## Limitations

- The dataset is disaster-message based, not a full Q&A chatbot dataset.
- The model predicts intent only; it does not generate full answers.
- Multilingual support is not included in Step 2. Translation is Step 4.
- ChatGPT-like answer generation requires Step 5 LLM/RAG.

## Safety Notes

The chatbot should provide general flood safety guidance only. It should not replace official emergency instructions, local authorities, or rescue services.
