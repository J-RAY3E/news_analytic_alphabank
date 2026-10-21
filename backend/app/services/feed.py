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
from app.contracts import Role
from app.core.errors import DataNotReady
from app.data.industries import load_industry_catalog
from app.data.store import DataStore
from app.scoring.config import load_scoring_config
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
    for candidate in ranked:
        event = candidate.event
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
                reasons=candidate.reasons,
                role=role,
            )
        )
    return FeedResponse(
        company=row_to_company(company),
        role=role,
        items=items,
        scoring_config_version=config.version,
    )
