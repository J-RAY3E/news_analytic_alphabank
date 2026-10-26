from __future__ import annotations

import json
from pathlib import Path

from app.contracts import Role
from app.data.store import DataStore
from app.config import Settings


def list_insights(
    settings: Settings,
    store: DataStore,
    company_id: str | None = None,
    role: Role | None = None,
    limit: int = 20,
) -> tuple[list[dict], int]:
    directory = settings.path("insights")
    if not directory.exists():
        return [], 0
    files = sorted(
        directory.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True
    )
    items: list[dict] = []
    total = 0
    for path in files:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if company_id and payload.get("company_id") != company_id:
            continue
        if role and payload.get("role") != role.value:
            continue
        total += 1
        if len(items) >= limit:
            continue
        relevance = payload.get("relevance_score")
        score = 0.0
        top_reason = None
        if isinstance(relevance, dict):
            score = float(relevance.get("score", 0.0))
            factors = relevance.get("factors") or []
            if factors:
                best = max(
                    factors, key=lambda factor: factor.get("contribution", 0.0)
                )
                top_reason = best.get("explanation")
        title = None
        try:
            title = store.event(payload.get("event_id", "")).title
        except Exception:
            title = None
        items.append(
            {
                "insight_id": payload.get("insight_id", path.stem),
                "company_id": payload.get("company_id", ""),
                "event_id": payload.get("event_id", ""),
                "event_title": title,
                "role": payload.get("role", "CEO"),
                "created_at": payload.get("created_at"),
                "relevance_score": round(score, 6),
                "top_reason": top_reason,
            }
        )
    return items, total
