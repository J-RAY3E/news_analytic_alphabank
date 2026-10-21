from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from rank_bm25 import BM25Okapi

from app.research.chunker import ResearchChunk

TOKEN_RE = re.compile(r"[a-zа-яё0-9]+", flags=re.IGNORECASE)

STOPWORDS = {
    "и",
    "в",
    "во",
    "на",
    "с",
    "со",
    "по",
    "для",
    "из",
    "от",
    "до",
    "о",
    "об",
    "при",
    "как",
    "что",
    "это",
    "не",
    "но",
    "а",
    "или",
    "за",
    "к",
    "у",
    "же",
    "бы",
    "ли",
    "the",
    "of",
    "to",
}


def tokenize(text: str) -> list[str]:
    return [
        token.casefold()
        for token in TOKEN_RE.findall(text)
        if len(token) > 2 and token.casefold() not in STOPWORDS
    ]


@dataclass(frozen=True)
class SearchResult:
    chunk: ResearchChunk
    score: float

    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk.chunk_id,
            "doc_id": self.chunk.doc_id,
            "title": self.chunk.title,
            "page": self.chunk.page,
            "source_id": self.chunk.source_id,
            "text": self.chunk.text,
            "score": round(self.score, 6),
        }


class ResearchIndex:
    def __init__(self, chunks: list[ResearchChunk]) -> None:
        self.chunks = chunks
        self._corpus = [tokenize(chunk.text) for chunk in chunks]
        self._bm25 = BM25Okapi(self._corpus) if any(self._corpus) else None

    @classmethod
    def from_jsonl(cls, path: str | Path) -> ResearchIndex:
        chunks: list[ResearchChunk] = []
        with Path(path).open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    chunks.append(ResearchChunk(**json.loads(line)))
        return cls(chunks)

    def to_jsonl(self, path: str | Path) -> None:
        with Path(path).open("w", encoding="utf-8") as handle:
            for chunk in self.chunks:
                handle.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + "\n")

    def search(self, query: str, k: int = 5, min_score: float = 0.01) -> list[SearchResult]:
        if self._bm25 is None or k <= 0:
            return []
        tokens = tokenize(query)
        if not tokens:
            return []
        scores = self._bm25.get_scores(tokens)
        ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
        results = [
            SearchResult(chunk=self.chunks[index], score=float(score))
            for index, score in ranked[:k]
            if float(score) > min_score
        ]
        return results

    def get_card(self, doc_id: str) -> list[ResearchChunk]:
        return [chunk for chunk in self.chunks if chunk.doc_id == doc_id]

    def documents(self) -> list[dict[str, str | int]]:
        seen: dict[str, dict[str, str | int]] = {}
        for chunk in self.chunks:
            if chunk.doc_id not in seen:
                seen[chunk.doc_id] = {
                    "doc_id": chunk.doc_id,
                    "title": chunk.title,
                    "pages": chunk.page,
                    "chunks": 0,
                }
            seen[chunk.doc_id]["chunks"] = int(seen[chunk.doc_id]["chunks"]) + 1
            seen[chunk.doc_id]["pages"] = max(int(seen[chunk.doc_id]["pages"]), chunk.page)
        return list(seen.values())


@lru_cache
def load_research_index(path: str | Path) -> ResearchIndex:
    return ResearchIndex.from_jsonl(path)
