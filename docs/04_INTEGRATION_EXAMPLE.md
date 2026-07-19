# Step 4 integration example

Use this pattern inside your final `utils/chatbot_engine.py` after Step 5 integration:

```python
from utils.multilingual_chatbot_adapter import prepare_multilingual_query, localize_chatbot_answer

prepared = prepare_multilingual_query(user_message)
english_message = prepared["english_text"]
user_language = prepared["language"]

# Step 2 model predicts intent from english_message
predicted_intent = predict_intent(english_message)

# Step 3 knowledge base returns answer_en, and answer_my if Burmese exists
answer_en = get_answer_from_kb(predicted_intent, language="en")

if user_language == "my":
    # Prefer the curated Burmese answer from Step 3 if available.
    answer = get_answer_from_kb(predicted_intent, language="my")
else:
    localized = localize_chatbot_answer(answer_en, user_language)
    answer = localized["answer"]
```

This lets one English-trained classifier support many user languages.
