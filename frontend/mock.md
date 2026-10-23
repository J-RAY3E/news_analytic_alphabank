# Frontend mock status vs backend (PRD reference)

Read together with `prd.md` (FR-numbers) and `contracts/openapi.json`.
`NEXT_PUBLIC_USE_MOCKS=true` in `frontend/.env.local` switches all data to mocks.
Flip to `false` when the backend endpoint is ready. Each mock lives in
`frontend/lib/mocks/`.

## Endpoints

| Endpoint | PRD | Mock status | Backend status | Notes |
|---|---|---|---|---|
| GET /health | FR-26 | bypassed | ready | used only by ops |
| GET /companies | FR-1 | mocked (5 anonymized clients) | ready per contract | mock adds industry labels |
| GET /companies/{id} | FR-1 | mocked | ready per contract | unused in UI today |
| GET /feed | FR-3, FR-4, FR-17 | mocked (7 events, full factors) | ready per contract | reasons are demo strings from PRD examples |
| GET /events/{id} | FR-6 | mocked | ready per contract | only title/summary/source used |
| POST /ingest | FR-9, FR-21 | mocked, returns demo REGULATION event | **not ready**: no extraction | UI shows 5-step progress |
| POST /insight | FR-12, FR-18 | mocked (6 blocks, typed claims, inline trace) | ready per contract | claims demo content |
| GET /trace/{id} | FR-19 | mocked (static trace-demo-001) | **not ready**: agent trace empty | insight.trace inline used instead |
| POST /feedback | FR-22 | mocked, always stored | ready per contract | - |

## UI features with no backend contract yet

| Feature | PRD | Status | Needed from backend |
|---|---|---|---|
| Follow-up chat | FR-20 | mocked replies, canned | no chat endpoint in openapi.json; needs POST /insight/{id}/chat |
| Budget meter | FR-23 | static demo numbers on home (labeled "Демо-данные") | needs GET /metrics or /budget |
| Source chips -> real docs | FR-18 | mock map in `lib/mocks/data.ts` (MOCK_SOURCES) | source registry endpoint or resolve source_ids server-side |
| Critic banner | FR-13 | derived from inline trace FAILED events | same, works when backend fills trace |
| Stepper for new news | FR-21 | timed fake progress around mock ingest | optional POST /ingest streaming or polling |

## Demo content caveats

- Companies are anonymized (PRD non-goal: no real identification).
- All insight texts and claims are synthetic demo content, not bank analytics.
- Trace tokens/cost in header are computed from mock trace numbers.
