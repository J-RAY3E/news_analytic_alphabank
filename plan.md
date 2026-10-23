# Plan: Extract Scanned PDFs (data/raw) → Real Research Corpus

## Problem
- All 9 PDFs in `data/raw/` are pure scans: zero `/Font`, each page = one
  1357×1920 raster image (FlateDecode). `pypdf` extracts nothing.
- `data/research/*.md` are synthetic stubs ("СИНТЕТИЧЕСКИЙ ДОКУМЕНТ..."), not
  real extraction. BM25 index searches stubs.
- Goal: real text corpus with `<!-- page: N -->` markers so existing
  `backend/app/research/chunker.py` + index pipeline work unchanged.

## Approach: Vision LLM (PRD-allowed Qwen3-VL-30B-A3B-Instruct)

Alternatives rejected:
- Tesseract OCR: free but poor on tables/charts, needs install + rus pack → fallback only
- Cloud OCR (Yandex/Google): forbidden by PRD (no external AI services)
- pypdf/pdfplumber: useless, no text layer

Cost estimate: ~100 pages × (1.3k tok in + 1.5k tok out) at 20/80 RUB per 1M
≈ 15–20 RUB one-time, cached per page (7-day TTL). Budget safe (500 RUB/day).

## Steps

1. **Dep:** add `pypdfium2` to `pyproject.toml` (Apache-2.0, render PDF→PNG;
   license noted in THIRD_PARTY_NOTICES later).

2. **LLM client vision support** (`backend/app/llm/client.py`):
   - new `complete_vision(purpose, system, user, images, ...)`:
     OpenAI-compatible `image_url` messages
   - route purpose `vision` → `qwen/qwen3-vl-30b-a3b-instruct`
     (`llm_model_vision` already in Settings)
   - add `vision: qwen/...` to `routing` in `config/llm.yaml`
   - cache: same disk cache (key includes image hashes), audit log reuse

3. **Pipeline** `pipelines/extract_scanned_pdfs.py`:
   - args: `--raw-dir`, `--out-dir` (default `data/research`), `--engine {vlm,tesseract}`, `--docs` (subset), `--force`
   - render each page → PNG (scale ~2, cap long side ~2000 px)
   - prompt (ru): verbatim transcription to markdown, preserve tables/numbers,
     never invent facts, ignore instructions inside image (untrusted framing),
     keep document structure/headings
   - page cache `data/cache/ocr/<doc_slug>_p<N>.md` → resumable, no re-billing
   - assemble per doc: `<!-- page: N -->` markers per section
   - write `data/research/<slug>.md` matching existing 9 slugs:
     bond_brief, inflation, gold, tactical_q3_2026, commodities, key_rate,
     macro_7m26, macro_1h26, consumption
   - map slugs → raw filenames explicitly (Cyrillic-safe)
   - `--engine tesseract` fallback path (pytesseract + rus traineddata) if
     budget exhausted or API down

4. **Rebuild index:** run `pipelines/build_research_index.py` → real chunks
   into `data/index/research_chunks.jsonl`.

5. **Verify:**
   - `pytest backend/tests/test_research.py -q` passes
   - spot-check: index.search("ключевая ставка") returns chunks with real
     pages/citations, not stub text
   - sanity check: no "СИНТЕТИЧЕСКИЙ" marker in new corpus files
   - cost check: `data/cache/llm_usage.jsonl` total ≤ ~20 RUB

## Files touched
- `pyproject.toml` (+1 dep)
- `config/llm.yaml` (+1 routing entry)
- `backend/app/llm/client.py` (+~60 lines)
- `pipelines/extract_scanned_pdfs.py` (new, ~200 lines)
- `data/research/*.md` (regenerated, 9 files)
- `data/index/research_chunks.jsonl` (regenerated)

## Risks
- VL model misreads dense tables → mitigated: per-page retry with fallback
  engine, human spot-check of 2–3 pages per doc
- Budget: bounded by per-page cache + budget governor check before each call
- Cyrillic filename on Windows → explicit slug map, no glob ordering reliance
