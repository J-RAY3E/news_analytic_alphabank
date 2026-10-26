from pathlib import Path

from app.contracts import NormalizedEvent
from app.products.catalog import load_product_catalog
from app.scoring.config import load_scoring_config
from app.services.products import select_offer

ROOT = Path(__file__).resolve().parents[2]
CATALOG = load_product_catalog(ROOT / "config" / "products.yaml")
CONFIG = load_scoring_config(ROOT / "config" / "scoring.yaml")


def make_event(macros: list[str]) -> NormalizedEvent:
    return NormalizedEvent.model_validate(
        {
            "event_id": "news:test-offer",
            "title": "Тестовое событие для подбора продукта",
            "summary": "Описание",
            "event_type": "MONETARY_POLICY",
            "sectors": ["ALL"],
            "macro_factors": macros,
            "source": {"source_id": "news:test-offer", "name": "Test"},
        }
    )


def test_catalog_has_large_business_set():
    assert len(CATALOG.products) == 16
    ids = {product.id for product in CATALOG.products}
    assert {"kredity", "garantii", "faktoring", "lizing", "depozity"} <= ids


def test_offer_for_key_rate_credit_company():
    company = {"company_id": "U_1", "CL_PRODUCT_LOA_MARK": 1}
    offer = select_offer(company, make_event(["KEY_RATE"]), CONFIG, CATALOG)
    assert offer is not None
    assert offer.id == "kredity"
    assert offer.url.startswith("https://")


def test_no_offer_without_macro_factors():
    company = {"company_id": "U_1", "CL_PRODUCT_LOA_MARK": 1}
    assert select_offer(company, make_event([]), CONFIG, CATALOG) is None


def test_no_offer_when_product_not_applicable():
    # COMMODITY_PRICE only maps to leasing, which the company does not use.
    company = {"company_id": "U_1", "CL_PRODUCT_RKO_MARK": 1}
    assert select_offer(company, make_event(["COMMODITY_PRICE"]), CONFIG, CATALOG) is None


def test_exporter_gets_ved_product_on_fx_event():
    exporter = {"company_id": "U_1", "is_exporter": True}
    offer = select_offer(exporter, make_event(["FX_RATE"]), CONFIG, CATALOG)
    assert offer is not None
    assert offer.id in {
        "mezhdunarodnye_raschety",
        "konvertaciya",
        "valyutny_kontrol",
        "hedzhirovanie",
        "bivalyut_depozit",
    }
