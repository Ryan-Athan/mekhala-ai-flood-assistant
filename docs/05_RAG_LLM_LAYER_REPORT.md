# Step 5 Report — Optional RAG/LLM Layer for AI Flood Assistant

## Goal

The goal of Step 5 is to make the AI Flood Assistant feel more like a real AI chatbot while still staying safe, project-ready, and flood-specific.

The chatbot now uses a Retrieval-Augmented Generation style pipeline:

1. Detect user language.
2. Translate or normalize the question when possible.
3. Detect the flood/disaster intent.
4. Retrieve relevant flood-safety knowledge documents.
5. Generate a natural response using either:
   - optional LLM provider, or
   - local RAG template fallback when no LLM key is configured.
6. Return the answer in the user's language when possible.

## Why RAG is needed

The Disaster Response Messages dataset is useful for classifying disaster intent, but it is not a complete question-answer conversation dataset. RAG improves the chatbot by grounding responses in a curated flood-safety knowledge base before generating an answer.

## Files Created

- `data/rag/flood_knowledge_documents.csv`
- `models/flood_rag_retriever.pkl`
- `models/flood_rag_documents.json`
- `utils/flood_rag_retriever.py`
- `utils/llm_client.py`
- `utils/rag_llm_chatbot_engine.py`
- `scripts/05_build_rag_index.py`
- `scripts/05_test_rag_llm_chatbot.py`
- `scripts/05_validate_rag_llm_layer.py`
- `reports/05_RAG_LLM_VALIDATION_REPORT.json`

## Knowledge Documents

The RAG layer contains flood-safety documents for these topics:

- flood causes
- what to do during flood
- warning signs
- emergency kit
- evacuation
- road and driving safety
- electricity safety
- safe water and food
- medical help
- flood cleanup
- protecting home
- search and rescue
- infrastructure damage
- official/security services
- general aid request
- fallback answer

## Model / Retrieval Method

Retriever:

- TF-IDF Vectorizer
- Cosine similarity search
- Intent-aware score boosting

This is lightweight and does not require a vector database.

## Optional LLM Providers

The package supports these optional provider modes through environment variables:

- `none` — use local RAG template fallback
- `openai_compatible` — use an OpenAI-compatible chat endpoint
- `openrouter` — use OpenRouter
- `ollama` — use local Ollama

The app works without any LLM API key.

## Validation Result

Validation status: PASS

The validation script checks that the retriever loads, test questions return answers, Burmese input returns a Burmese answer, and retrieved documents are available.

## Report Wording

Use this sentence in the project report:

> The AI Flood Assistant uses Retrieval-Augmented Generation. A TF-IDF retriever searches a curated flood-safety knowledge base and passes the most relevant context to an optional LLM. When an LLM is not configured, the system falls back to a local RAG template response generator. This keeps the chatbot flood-specific, grounded, and safe.
