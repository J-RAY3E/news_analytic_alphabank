from __future__ import annotations

from app.agents.tools import build_retrieval_query
from app.contracts import NormalizedEvent
from app.core.errors import NotFound
from app.research.index import ResearchIndex


class A4Retriever:
    def __init__(self, index: ResearchIndex | None) -> None:
        self.index = index

    def search_event(self, event: NormalizedEvent, k: int = 4) -> list[dict]:
        return self.search(build_retrieval_query(event), k=k)

    def search(self, query: str, k: int = 4) -> list[dict]:
        if self.index is None:
            return []
        return [result.to_dict() for result in self.index.search(query, k=k)]

    def get_card(self, doc_id: str) -> list[dict]:
        if self.index is None:
            return []
        chunks = self.index.get_card(doc_id)
        if not chunks:
            raise NotFound(f"research document not found: {doc_id}")
        return [chunk.to_dict() for chunk in chunks]
