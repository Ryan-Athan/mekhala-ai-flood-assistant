# Step 5 Integration Guide

## 1. Copy files

Copy these folders/files into your project:

```text
models/flood_rag_retriever.pkl
models/flood_rag_documents.json
utils/flood_rag_retriever.py
utils/llm_client.py
utils/rag_llm_chatbot_engine.py
data/rag/flood_knowledge_documents.csv
scripts/05_build_rag_index.py
scripts/05_test_rag_llm_chatbot.py
scripts/05_validate_rag_llm_layer.py
```

## 2. Use the new engine in `tabs/ai_assistant.py`

Find the old import:

```python
from utils.chatbot_engine import get_flood_assistant_response
```

or:

```python
from utils.mock_ai import get_flood_assistant_response
```

Replace with:

```python
from utils.rag_llm_chatbot_engine import get_flood_assistant_response
```

The function name is the same, so the UI logic does not need to change.

## 3. Test locally

```powershell
python scripts/05_validate_rag_llm_layer.py
python scripts/05_test_rag_llm_chatbot.py
```

## 4. Optional LLM setup

Default mode uses local fallback:

```text
FLOODMIND_LLM_PROVIDER=none
```

To use an online or local LLM, copy `.env.example`, configure one provider, and load environment variables before running Streamlit.

## 5. Run app

```powershell
python -m streamlit run app.py --server.port 8501 --server.address localhost
```
