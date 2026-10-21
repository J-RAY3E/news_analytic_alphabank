from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.contracts import (
    ClaimType,
    EvidenceClaim,
    Insight,
    NormalizedEvent,
    RelevanceFactor,
    RelevanceScore,
    Role,
    SourceRef,
    TraceEvent,
    TraceStepKind,
)


def make_event() -> NormalizedEvent:
    return NormalizedEvent(
        event_id="news:test-1",
        title="ЦБ сохранил ключевую ставку",
        summary="Ключевая ставка осталась на уровне 16%.",
        raw_text="Банк России сохранил ключевую ставку на уровне 16% годовых.",
        event_type="MONETARY_POLICY",
        sectors=["64"],
        regions=["Москва"],
        countries=["Россия"],
        macro_factors=["KEY_RATE"],
        entities=["Банк России", "ЦБ РФ"],
        sentiment="NEUTRAL",
        source=SourceRef(
            source_id="news:test-1",
            name="Synthetic Wire",
            url="https://example.com/news/1",
            published_at=datetime(2026, 10, 20, tzinfo=timezone.utc),
        ),
    )


def test_normalized_event_valid() -> None:
    event = make_event()
    assert event.event_id == "news:test-1"
    assert event.macro_factors[0].value == "KEY_RATE"
    assert event.source.source_id == event.event_id


def test_event_rejects_unknown_macro_factor() -> None:
    with pytest.raises(ValidationError):
        NormalizedEvent(
            event_id="news:bad",
            title="Bad event",
            event_type="OTHER",
            macro_factors=["NOT_A_FACTOR"],
            source=SourceRef(source_id="news:bad", name="test"),
        )


def test_claim_dedupes_ids_and_requires_type() -> None:
    claim = EvidenceClaim(
        text="Ставка не изменилась.",
        type=ClaimType.FACT,
        source_ids=["news:1", "news:1", " "],
        company_features=["CL_PRODUCT_LOA_MARK"],
        confidence=0.9,
    )
    assert claim.source_ids == ["news:1"]

    with pytest.raises(ValidationError):
        EvidenceClaim(text="x", type="GUESS", confidence=0.5)


def test_insight_contract_roundtrip() -> None:
    claim = EvidenceClaim(
        text="Компания использует кредитные продукты.",
        type=ClaimType.AI_INFERENCE,
        source_ids=["news:test-1"],
        company_features=["CL_PRODUCT_LOA_MARK"],
        confidence=0.7,
    )
    score = RelevanceScore(
        score=0.5,
        factors=[
            RelevanceFactor(
                name="sector_match",
                value=1.0,
                weight=0.3,
                contribution=0.3,
                explanation="Совпадение отрасли",
            )
        ],
        config_version="1",
    )
    trace = TraceEvent(
        trace_id="trace:1",
        seq=0,
        kind=TraceStepKind.PLAN,
        name="planner",
        source_ids=["news:test-1"],
    )
    insight = Insight(
        insight_id="insight:1",
        company_id="U_1",
        event_id="news:test-1",
        role=Role.CFO,
        what_happened=[claim],
        why_it_matters=[claim],
        consequences=[],
        actions=[],
        bank_view=[],
        basis=[claim],
        relevance_score=score,
        trace=[trace],
    )
    restored = Insight.model_validate_json(insight.model_dump_json())
    assert restored.role == Role.CFO
    assert restored.relevance_score.factors[0].contribution == 0.3
