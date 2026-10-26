from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.contracts import NormalizedEvent, RelevanceScore, Role
from app.data.industries import IndustryCatalog
from app.news.normalize import event_similarity
from app.scoring.config import ScoringConfig
from app.scoring.engine import score_event


@dataclass(frozen=True)
class RankedEvent:
    event: NormalizedEvent
    relevance: RelevanceScore
    reasons: list[str]
    role_preference: bool


def _role_preference(event: NormalizedEvent, role: Role, config: ScoringConfig) -> bool:
    return event.event_type in config.roles.preferences.get(role, [])


def rank_events(
    company: dict,
    events: list[NormalizedEvent],
    config: ScoringConfig,
    catalog: IndustryCatalog,
    graph_row: dict | None = None,
    role: Role = Role.CEO,
    limit: int = 10,
    now: datetime | None = None,
    diversify: bool = True,
) -> list[RankedEvent]:
    candidates: list[RankedEvent] = []
    for event in events:
        relevance = score_event(
            company, event, config, catalog, graph_row=graph_row, now=now
        )
        reasons = [
            factor.explanation
            for factor in sorted(
                relevance.factors, key=lambda factor: factor.contribution, reverse=True
            )
            if factor.contribution > 0
        ][:3]
        candidates.append(
            RankedEvent(
                event=event,
                relevance=relevance,
                reasons=reasons,
                role_preference=_role_preference(event, role, config),
            )
        )

    if config.min_score > 0:
        candidates = [
            candidate
            for candidate in candidates
            if candidate.relevance.score >= config.min_score
        ]

    candidates.sort(
        key=lambda item: (
            -item.relevance.score,
            -int(item.role_preference),
            -(item.event.source.published_at.timestamp() if item.event.source.published_at else 0),
        )
    )

    tolerance = config.roles.tie_break_tolerance
    for index in range(len(candidates) - 1):
        current = candidates[index]
        following = candidates[index + 1]
        if (
            abs(current.relevance.score - following.relevance.score) <= tolerance
            and following.role_preference
            and not current.role_preference
        ):
            candidates[index], candidates[index + 1] = following, current

    if diversify:
        kept: list[RankedEvent] = []
        for candidate in candidates:
            if all(
                event_similarity(candidate.event, existing.event) < 0.88
                for existing in kept
            ):
                kept.append(candidate)
        candidates = kept

    return candidates[:limit]
