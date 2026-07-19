# RAG/LLM Architecture

```text
User question
↓
Language detection
↓
Translate to English when available
↓
Intent detection / classifier
↓
TF-IDF RAG retriever
↓
Top flood-safety context documents
↓
Optional LLM answer generation
↓
Fallback local RAG answer composer if LLM unavailable
↓
Translate/localize answer back to user language
```

## Why this is better than an intent-only chatbot

An intent-only chatbot predicts a label and returns a fixed answer. This can feel robotic.

A RAG chatbot retrieves relevant knowledge first, so it can combine several pieces of flood guidance and produce a more complete answer.

## Safety Design

The system prompt tells the LLM:

- answer only from provided flood-safety context
- do not invent official warnings, phone numbers, or weather data
- recommend following local authorities in dangerous situations
- stay flood-specific

## Offline Mode

If no LLM provider is enabled, the chatbot still works using local retrieval and template composition.

## Multilingual Mode

The package is designed to work with Step 4 translation utilities. It can answer Burmese using curated Burmese safety content. Other languages depend on the translation service.
