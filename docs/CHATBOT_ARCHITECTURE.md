# AI Flood Assistant Architecture — After Step 2

## Current Architecture

```text
User message
↓
Text cleaning / normalization
↓
TF-IDF vectorizer
↓
Flood/disaster intent classifier
↓
Predicted intent
```

Step 2 only completes the **intent classifier**.

## Current Classifier

```text
TF-IDF + LinearSVC
```

## Predicted Intents

```text
- flood_event
- food_supply
- general_aid_request
- infrastructure_damage
- medical_help
- road_transport
- search_and_rescue
- security_services
- shelter_evacuation
- storm_weather
- water_supply
- weather_warning
```

## Future Architecture

```text
User asks in any language
↓
Language detection
↓
Translate to English
↓
Intent classifier predicts flood/disaster topic
↓
Retrieve flood-safety knowledge
↓
Generate natural answer with templates or LLM/RAG
↓
Translate answer back to user language
```

## Next Step

Step 3 will build the flood-safety knowledge base. The predicted intent from this model will map to a safe answer.
