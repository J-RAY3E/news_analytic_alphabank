
**[SCREENSHOT] Give screenshot from: terminal running `docker compose up --build` reaching "healthy" / both services up (or `docker compose ps` output).**

---

## Slide 18 — Mapping to judging criteria

| Criteria | Covered by |
| --- | --- |
| 01, 04 Client context & source linking | Company profile from tables, payment-graph exposure, deterministic scoring, source ids on every claim |
| 02 Multi-factor interpretation | Six answers, consequences, role-specific actions |
| 03 Bank view vs AI | Three typed labels + Critic hard rules + UI downgrade of unsourced facts |
| 05 Unseen news | Live "Проверить новость" flow (text/URL → full pipeline) |
| 06, 09, 10 Product & flow | Home-screen Radar widget, full scenario, follow-up chat, source links |
| 07 Tunability | YAML-configured industries (config/industries.yaml), scoring weights, pluggable source adapters; maintenance notes in PRD |
| 08 Metrics & monitoring | Success metrics table + feedback loop + audit/usage logs |
| 11, 12 Agentic logic | Planner/Executor/Critic loop, Agent Trace panel, Evidence Ledger |

**Planned metrics:** Precision@5 ≥ 0.7 · claims with valid sources ≥ 95% · hallucination ≤ 5% · ≤ 500 ₽/day · time-to-insight ≤ 30 s.

---

## Slide 19 — Status: what works today

Implemented and demonstrated end-to-end:

- Backend FastAPI with all contract endpoints; scoring + ranking with per-factor explanations
- Agent loop: Planner → Executor → Interpreter → Critic with correction loop; guard + audit
- RAG over the real OCR-extracted bank research corpus (9 docs / 116 chunks)
- Ingest of unseen news (text/URL) with dedup; 25-item synthetic noisy corpus
- Frontend: login, home widget, workspace, insight with typed claims, trace panel, chat, feedback, new-news tester, budget card
- Dockerized api + frontend; tests green

Honest limitations: chat answers and the trace cost figure are currently demo-scale; RBAC is design-level; deployed URL / release tag recorded at submission.

**[SCREENSHOT] Give screenshot from: the repository file tree on GitHub (root) showing backend/, frontend/, pipelines/, config/, contracts/, data/ — the scope of the delivery.**

---

## Slide 20 — Summary

**Alfa Radar turns a news stream into decisions — with receipts.**

- **Personalized**: industry, payment graph, products, geography, scale, role — six explainable factors drive every rank
- **Deep, not summary**: six answers with consequences and next actions, per role
- **Trustworthy**: every claim typed and sourced; Critic enforces it; failures stay visible
- **Real agents, real engineering**: team-built Planner/Executor/Critic, audited tool calls, governed cost
- **Works on unseen news**: paste it and get a fresh, labeled, sourced insight in under 30 seconds

**[SCREENSHOT] Give screenshot from: the Insight page of the rate-decision event for a CFO role — the single most representative screen of the product (six blocks + labels + Bank View + trace visible in one frame).**    