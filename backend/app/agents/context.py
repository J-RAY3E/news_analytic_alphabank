from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.contracts import (
    NormalizedEvent,
    Role,
    TraceEvent,
    TraceStepKind,
    TraceStepStatus,
)


@dataclass
class CaseContext:
    trace_id: str
    company_id: str
    event_id: str
    role: Role
    company: dict[str, Any]
    event: NormalizedEvent
    results: dict[str, Any] = field(default_factory=dict)
    trace: list[TraceEvent] = field(default_factory=list)

    def add_trace(
        self,
        kind: TraceStepKind,
        name: str,
        status: TraceStepStatus = TraceStepStatus.OK,
        source_ids: list[str] | None = None,
        company_features: list[str] | None = None,
        model: str | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        latency_ms: int | None = None,
        payload: dict[str, Any] | None = None,
    ) -> TraceEvent:
        event = TraceEvent(
            trace_id=self.trace_id,
            seq=len(self.trace),
            kind=kind,
            name=name,
            status=status,
            timestamp=datetime.now(timezone.utc),
            source_ids=source_ids or [],
            company_features=company_features or [],
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            payload=payload or {},
        )
        self.trace.append(event)
        return event

    @property
    def graph(self) -> dict[str, Any] | None:
        value = self.results.get("get_graph_exposure")
        return value if isinstance(value, dict) else None

    @property
    def bank_chunks(self) -> list[dict[str, Any]]:
        value = self.results.get("search_bank_analytics")
        return value if isinstance(value, list) else []
