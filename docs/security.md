# Alfa Radar — Security Design

This document describes the security model of Alfa Radar and marks what is
implemented in the prototype versus designed for production (PRD FR-24:
"role-based access, masking of sensitive fields before prompts, allowlisted
tools, audit log of every tool call", priority P0 design / P1 implementation).

## Status summary

| Mechanism | Status | Location |
| --- | --- | --- |
| Tool allowlist + parameter validation | Implemented | `backend/app/agents/guard.py` (`ALLOWED_TOOLS`, `authorize`) |
| Sensitive-field masking before prompts | Implemented | `backend/app/agents/guard.py` (`prompt_safe_company`, `prompt_safe_graph`) |
| Append-only audit log (tool + model calls) | Implemented | `backend/app/agents/guard.py` (`Guard.audit`, `ModelAudit`) → `data/audit/tool_calls.jsonl` |
| Untrusted-input framing (news, PDFs) | Implemented | A2/A6 prompts (`<untrusted_news>`, `<bank_research>`), schema validation |
| SSRF guard on URL ingestion | Implemented | `backend/app/news/extract.py` (`validate_public_url`) |
| No write / external-action tools | Implemented | all tools read-only (`ToolRegistry`) |
| Role-based access control (authentication + authorization) | **Design only** | described below; `role` is a demo request parameter today |
| Row-level company authorization | **Design only** | described below |

## Trust boundary — A0 Guard

`A0` is a deterministic middleware layer (not an LLM). Every data access and
tool call passes through it. It enforces:

- **Tool allowlist.** Only these read-only tools may run: `plan_write`,
  `budget_check`, `get_company_profile`, `get_graph_exposure`, `get_event`,
  `search_bank_analytics`, `get_bank_card`, `search_news`. Unknown tools raise
  `ToolNotAllowed` and are recorded as failed steps.
- **Parameter validation.** Missing `company_id`/`event_id`, out-of-range `k`,
  and malformed plans are rejected before execution.
- **No write capability.** Tools only read the data store and the research
  index; there is no tool that mutates data or performs external actions.

## Prompt-injection defense

News pages and research documents are treated as untrusted data, never as
instructions:

- Untrusted content is wrapped in explicit delimiters (`<untrusted_news>`,
  `<bank_research>`) and the system prompts instruct the model to ignore any
  commands found inside them.
- All LLM output is validated against strict schemas (`LLMLedger`,
  `NormalizedEvent`); anything off-schema or referencing an unknown source id is
  dropped.
- Claim source ids and company features are filtered against an allowlist built
  from the actual retrieved evidence, so the model cannot invent citations.

## Sensitive-data handling

Before any field reaches a prompt, `prompt_safe_company` and
`prompt_safe_graph` remove identifying columns (`company_id`, `group_id`, INN,
OGRN, KPP, names, addresses) and pass only aggregates: industry, region, scale
bands, product flags, exporter status and payment-graph shares. Counterparties
are pseudonymized. Client data is used as context only, never as factual
evidence.

## Audit log

Every tool call and every model call is appended to
`data/audit/tool_calls.jsonl` with a timestamp, role, tool/model name, status,
latency and (for models) token counts and cost. The log is append-only and is
correlated with the request trace id.

## Role-based access control (designed, not implemented)

In production, access would be enforced as follows:

1. **Authentication** — the Alfa-Business session issues a signed token
   (`POST /auth/login` with test accounts in the prototype). The token carries
   the user id and role.
2. **Authorization** — a FastAPI dependency resolves the token to a user and
   checks that the requested `company_id` is within the user's allowed set
   (row-level security). Requests for other companies return `403`.
3. **Role scoping** — the effective role comes from the token, not from a
   request parameter; it selects the Role Lens guidance and the ranking
   tie-break.
4. **Audit** — authorization decisions (allow/deny) are written to the audit
   log alongside tool and model calls.

In this prototype the boundary above is stubbed: the frontend login is a local
demo selector, the `role` is a request parameter, and `company_id` is not
constrained per user. Masking, the allowlist and the audit log are real, so an
implemented authorization layer would slot in at A0 without changing the agent
modules.

## Network safety

`/ingest` with a URL fetches the page through `validate_public_url`, which
rejects non-HTTP(S) schemes, localhost/.local hosts and private, loopback,
link-local, reserved, multicast or unspecified IP addresses, mitigating SSRF and
prompt-injection-by-fetch.

## Out of scope (prototype)

Production hardening (real identity provider, TLS termination, secret
management, rate limiting, malware scanning of uploaded content) is out of scope
for the hackathon prototype and noted here for completeness.
