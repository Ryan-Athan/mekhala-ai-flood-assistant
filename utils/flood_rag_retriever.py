from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCS_CSV = PROJECT_ROOT / "data" / "rag" / "flood_knowledge_documents.csv"
DEFAULT_INDEX_PATH = PROJECT_ROOT / "models" / "flood_rag_retriever.pkl"
DEFAULT_DOCS_JSON = PROJECT_ROOT / "models" / "flood_rag_documents.json"


@dataclass
class RetrievedDocument:
    doc_id: str
    intent: str
    title: str
    content_en: str
    content_my: str
    source_name: str
    source_url: str
    score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "intent": self.intent,
            "title": self.title,
            "content_en": self.content_en,
            "content_my": self.content_my,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "score": self.score,
        }


class FloodRAGRetriever:
    """Small, local TF-IDF retriever for flood safety documents.

    This is intentionally lightweight so it works inside Streamlit without a vector DB.
    It retrieves relevant flood safety passages that can be sent to an LLM or to the
    fallback response composer.
    """

    def __init__(self, documents: list[dict[str, Any]], vectorizer: TfidfVectorizer | None = None, matrix: Any | None = None):
        self.documents = documents
        self.vectorizer = vectorizer or TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            strip_accents="unicode",
        )
        self.matrix = matrix

    @staticmethod
    def _document_text(document: dict[str, Any]) -> str:
        return " ".join(
            [
                str(document.get("intent", "")),
                str(document.get("title", "")),
                str(document.get("content_en", "")),
            ]
        )

    @classmethod
    def from_csv(cls, csv_path: str | Path = DEFAULT_DOCS_CSV) -> "FloodRAGRetriever":
        csv_path = Path(csv_path)
        frame = pd.read_csv(csv_path).fillna("")
        documents = frame.to_dict(orient="records")
        retriever = cls(documents=documents)
        retriever.fit()
        return retriever

    def fit(self) -> None:
        corpus = [self._document_text(document) for document in self.documents]
        self.matrix = self.vectorizer.fit_transform(corpus)

    def save(self, index_path: str | Path = DEFAULT_INDEX_PATH, docs_json_path: str | Path = DEFAULT_DOCS_JSON) -> None:
        index_path = Path(index_path)
        docs_json_path = Path(docs_json_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        docs_json_path.parent.mkdir(parents=True, exist_ok=True)

        joblib.dump(
            {
                "vectorizer": self.vectorizer,
                "matrix": self.matrix,
            },
            index_path,
        )
        docs_json_path.write_text(json.dumps(self.documents, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, index_path: str | Path = DEFAULT_INDEX_PATH, docs_json_path: str | Path = DEFAULT_DOCS_JSON) -> "FloodRAGRetriever":
        index_path = Path(index_path)
        docs_json_path = Path(docs_json_path)

        if not index_path.exists() or not docs_json_path.exists():
            retriever = cls.from_csv(DEFAULT_DOCS_CSV)
            retriever.save(index_path, docs_json_path)
            return retriever

        payload = joblib.load(index_path)
        documents = json.loads(docs_json_path.read_text(encoding="utf-8"))
        return cls(
            documents=documents,
            vectorizer=payload["vectorizer"],
            matrix=payload["matrix"],
        )

    def search(self, query: str, intent: str | None = None, top_k: int = 4) -> list[RetrievedDocument]:
        if not query.strip():
            query = intent or "flood safety"

        if self.matrix is None:
            self.fit()

        query_parts = [query]
        if intent:
            query_parts.extend([intent, intent.replace("_", " ")])

        query_vector = self.vectorizer.transform([" ".join(query_parts)])
        scores = cosine_similarity(query_vector, self.matrix).ravel()

        candidates: list[tuple[int, float]] = []
        for index, score in enumerate(scores):
            document = self.documents[index]
            adjusted_score = float(score)
            if intent and document.get("intent") == intent:
                adjusted_score += 0.22
            candidates.append((index, adjusted_score))

        candidates.sort(key=lambda item: item[1], reverse=True)
        top_candidates = candidates[: max(1, top_k)]

        results: list[RetrievedDocument] = []
        for index, score in top_candidates:
            document = self.documents[index]
            results.append(
                RetrievedDocument(
                    doc_id=str(document.get("id", "")),
                    intent=str(document.get("intent", "")),
                    title=str(document.get("title", "")),
                    content_en=str(document.get("content_en", "")),
                    content_my=str(document.get("content_my", "")),
                    source_name=str(document.get("source_name", "")),
                    source_url=str(document.get("source_url", "")),
                    score=float(score),
                )
            )

        return results


def build_and_save_default_index() -> FloodRAGRetriever:
    retriever = FloodRAGRetriever.from_csv(DEFAULT_DOCS_CSV)
    retriever.save(DEFAULT_INDEX_PATH, DEFAULT_DOCS_JSON)
    return retriever


def load_default_retriever() -> FloodRAGRetriever:
    return FloodRAGRetriever.load(DEFAULT_INDEX_PATH, DEFAULT_DOCS_JSON)


if __name__ == "__main__":
    retriever = build_and_save_default_index()
    for result in retriever.search("what should I do during a flood", top_k=3):
        print(result.score, result.intent, result.title)
