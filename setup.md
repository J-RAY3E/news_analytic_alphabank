# Alfa Radar — Setup

How to run the project locally (Docker is the primary path; no build step is
required because the data artifacts are committed).

## Prerequisites

- Git
- Docker Desktop / Docker Engine with **Compose v2**
- Optional, for local development without Docker: Python 3.11–3.14 and Node.js 20

## 1. Clone

```bash
git clone https://github.com/J-RAY3E/news_analytic_alphabank.git
cd news_analytic_alphabank
git checkout system-design
```

## 2. Run (Docker — recommended)

```bash
docker compose up --build
```

- Web app: <http://localhost:3000>
- API docs (OpenAPI): <http://localhost:8000/docs>
- Health: <http://localhost:8000/health>

`data/processed/*.parquet`, `data/index/*` and `data/research/*.md` are committed,
so the API starts with data — nothing to extract or chunk. Stop with
`docker compose down`.

## 3. LLM modes

- **Deterministic (default):** do **not** create `.env`. With no API key the
  service returns a complete six-block insight from the deterministic fallback —
  no network, no cost.
- **Live LLM:** `cp .env.example .env`, set `LLM_API_KEY`, then
  `docker compose up -d --build`. `.env` is gitignored.

Routing lives in `config/llm.yaml` (A2 extraction on Gemma 4, A6 interpretation
on DeepSeek-V4.1-Flash with automatic failover, scanned-PDF OCR on Qwen3-VL).
Daily budget: 500 ₽; results are cached under `data/cache/llm/`.

## 4. Sign in

Demo accounts are listed in the README ("Test accounts") table, e.g.
`ceo` / `ceo-radar-2026`. Sign-in is required (no guest).

## 5. Verify

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/feed?company_id=U_57706&role=CFO&limit=3"
curl http://localhost:8000/metrics
```

The feed and metrics endpoints should return JSON with items.

## 6. Local development (optional)

Backend:

```bash
uv sync
uv run uvicorn app.main:app --app-dir backend --reload --port 8000
uv run pytest -q
uv run python scripts/export_openapi.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
npm run lint
npx tsc --noEmit
npm run build
```

Set `NEXT_PUBLIC_USE_MOCKS=true` in `frontend/.env.local` to run the UI against
bundled mocks with no backend.

## 7. Rebuild data (only if needed)

```bash
uv run python pipelines/build_features.py         # companies + exposure graph
uv run python pipelines/build_research_index.py   # research chunk index
uv run python pipelines/ingest_news.py --dry-run  # collect fresh news (no write)
# optional, needs LLM_API_KEY: uv run python pipelines/extract_scanned_pdfs.py
```

## 8. Configuration files

| File | Purpose |
| --- | --- |
| `config/scoring.yaml` | relevance weights, thresholds, role preferences |
| `config/llm.yaml` | model routing + per-model pricing + budget |
| `config/industries.yaml` | OKVED sections/divisions and industry text rules |
| `config/news_sources.yaml` | RSS/open-API news sources |
| `config/products.yaml` | native product catalog (FAQ 50) |
| `.env` | API key and overrides (gitignored; see `.env.example`) |

## 9. Troubleshooting

- **Ports busy:** stop other services or change the ports in `docker-compose.yml`.
- **"failed to connect to the docker API":** start Docker Desktop.
- **Feed shows "Лента недоступна":** the API is not up, or the browser holds a
  stale client id. Check `/health`, then hard-refresh (`Ctrl+F5`) and, if needed,
  run `localStorage.clear()` in the browser console.
- **Live LLM fails / slow:** an invalid key or the daily budget. DeepSeek failures
  fall back to Gemma automatically; the insight still returns.
- **Windows CRLF warnings from git:** cosmetic; the files are stored as text.
