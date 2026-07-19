from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.flood_rag_retriever import build_and_save_default_index, DEFAULT_DOCS_CSV, DEFAULT_INDEX_PATH, DEFAULT_DOCS_JSON


def main() -> None:
    retriever = build_and_save_default_index()
    print("RAG index built successfully.")
    print(f"Source documents: {DEFAULT_DOCS_CSV}")
    print(f"Index file: {DEFAULT_INDEX_PATH}")
    print(f"Documents JSON: {DEFAULT_DOCS_JSON}")
    print(f"Document count: {len(retriever.documents)}")


if __name__ == "__main__":
    main()
