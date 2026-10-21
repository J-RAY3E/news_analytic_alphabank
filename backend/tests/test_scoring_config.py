from pathlib import Path

import pytest
from pydantic import ValidationError

from app.contracts import EventType, MacroFactor, Role
from app.data.industries import load_industry_catalog
from app.scoring.config import ScoringConfig, load_scoring_config

ROOT = Path(__file__).resolve().parents[2]
SCORING = ROOT / "config" / "scoring.yaml"
INDUSTRIES = ROOT / "config" / "industries.yaml"


def test_scoring_config_loads_and_sums_to_one() -> None:
    config = load_scoring_config(SCORING)
    assert isinstance(config, ScoringConfig)
    assert sum(config.weights.model_dump().values()) == pytest.approx(1.0)
    assert config.product.factor_features[MacroFactor.KEY_RATE]["CL_PRODUCT_LOA_MARK"] == 1.0
    assert EventType.MONETARY_POLICY in config.roles.preferences[Role.CFO]


def test_scoring_config_rejects_bad_weight_sum(tmp_path: Path) -> None:
    payload = SCORING.read_text(encoding="utf-8").replace(
        "sector_match: 0.30", "sector_match: 0.40"
    )
    target = tmp_path / "scoring.yaml"
    target.write_text(payload, encoding="utf-8")
    with pytest.raises(ValidationError, match="sum to 1.0"):
        load_scoring_config(target)


def test_industry_catalog_maps_okved_sections() -> None:
    catalog = load_industry_catalog(INDUSTRIES)
    assert catalog.division_of("46.51") == "46"
    assert catalog.division_of("01.11.1") == "01"
    assert catalog.division_of("68.20.2") == "68"
    assert catalog.division_of(None) is None
    assert catalog.division_of("not-a-code") is None
    assert catalog.section_of_okved("46.51") == "G"
    assert catalog.section_of_okved("64.19") == "K"
    assert catalog.section_of_okved("01.11") == "A"
    assert catalog.section_of_okved("99.00") == "U"
    assert catalog.section_of_okved("none") is None


def test_industry_text_inference() -> None:
    catalog = load_industry_catalog(INDUSTRIES)
    sections = catalog.infer_sections_from_text(
        "Логистическая компания столкнулась с перевозками и складскими ограничениями"
    )
    assert "H" in sections
