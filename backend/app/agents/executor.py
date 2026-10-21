from __future__ import annotations

import time
from typing import Any

from app.agents.context import CaseContext
from app.agents.guard import Guard, ToolNotAllowed, company_feature_names
from app.agents.planner import PlanStep
from app.agents.tools import ToolRegistry
from app.contracts import TraceStepKind, TraceStepStatus

OPTIONAL_TOOLS = {"get_graph_exposure", "search_bank_analytics"}


def _result_summary(result: Any) -> dict[str, Any]:
    if result is None:
        return {"count": 0}
    if isinstance(result, list):
        source_ids = [
            item.get("source_id")
            for item in result
            if isinstance(item, dict) and item.get("source_id")
        ]
        return {"count": len(result), "source_ids": source_ids}
    if isinstance(result, dict):
        return {"count": 1, "keys": sorted(result.keys())}
    return {"count": 1, "type": type(result).__name__}


class Executor:
    def __init__(self, registry: ToolRegistry, guard: Guard) -> None:
        self.registry = registry
        self.guard = guard

    def run(self, context: CaseContext, plan: list[PlanStep]) -> CaseContext:
        for step in plan:
            try:
                self.guard.authorize(step.tool, context.role, step.params)
            except ToolNotAllowed as exc:
                context.add_trace(
                    TraceStepKind.ERROR,
                    step.tool,
                    status=TraceStepStatus.FAILED,
                    payload={"error": str(exc)},
                )
                raise
            context.add_trace(
                TraceStepKind.TOOL_CALL,
                step.tool,
                payload={"purpose": step.purpose, "params": step.params},
            )
            started = time.monotonic()
            try:
                result = self.registry.call(step.tool, **step.params)
            except Exception as exc:
                elapsed = int((time.monotonic() - started) * 1000)
                self.guard.audit(
                    step.tool,
                    context.role,
                    step.params,
                    status="FAILED",
                    latency_ms=elapsed,
                    error=type(exc).__name__,
                )
                context.add_trace(
                    TraceStepKind.TOOL_RESULT,
                    step.tool,
                    status=TraceStepStatus.FAILED,
                    latency_ms=elapsed,
                    payload={"error": type(exc).__name__},
                )
                if step.tool in OPTIONAL_TOOLS:
                    context.results[step.tool] = [] if step.tool == "search_bank_analytics" else None
                    continue
                raise
            elapsed = int((time.monotonic() - started) * 1000)
            context.results[step.tool] = result
            source_ids: list[str] = []
            features: list[str] = []
            if step.tool == "get_event" and isinstance(result, dict):
                source_ids = [str(result.get("event_id"))]
            elif step.tool == "search_bank_analytics" and isinstance(result, list):
                source_ids = [
                    str(item["source_id"])
                    for item in result
                    if isinstance(item, dict) and item.get("source_id")
                ]
            elif step.tool == "get_graph_exposure" and isinstance(result, dict):
                features = company_feature_names(context.company, result)
            self.guard.audit(
                step.tool,
                context.role,
                step.params,
                status="OK",
                latency_ms=elapsed,
                result_count=len(result) if isinstance(result, list) else 1,
            )
            context.add_trace(
                TraceStepKind.TOOL_RESULT,
                step.tool,
                source_ids=source_ids,
                company_features=features,
                latency_ms=elapsed,
                payload=_result_summary(result),
            )
        return context
