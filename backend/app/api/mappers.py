from __future__ import annotations

from typing import Any

import pandas as pd

from app.api.schemas import (
    ClaimResponse,
    CompanySummary,
    InsightResponse,
    RelevanceFactorResponse,
)
from app.contracts import Insight

DISCLAIMER = (
    "Материал подготовлен сервисом Alfa Radar на основе открытых источников и аналитики Альфа-Банка. Не является инвестиционной рекомендацией."
)


def clean_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, float) and pd.isna(value):
        return default
    if value is pd.NA:
        return default
    text = str(value).strip()
    return text if text and text.casefold() not in {"nan", "none", "<na>"} else default


def clean_list(value: Any) -> list[str]:
    if value is None:
        return []
    if hasattr(value, "tolist") and not isinstance(value, (str, bytes)):
        value = value.tolist()
    if isinstance(value, float) and pd.isna(value):
        return []
    if isinstance(value, (list, tuple, set)):
        return [clean_str(item) for item in value if clean_str(item)]
    text = clean_str(value)
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]


def row_to_company(row: pd.Series | dict[str, Any]) -> CompanySummary:
    data = row.to_dict() if isinstance(row, pd.Series) else row
    return CompanySummary(
        company_id=clean_str(data.get("company_id")),
        display_name=clean_str(data.get("display_name")),
        okved_code=clean_str(data.get("okved_code")),
        okved_name=clean_str(data.get("okved_name")),
        okved_division=clean_str(data.get("okved_division")) or None,
        okved_section=clean_str(data.get("okved_section")) or None,
        industry_label=clean_str(data.get("industry_label")),
        region=clean_str(data.get("region")),
        city=clean_str(data.get("city")),
        revenue_rub=(
            0.0
            if data.get("revenue_rub") is None or pd.isna(data.get("revenue_rub"))
            else float(data.get("revenue_rub"))
        ),
        revenue_band=clean_str(data.get("revenue_band")),
        employees_band=clean_str(data.get("employees_band")),
        client_type=clean_str(data.get("client_type")),
        product_flags=clean_list(data.get("product_flags")),
        is_exporter=bool(data.get("is_exporter") or False),
        fts_countries=clean_list(data.get("fts_countries")),
        group_id=clean_str(data.get("group_id")) or None,
        group_size=int(data.get("group_size") or 1),
        group_revenue_rub=(
            0.0
            if data.get("group_revenue_rub") is None
            or pd.isna(data.get("group_revenue_rub"))
            else float(data.get("group_revenue_rub"))
        ),
    )


def insight_to_response(insight: Insight) -> InsightResponse:
    def claims(items):
        return [ClaimResponse(**claim.model_dump()) for claim in items]

    return InsightResponse(
        insight_id=insight.insight_id,
        company_id=insight.company_id,
        event_id=insight.event_id,
        role=insight.role,
        created_at=insight.created_at,
        what_happened=claims(insight.what_happened),
        why_it_matters=claims(insight.why_it_matters),
        consequences=claims(insight.consequences),
        actions=claims(insight.actions),
        bank_view=claims(insight.bank_view),
        basis=claims(insight.basis),
        relevance_score=insight.relevance_score.score,
        scoring_factors=[
            RelevanceFactorResponse(**factor.model_dump())
            for factor in insight.relevance_score.factors
        ],
        disclaimer=DISCLAIMER,
        trace=[event.model_dump(mode="json") for event in insight.trace],
    )
