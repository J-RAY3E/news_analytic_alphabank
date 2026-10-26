from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from app.config import Settings
from app.contracts import NormalizedEvent
from app.core.errors import NotFound
from app.data.store import DataStore
from app.llm.client import LLMClient
from app.llm.config import load_llm_config
from app.llm.governor import CostGovernor
from app.research.index import ResearchIndex

REGISTRY_TOOLS = {
    "plan_write",
    "budget_check",
    "get_company_profile",
    "get_graph_exposure",
    "get_group_view",
    "get_event",
    "search_bank_analytics",
    "get_bank_card",
    "search_news",
}


class ToolRegistry:
    def __init__(
        self,
        store: DataStore,
        settings: Settings,
        index: ResearchIndex | None = None,
        retriever: Any = None,
        llm: LLMClient | None = None,
    ) -> None:
        self.store = store
        self.settings = settings
        self.index = index
        self.retriever = retriever
        if self.retriever is None and index is not None:
            from app.agents.a4_retriever import A4Retriever

            self.retriever = A4Retriever(index)
        governor = getattr(llm, "governor", None)
        if governor is not None:
            self.governor = governor
        else:
            self.governor = CostGovernor(
                load_llm_config(str(settings.llm_config)),
                settings.path("cache", "llm_usage.jsonl"),
            )

    def _graph_row(self, company_id: str) -> dict[str, Any] | None:
        try:
            frame = self.store.graph
        except Exception:
            return None
        if company_id not in frame.index:
            return None
        row = frame.loc[company_id]
        if hasattr(row, "iloc") and getattr(row, "ndim", 1) > 1:
            row = row.iloc[0]
        return row.to_dict()

    def plan_write(self, trace_id: str, plan: list[dict[str, Any]]) -> dict[str, Any]:
        path = self.settings.path("agent", "plans.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": trace_id,
            "plan": plan,
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        return {"written": str(path), "steps": len(plan)}

    def budget_check(self) -> dict[str, Any]:
        return self.governor.summary()

    def get_company_profile(self, company_id: str) -> dict[str, Any]:
        return self.store.company(company_id)

    def get_graph_exposure(self, company_id: str) -> dict[str, Any] | None:
        return self._graph_row(company_id)

    def get_group_view(self, company_id: str) -> dict[str, Any] | None:
        company = self.store.company(company_id)
        group_id = str(company.get("group_id") or "").strip()
        if not group_id:
            return None
        frame = self.store.companies
        members = frame[frame["group_id"].astype(str) == group_id]
        rows: list[dict[str, Any]] = []
        for _, row in members.iterrows():
            rows.append(
                {
                    "company_id": row.get("company_id"),
                    "industry_label": row.get("industry_label"),
                    "okved_division": row.get("okved_division"),
                    "revenue_band": row.get("revenue_band"),
                }
            )
        return {
            "group_id": group_id,
            "group_size": len(rows),
            "group_revenue_rub": float(company.get("group_revenue_rub") or 0.0),
            "members": rows[:20],
        }

    def get_event(self, event_id: str) -> dict[str, Any]:
        return self.store.event(event_id).model_dump(mode="json")

    def search_bank_analytics(self, query: str, k: int = 4) -> list[dict[str, Any]]:
        if self.retriever is None:
            return []
        return self.retriever.search(query, k=k)

    def get_bank_card(self, doc_id: str) -> list[dict[str, Any]]:
        if self.retriever is None:
            return []
        return self.retriever.get_card(doc_id)

    def search_news(self, query: str, k: int = 5) -> list[dict[str, Any]]:
        tokens = [
            token for token in query.casefold().split() if len(token) > 2
        ]
        scored: list[tuple[int, int, NormalizedEvent]] = []
        for event in self.store.events_or_empty():
            haystack = " ".join(
                (
                    event.title,
                    event.summary,
                    " ".join(event.entities),
                    " ".join(event.regions),
                    " ".join(event.countries),
                    " ".join(event.sectors),
                )
            ).casefold()
            score = sum(1 for token in tokens if token in haystack)
            if score > 0:
                scored.append((score, event.noise_score, event))
        scored.sort(key=lambda item: (-item[0], item[1]))
        results: list[dict[str, Any]] = []
        for _, _, event in scored[: max(1, min(k, 10))]:
            results.append(
                {
                    "event_id": event.event_id,
                    "title": event.title,
                    "summary": event.summary,
                    "event_type": event.event_type.value,
                    "published_at": event.source.published_at.isoformat()
                    if event.source.published_at
                    else None,
                    "source_id": event.source.source_id,
                }
            )
        return results

    def call(self, tool: str, **params: Any) -> Any:
        if tool not in REGISTRY_TOOLS:
            raise ValueError(f"unknown tool: {tool}")
        return getattr(self, tool)(**params)


def build_retrieval_query(event: NormalizedEvent) -> str:
    parts = [
        event.title,
        event.summary[:600],
        " ".join(event.sectors),
        " ".join(factor.value for factor in event.macro_factors),
        " ".join(event.regions),
        " ".join(event.countries),
    ]
    return " ".join(part for part in parts if part).strip()


def graph_json_map(value: Any) -> dict[str, float]:
    if isinstance(value, dict):
        return {str(key): float(item) for key, item in value.items()}
    if isinstance(value, str) and value.strip():
        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            return {}
        if isinstance(loaded, dict):
            return {str(key): float(item) for key, item in loaded.items()}
    return {}
