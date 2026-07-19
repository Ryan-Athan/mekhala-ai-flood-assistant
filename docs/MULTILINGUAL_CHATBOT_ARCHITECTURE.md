# Multilingual Chatbot Architecture

## Why translation is needed

The Kaggle Disaster Response Messages dataset is primarily English. Training separate models for 15 languages would require large labeled datasets in each language. Instead, the system uses one English classifier and a translation layer.

## Pipeline

1. **Language Detection**
   - Unicode script rules detect Burmese, Thai, Arabic, Hindi, Bengali, Chinese, Japanese, and Korean.
   - `langdetect` handles Latin-script languages such as English, French, Spanish, German, Indonesian, Malay, and Vietnamese.

2. **Input Translation**
   - Non-English queries are translated to English.
   - The English message is passed to the Step 2 classifier.

3. **Intent Classification**
   - Step 2 model predicts a flood/disaster intent.

4. **Knowledge Base Response**
   - Step 3 knowledge base returns flood-specific safety guidance.

5. **Output Localization**
   - English answer is translated back to the user's language.
   - For Burmese, curated Burmese knowledge-base answers are preferred.

## Limitations

- Translation accuracy depends on the translation backend.
- Internet is required for `deep-translator` Google translation.
- Offline fallback keeps the app stable but cannot guarantee 15-language translation quality.
