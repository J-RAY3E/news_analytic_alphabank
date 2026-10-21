from __future__ import annotations

import json
from uuid import uuid4

from app.agents.a6_interpreter import A6Interpreter, Interpretation
from app.agents.context import CaseContext
from app.agents.critic import CriticResult, evaluate
from app.agents.executor import Executor
from app.agents.guard import Guard
from app.agents.planner import Planner
from app.agents.tools import ToolRegistry
from app.config import Settings
from app.contracts import (
    Insight,
    Role,
    TraceStepKind,
    TraceStepStatus,
)
from app.data.industries import load_industry_catalog
from app.data.store import DataStore
from app.llm.client import LLMClient
from app.research.index import ResearchIndex, load_research_index
from app.scoring.config import load_scoring_config
from app.scoring.engine import RelevanceScore, score_event

MAX_CORRECTION_LOOPS = 2


class InsightOrchestrator:
    def __init__(
        self,
        settings: Settings,
        store: DataStore,
        index: ResearchIndex | None = None,
        llm: LLMClient | None = None,
    ) -> None:
        self.settings = settings
        self.store = store
        if index is None:
            index_path = settings.path("index", "research_chunks.jsonl")
            index = load_research_index(str(index_path)) if index_path.exists() else None
        self.index = index
        self.llm = llm or LLMClient(settings)
        self.guard = Guard(settings)
        self.tools = ToolRegistry(store, settings, index=index, llm=self.llm)
        self.executor = Executor(self.tools, self.guard)
        self.planner = Planner()
        self.interpreter = A6Interpreter(settings, self.llm)

    def run(self, company_id: str, event_id: str, role: Role) -> Insight:
        company = self.store.company(company_id)
        event = self.store.event(event_id)
        trace_id = f"trace:{uuid4().hex[:12]}"
        context = CaseContext(
            trace_id=trace_id,
            company_id=company_id,
            event_id=event_id,
            role=role,
            company=company,
            event=event,
        )
        plan = self.planner.build(context)
        context.add_trace(
            TraceStepKind.PLAN,
            "insight_plan",
            payload={
                "steps": [
                    {"tool": step.tool, "purpose": step.purpose} for step in plan
                ],
                "llm_enabled": self.llm.enabled,
            },
        )
        self.executor.run(context, plan)

        relevance = score_event(
            company=company,
            event=event,
            config=load_scoring_config(str(self.settings.scoring_config)),
            catalog=load_industry_catalog(str(self.settings.industries_config)),
            graph_row=context.graph,
        )
        interpretation = self._interpret_with_critic(context, relevance)
        context.add_trace(
            TraceStepKind.COMPLETED,
            "interpret",
            model=interpretation.model,
            prompt_tokens=interpretation.prompt_tokens,
            completion_tokens=interpretation.completion_tokens,
            payload={
                "method": interpretation.method,
                "error": interpretation.error,
                "relevance_score": relevance.score,
                "bank_sources": len(context.bank_chunks),
                "cached": interpretation.cached,
                "critic": interpretation.critic_payload,
            },
        )
        insight = Insight(
            insight_id=f"insight:{uuid4().hex[:12]}",
            company_id=company_id,
            event_id=event_id,
            role=role,
            what_happened=interpretation.blocks["what_happened"],
            why_it_matters=interpretation.blocks["why_it_matters"],
            consequences=interpretation.blocks["consequences"],
            actions=interpretation.blocks["actions"],
            bank_view=interpretation.blocks["bank_view"],
            basis=interpretation.blocks["basis"],
            relevance_score=relevance,
            trace=context.trace,
        )
        self._persist(insight)
        return insight

    def _interpret_with_critic(
        self, context: CaseContext, relevance: RelevanceScore
    ) -> "Interpretation":
        interpretation = None
        critic: CriticResult | None = None
        for attempt in range(MAX_CORRECTION_LOOPS):
            interpretation = self.interpreter.interpret(
                context, relevance, prefer_fallback=attempt > 0
            )
            critic = evaluate(
                interpretation.blocks,
                context.event_id,
                context.bank_chunks,
            )
            context.add_trace(
                TraceStepKind.CRITIC_CHECK,
                "deterministic_checks",
                status=TraceStepStatus.OK
                if critic.passed
                else TraceStepStatus.FAILED,
                payload={
                    "attempt": attempt + 1,
                    "checks": critic.checks,
                    "failed": critic.failed,
                },
            )
            if critic.passed:
                interpretation.critic_payload = {
                    "passed": True,
                    "correction_iterations": attempt,
                }
                return interpretation
            if attempt + 1 < MAX_CORRECTION_LOOPS:
                context.add_trace(
                    TraceStepKind.RETRY,
                    "critic_revision",
                    payload={
                        "reason": "critic_failed",
                        "failed": critic.failed,
                        "strategy": "deterministic_revision",
                    },
                )
        interpretation.critic_payload = {
            "passed": False,
            "failed": critic.failed,
            "correction_iterations": MAX_CORRECTION_LOOPS - 1,
        }
        return interpretation

    def _persist(self, insight: Insight) -> None:
        insights_dir = self.settings.path("insights")
        traces_dir = self.settings.path("traces")
        insights_dir.mkdir(parents=True, exist_ok=True)
        traces_dir.mkdir(parents=True, exist_ok=True)
        insight_path = insights_dir / f"{insight.insight_id.replace(':', '_')}.json"
        insight_path.write_text(
            insight.model_dump_json(indent=2), encoding="utf-8"
        )
        trace_payload = {
            "trace_id": insight.trace[0].trace_id if insight.trace else "",
            "events": [event.model_dump(mode="json") for event in insight.trace],
        }
        trace_path = traces_dir / f"{trace_payload['trace_id']}.json"
        trace_path.write_text(
            json.dumps(trace_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
