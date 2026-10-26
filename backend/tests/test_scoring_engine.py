import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pytest

from app.contracts import EventType, MacroFactor, Role
from app.data.industries import load_industry_catalog
from app.scoring.config import load_scoring_config
from app.scoring.engine import (
    geo_match,
    product_match,
    recency,
    score_event,
    sector_match,
    supply_chain_exposure,
)
from app.scoring.ranker import rank_events

ROOT = Path(__file__).resolve().parents[2]
SCORING = load_scoring_config(ROOT / "config" / "scoring.yaml")
CATALOG = load_industry_catalog(ROOT / "config" / "industries.yaml")


def make_company(**overrides):
    company = {
        "company_id": "U_1",
        "okved_code": "46.51",
        "okved_division": "46",
        "okved_section": "G",
        "okved_name": "Торговля оптовая",
        "industry_label": "Торговля оптовая и розничная",
        "region": "Москва",
        "city": "г. Москва",
        "revenue_rub": 20_000_000_000,
        "revenue_band": "≥ 15 млрд ₽",
        "scale_value": 1.0,
        "employees_lower_bound": 251,
        "employees_band": "Более 251",
        "fts_countries": [],
        "is_exporter": False,
        "CL_PRODUCT_LOA_MARK": True,
        "CL_PRODUCT_RKO_MARK": True,
        "CL_PRODUCT_LEA_MARK": False,
        "CL_PRODUCT_DEP_MARK": False,
        "CL_PRODUCT_GAR_MARK": False,
        "CL_PRODUCT_ZPP_MARK": False,
        "FACTORING_MARK": False,
    }
    company.update(overrides)
    return company


def make_event(event_id="news:test-1", **overrides):
    base = {
        "event_id": event_id,
        "title": "Банк России сохранил ключевую ставку",
        "summary": "Ключевая ставка осталась на уровне 16%.",
        "raw_text": "Банк России сохранил ключевую ставку на уровне 16% годовых.",
        "event_type": EventType.MONETARY_POLICY,
        "sectors": ["ALL"],
        "regions": [],
        "countries": ["Россия"],
        "macro_factors": [MacroFactor.KEY_RATE],
        "entities": ["Банк России"],
        "sentiment": "NEUTRAL",
        "source": {
            "source_id": "news:test-1",
            "name": "Synthetic",
            "published_at": datetime.now(timezone.utc).isoformat(),
        },
    }
    base.update(overrides)
    from app.contracts import NormalizedEvent

    return NormalizedEvent.model_validate(base)


def make_graph():
    return {
        "has_payment_activity": True,
        "supplier_division_shares": json.dumps({"46": 0.5, "64": 0.2}),
        "client_division_shares": json.dumps({"46": 0.4, "41": 0.1}),
    }


def test_sector_match_all_exact_same_and_miss():
    company = make_company()
    event_all = make_event()
    assert sector_match(company, event_all, SCORING, CATALOG)[0] == 1.0

    event_exact = make_event(sectors=["46"])
    assert sector_match(company, event_exact, SCORING, CATALOG)[0] == 1.0

    event_same = make_event(sectors=["G"])
    assert sector_match(company, event_same, SCORING, CATALOG)[0] == pytest.approx(0.65)

    event_miss = make_event(sectors=["41"])
    assert sector_match(company, event_miss, SCORING, CATALOG)[0] == 0.0


def test_supply_chain_all_and_sector_hit():
    event_all = make_event()
    value, _ = supply_chain_exposure(event_all, SCORING, CATALOG, make_graph())
    assert value == pytest.approx(SCORING.supply_chain.all_sectors)

    event_46 = make_event(sectors=["46"])
    value, explanation = supply_chain_exposure(event_46, SCORING, CATALOG, make_graph())
    assert value == pytest.approx(0.5)
    assert "поставщиков" in explanation

    no_activity = {"has_payment_activity": False}
    assert supply_chain_exposure(event_46, SCORING, CATALOG, no_activity)[0] == 0.0


def test_product_match_reads_product_flags_array():
    company = make_company(
        CL_PRODUCT_LOA_MARK=False,
        CL_PRODUCT_RKO_MARK=False,
        product_flags=np.array(["CL_PRODUCT_LOA_MARK", "CL_PRODUCT_DEP_MARK"]),
    )
    assert product_match(company, make_event(), SCORING)[0] == pytest.approx(1.0)


def test_product_match_key_rate_and_no_products():
    assert product_match(make_company(), make_event(), SCORING)[0] == pytest.approx(1.0)
    no_products = make_company(
        CL_PRODUCT_LOA_MARK=False,
        CL_PRODUCT_RKO_MARK=False,
    )
    assert product_match(no_products, make_event(), SCORING)[0] == 0.0


def test_geo_match_region_domestic_and_foreign():
    company = make_company()
    assert geo_match(company, make_event(regions=["Москва"]), SCORING, CATALOG)[0] == 1.0
    assert geo_match(company, make_event(regions=["Татарстан"]), SCORING, CATALOG)[0] == 0.0
    assert geo_match(company, make_event(), SCORING, CATALOG)[0] == pytest.approx(0.6)

    exporter = make_company(fts_countries=["КИТАЙ"], is_exporter=True)
    foreign = make_event(countries=["Китай"], macro_factors=[MacroFactor.SUPPLY_CHAIN])
    assert geo_match(exporter, foreign, SCORING, CATALOG)[0] == pytest.approx(0.9)


def test_recency_decay_and_missing():
    fresh = make_event()
    assert recency(fresh, SCORING)[0] > 0.99
    old = make_event(
        source={
            "source_id": "news:old",
            "name": "Synthetic",
            "published_at": (datetime.now(timezone.utc) - timedelta(days=60)).isoformat(),
        }
    )
    assert recency(old, SCORING)[0] < 0.01
    missing = make_event(source={"source_id": "news:x", "name": "Synthetic"})
    assert recency(missing, SCORING)[0] == SCORING.recency.missing


def test_score_event_contributions_and_bounds():
    result = score_event(
        make_company(),
        make_event(),
        SCORING,
        CATALOG,
        graph_row=make_graph(),
    )
    assert 0.0 <= result.score <= 1.0
    assert result.config_version == SCORING.version
    assert len(result.factors) == 7
    assert sum(factor.contribution for factor in result.factors) == pytest.approx(
        result.score, abs=1e-5
    )
    assert result.score > 0.8


def test_ranker_prefers_role_on_tie():
    company = make_company()
    monetary = make_event("news:monetary", event_type=EventType.MONETARY_POLICY)
    regulation = make_event(
        "news:logistics",
        event_type=EventType.LOGISTICS,
        macro_factors=[MacroFactor.KEY_RATE],
        sectors=["ALL"],
    )
    ranked = rank_events(
        company,
        [regulation, monetary],
        SCORING,
        CATALOG,
        graph_row=make_graph(),
        role=Role.CFO,
        limit=2,
        diversify=False,
    )
    assert ranked[0].event.event_type == EventType.MONETARY_POLICY
    assert ranked[0].role_preference is True
