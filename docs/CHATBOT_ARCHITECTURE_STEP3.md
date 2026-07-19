# AI Flood Assistant Architecture After Step 3

## Current Pipeline

```text
User question
↓
Text preprocessing
↓
Step 2 intent classifier
↓
Predicted intent
↓
Step 3 flood-safety knowledge base
↓
English/Burmese answer
```

## Why This Is Needed

The Disaster Response Messages dataset is useful for recognizing disaster categories, but it is not a question-answer dataset. Therefore, the trained classifier needs a response layer. The knowledge base provides that response layer.

## Components

### Intent Classifier

- Learns from the cleaned disaster-response dataset.
- Predicts a topic/intent.

### Knowledge Base

- Stores safety responses.
- Provides step-by-step advice.
- Provides English and Burmese responses.
- Includes safety warnings.

### Future Translation Layer

Step 4 will add support for more languages by translating user input into English, running the classifier, and translating the answer back to the user's language.

### Future RAG/LLM Layer

Step 5 can add a retrieval-augmented generation layer so the chatbot answers more naturally like a real AI assistant.
