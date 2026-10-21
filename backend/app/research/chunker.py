from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path

PAGE_MARKER_RE = re.compile(r"<!--\s*page:\s*(\d+)\s*-->", flags=re.IGNORECASE)
WORD_RE = re.compile(r"\S+")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s*", flags=re.MULTILINE)


@dataclass(frozen=True)
class DocumentPage:
    page: int
    text: str


@dataclass(frozen=True)
class ResearchChunk:
    chunk_id: str
    doc_id: str
    title: str
    page: int
    chunk_index: int
    text: str
    source_id: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ResearchDocument:
    doc_id: str
    title: str
    pages: list[DocumentPage]
    path: str


def clean_markdown(text: str) -> str:
    text = HEADING_RE.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def split_pages(text: str) -> list[DocumentPage]:
    markers = list(PAGE_MARKER_RE.finditer(text))
    if not markers:
        cleaned = clean_markdown(text)
        return [DocumentPage(page=1, text=cleaned)] if cleaned else []
    pages: list[DocumentPage] = []
    first = clean_markdown(text[: markers[0].start()])
    start_index = 0
    if first and int(markers[0].group(1)) == 1:
        end = markers[1].start() if len(markers) > 1 else len(text)
        content = clean_markdown(text[markers[0].end() : end])
        pages.append(DocumentPage(page=1, text=clean_markdown(f"{first}\n{content}")))
        start_index = 1
    elif first:
        pages.append(DocumentPage(page=1, text=first))
    for index in range(start_index, len(markers)):
        marker = markers[index]
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        content = clean_markdown(text[marker.end() : end])
        if content:
            pages.append(DocumentPage(page=int(marker.group(1)), text=content))
    return pages


def title_from_text(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            candidate = stripped.lstrip("#").strip()
            if candidate:
                return candidate
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped[:200]
    return fallback


def read_text_document(path: Path) -> ResearchDocument:
    text = path.read_text(encoding="utf-8")
    title = title_from_text(text, path.stem.replace("_", " ").title())
    return ResearchDocument(
        doc_id=path.stem,
        title=title,
        pages=split_pages(text),
        path=str(path),
    )


def read_pdf_document(path: Path) -> ResearchDocument:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = clean_markdown(page.extract_text() or "")
        if text:
            pages.append(DocumentPage(page=index, text=text))
    metadata = reader.metadata or {}
    title = str(metadata.get("/Title") or path.stem.replace("_", " ").title())
    return ResearchDocument(doc_id=path.stem, title=title, pages=pages, path=str(path))


def read_documents(directory: Path) -> list[ResearchDocument]:
    documents: list[ResearchDocument] = []
    for path in sorted(directory.iterdir()):
        suffix = path.suffix.casefold()
        if suffix == ".pdf":
            documents.append(read_pdf_document(path))
        elif suffix in {".md", ".txt"}:
            documents.append(read_text_document(path))
    return [document for document in documents if document.pages]


def chunk_pages(
    pages: list[DocumentPage],
    doc_id: str,
    title: str,
    chunk_size: int = 350,
    overlap: int = 60,
) -> list[ResearchChunk]:
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("invalid chunk_size/overlap")
    chunks: list[ResearchChunk] = []
    for page in pages:
        words = WORD_RE.findall(page.text)
        if not words:
            continue
        step = chunk_size - overlap
        for chunk_index, start in enumerate(range(0, len(words), step)):
            window = words[start : start + chunk_size]
            if not window:
                continue
            chunks.append(
                ResearchChunk(
                    chunk_id=f"bank:{doc_id}:p{page.page}:c{chunk_index}",
                    doc_id=doc_id,
                    title=title,
                    page=page.page,
                    chunk_index=chunk_index,
                    text=" ".join(window),
                    source_id=f"bank:{doc_id}:p{page.page}",
                )
            )
            if start + chunk_size >= len(words):
                break
    return chunks


def build_chunks(documents: list[ResearchDocument]) -> list[ResearchChunk]:
    chunks: list[ResearchChunk] = []
    for document in documents:
        chunks.extend(
            chunk_pages(
                document.pages,
                doc_id=document.doc_id,
                title=document.title,
            )
        )
    return chunks
