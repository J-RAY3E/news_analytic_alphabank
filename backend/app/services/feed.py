from __future__ import annotations

from typing import Any

import pandas as pd

from app.api.mappers import row_to_company
from app.api.schemas import (
    FeedEventCard,
    FeedItem,
    FeedResponse,
    RelevanceFactorResponse,
)
from app.config import Settings
from app.contracts import Impact, Role
from app.core.errors import DataNotReady
from app.data.industries import load_industry_catalog
from app.data.store import DataStore
from app.scoring.config import load_scoring_config
from app.scoring.engine import parse_event_sectors
from app.scoring.ranker import rank_events


def _graph_row(store: DataStore, company_id: str) -> dict[str, Any] | None:
    try:
        graph = store.graph
    except DataNotReady:
        return None
    if company_id not in graph.index:
        return None
    row = graph.loc[company_id]
    if isinstance(row, pd.DataFrame):
        row = row.iloc[0]
    return row.to_dict()


GENERIC_REASON = "Событие затрагивает все отрасли экономики"
MEDIUM_IMPACT_MIN = 0.4


def _impact(event, score: float, high_min: float) -> Impact:
    risk = event.risk_opportunity.value
    if risk == "RISK" and score >= high_min:
        return Impact.HIGH
    if risk in {"RISK", "OPPORTUNITY", "BOTH"} and score >= MEDIUM_IMPACT_MIN:
        return Impact.MEDIUM
    if score >= high_min:
        return Impact.MEDIUM
    return Impact.LOW


def _group_context(
    store: DataStore, company: dict[str, Any], event, catalog
) -> tuple[str | None, bool]:
    group_id = str(company.get("group_id") or "").strip()
    if not group_id:
        return None, False
    try:
        frame = store.companies
    except DataNotReady:
        return group_id, False
    members = frame[
        (frame["group_id"].astype(str) == group_id)
        & (frame["company_id"].astype(str) != str(company.get("company_id")))
    ]
    if members.empty:
        return group_id, False
    _, divisions, sections = parse_event_sectors(event, catalog)
    if not divisions and not sections:
        return group_id, False
    member_sections = {str(value) for value in members["okved_section"].dropna().tolist()}
    member_divisions = {str(value) for value in members["okved_division"].dropna().tolist()}
    via = bool((sections & member_sections) or (divisions & member_divisions))
    return group_id, via


def build_feed(
    store: DataStore,
    settings: Settings,
    company_id: str,
    role: Role,
    limit: int = 10,
) -> FeedResponse:
    company = store.company(company_id)
    config = load_scoring_config(settings.scoring_config)
    catalog = load_industry_catalog(settings.industries_config)
    graph = _graph_row(store, company_id)
    ranked = rank_events(
        company=company,
        events=store.events,
        config=config,
        catalog=catalog,
        graph_row=graph,
        role=role,
        limit=limit,
    )
    items: list[FeedItem] = []
    external_sources = {name.casefold() for name in config.external_sources}
    for candidate in ranked:
        event = candidate.event
        group_id, via_group = _group_context(store, company, event, catalog)
        reasons = [reason for reason in candidate.reasons if reason != GENERIC_REASON]
        items.append(
            FeedItem(
                event=FeedEventCard(
                    event_id=event.event_id,
                    title=event.title,
                    summary=event.summary,
                    event_type=event.event_type,
                    sectors=event.sectors,
                    regions=event.regions,
                    countries=event.countries,
                    macro_factors=event.macro_factors,
                    sentiment=event.sentiment,
                    risk_opportunity=event.risk_opportunity,
                    published_at=event.source.published_at,
                    source_name=event.source.name,
                    source_url=event.source.url,
                ),
                relevance_score=candidate.relevance.score,
                factors=[
                    RelevanceFactorResponse(
                        name=factor.name,
                        value=factor.value,
                        weight=factor.weight,
                        contribution=factor.contribution,
                        explanation=factor.explanation,
                    )
                    for factor in candidate.relevance.factors
                ],
                reasons=reasons or candidate.reasons,
                role=role,
                urgent=(
                    event.risk_opportunity.value == "RISK"
                    and candidate.relevance.score >= config.urgency.min_score
                ),
                impact=_impact(event, candidate.relevance.score, config.urgency.min_score),
                via_group=via_group,
                group_id=group_id if via_group else None,
                external=event.source.name.casefold() in external_sources,
            )
        )
    return FeedResponse(
        company=row_to_company(company),
        role=role,
        items=items,
        scoring_config_version=config.version,
    )
