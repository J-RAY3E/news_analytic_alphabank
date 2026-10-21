from __future__ import annotations

from app.agents.orchestrator import InsightOrchestrator
from app.config import Settings
from app.contracts import Insight, Role
from app.data.store import DataStore


def build_insight(
    store: DataStore,
    settings: Settings,
    company_id: str,
    event_id: str,
    role: Role,
) -> Insight:
    return InsightOrchestrator(settings, store).run(company_id, event_id, role)
