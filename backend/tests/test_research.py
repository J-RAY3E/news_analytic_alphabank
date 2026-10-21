from pathlib import Path

import pytest

from app.research.chunker import (
    build_chunks,
    chunk_pages,
    read_documents,
    split_pages,
)
from app.research.index import ResearchIndex, tokenize

ROOT = Path(__file__).resolve().parents[2]
RESEARCH_DIR = ROOT / "data" / "research"
CHUNKS_PATH = ROOT / "data" / "index" / "research_chunks.jsonl"


def test_split_pages_merges_header_with_page_one():
    text = "Заголовок\n\n<!-- page: 1 -->\nПервый текст.\n<!-- page: 2 -->\nВторой текст."
    pages = split_pages(text)
    assert [page.page for page in pages] == [1, 2]
    assert "Заголовок" in pages[0].text
    assert "Первый текст" in pages[0].text
    assert pages[1].text == "Второй текст."


def test_chunk_pages_source_ids_and_size():
    from app.research.chunker import DocumentPage

    pages = [
        DocumentPage(page=1, text=" ".join(f"слово{index}" for index in range(400))),
        DocumentPage(page=2, text="короткий текст"),
    ]
    chunks = chunk_pages(pages, doc_id="test_doc", title="Test", chunk_size=350, overlap=50)
    assert chunks[0].source_id == "bank:test_doc:p1"
    assert chunks[0].chunk_id == "bank:test_doc:p1:c0"
    assert len(chunks[0].text.split()) == 350
    assert chunks[1].source_id == "bank:test_doc:p1"
    assert len(chunks[1].text.split()) == 100
    assert chunks[-1].source_id == "bank:test_doc:p2"
    assert all(len(chunk.text.split()) <= 350 for chunk in chunks)
    assert len({chunk.chunk_id for chunk in chunks}) == len(chunks)


def test_build_research_index_and_search():
    documents = read_documents(RESEARCH_DIR)
    assert len(documents) == 9
    chunks = build_chunks(documents)
    assert len(chunks) == 18
    index = ResearchIndex(chunks)

    results = index.search("ключевая ставка инфляция", k=3)
    assert results
    assert all(result.chunk.source_id.startswith("bank:") for result in results)
    assert results[0].chunk.doc_id in {"key_rate", "tactical_q3_2026", "inflation"}
    assert index.search("квантовые компьютеры") == []
    assert index.search("") == []
    card = index.get_card("key_rate")
    assert len(card) == 2
    assert {chunk.page for chunk in card} == {1, 2}


def test_persisted_index_contract():
    index = ResearchIndex.from_jsonl(CHUNKS_PATH)
    assert len(index.chunks) == 18
    assert len({chunk.chunk_id for chunk in index.chunks}) == 18
    titles = {document["title"] for document in index.documents()}
    assert "Ключевая ставка и кредитный рынок" in titles
    assert tokenize("Ключевая ставка и инфляция") == ["ключевая", "ставка", "инфляция"]
