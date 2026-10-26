from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.agents.context import CaseContext
from app.agents.tools import build_retrieval_query


@dataclass(frozen=True)
class PlanStep:
    tool: str
    params: dict[str, Any] = field(default_factory=dict)
    purpose: str = ""


class Planner:
    def build(self, context: CaseContext) -> list[PlanStep]:
        query = build_retrieval_query(context.event)
        return [
            PlanStep(
                tool="plan_write",
                params={
                    "trace_id": context.trace_id,
                    "plan": [
                        "get_company_profile",
                        "get_graph_exposure",
                        "get_event",
                        "search_bank_analytics",
                    ],
                },
                purpose="Зафиксировать план (A1 plan_write)",
            ),
            PlanStep(
                tool="budget_check",
                params={},
                purpose="Проверить остаток дневного бюджета LLM (A1 budget_check)",
            ),
            PlanStep(
                tool="get_company_profile",
                params={"company_id": context.company_id},
                purpose="Профиль и продукты компании",
            ),
            PlanStep(
                tool="get_graph_exposure",
                params={"company_id": context.company_id},
                purpose="Платежные связи и отраслевая экспозиция",
            ),
            PlanStep(
                tool="get_group_view",
                params={"company_id": context.company_id},
                purpose="Контекст группы компаний (Q24/Q25)",
            ),
            PlanStep(
                tool="get_event",
                params={"event_id": context.event_id},
                purpose="Нормализованное событие и его источник",
            ),
            PlanStep(
                tool="search_bank_analytics",
                params={"query": query, "k": 4},
                purpose="Релевантная аналитика и позиция банка",
            ),
        ]
