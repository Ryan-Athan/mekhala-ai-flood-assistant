# Step 4 Translation Layer Report

## Goal

Add a multilingual layer for the AI Flood Assistant so users can ask flood-related questions in multiple languages while the Step 2 classifier remains English-based.

## Completed Work

1. Created `models/supported_languages.json` with 15 supported languages.
2. Created `utils/translation_service.py` for language detection and translation.
3. Created `utils/multilingual_chatbot_adapter.py` for chatbot integration.
4. Created multilingual test questions.
5. Created validation and test scripts.
6. Added documentation and integration notes.

## Supported Languages

- English
- Burmese / Myanmar
- Thai
- Chinese Simplified
- Hindi
- Bengali
- Indonesian
- Vietnamese
- Japanese
- Korean
- French
- Spanish
- Arabic
- German
- Malay

## Architecture

```text
User message in any supported language
↓
Detect language
↓
Translate message to English
↓
Step 2 flood/disaster intent classifier
↓
Step 3 flood-safety knowledge base
↓
Translate answer back to user's language
```

## Important Accuracy Note

The Disaster Response Messages dataset is English-based. Therefore, high multilingual accuracy should be achieved through translation, not by training 15 separate classifiers.

For offline demonstrations, the translation service fails safely and returns the original text instead of crashing. For best multilingual quality, internet access is needed because `deep-translator` uses an online translation backend.

## Recommended Report Wording

> The multilingual AI Flood Assistant uses language detection and translation to convert user queries into English before intent classification. A TF-IDF + LinearSVC disaster-intent classifier processes the English query, then the selected flood-safety knowledge base response is translated back to the user's language. Burmese is additionally supported with curated local safety responses.
