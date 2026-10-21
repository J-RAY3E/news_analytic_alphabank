from pathlib import Path

import pandas as pd
import pytest

from app.data.industries import load_industry_catalog
from app.data.profiler import (
    build_company_profiles,
    clean_text,
    parse_countries,
    numeric_flag,
    normalize_okved,
)
from app.scoring.config import load_scoring_config

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def catalog():
    return load_industry_catalog(ROOT / "config" / "industries.yaml")


@pytest.fixture(scope="module")
def scoring():
    return load_scoring_config(ROOT / "config" / "scoring.yaml")


def raw_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "SYNTHETIC_U": "U_1",
                "ORG_TYPE": "КОММ_ОРГ",
                "OKFS_NAME": "ЧАСТНАЯ СОБСТВЕННОСТЬ",
                "COMPANY_AGE_YEARS_GRADATION": "16-25",
                "ECO_MARK_LABEL": "Оптимизация",
                "MAINOKVED_CODE": "46.51",
                "MAINOKVED_NAME": "Торговля оптовая компьютерами",
                "NEGATIVEMARK": 0,
                "AMOUNT_WORKERS_FNS_GRADATION": "Более 251",
                "AMOUNT_WORKERS_SPARK_GRADATION": "Более 251",
                "CL_TYPE": "CLOSE_CLIENT",
                "CL_PRODUCT_RKO_MARK": 1,
                "CL_PRODUCT_GAR_MARK": 0,
                "CL_PRODUCT_LOA_MARK": 1,
                "CL_PRODUCT_LEA_MARK": 0,
                "CL_PRODUCT_DEP_MARK": 1,
                "CL_PRODUCT_ZPP_MARK": 1,
                "FTS_FLAG": 1,
                "FTS_COUNTRY_NAME": "КИТАЙ, ТУРЦИЯ",
                "FACTORING_MARK": 0,
                "REVENUE_COMPANY": 20_000_000_000,
                "GROUP_ID": "group_1",
                "CITY": "г. Москва",
                "REGION": "Москва",
            },
            {
                "SYNTHETIC_U": "U_1",
                "ORG_TYPE": "КОММ_ОРГ",
                "OKFS_NAME": "ЧАСТНАЯ СОБСТВЕННОСТЬ",
                "COMPANY_AGE_YEARS_GRADATION": "16-25",
                "ECO_MARK_LABEL": "Оптимизация",
                "MAINOKVED_CODE": "46.51",
                "MAINOKVED_NAME": "Торговля оптовая компьютерами",
                "NEGATIVEMARK": 0,
                "AMOUNT_WORKERS_FNS_GRADATION": "Более 251",
                "AMOUNT_WORKERS_SPARK_GRADATION": "Более 251",
                "CL_TYPE": "CLOSE_CLIENT",
                "CL_PRODUCT_RKO_MARK": 1,
                "CL_PRODUCT_GAR_MARK": 0,
                "CL_PRODUCT_LOA_MARK": 1,
                "CL_PRODUCT_LEA_MARK": 0,
                "CL_PRODUCT_DEP_MARK": 1,
                "CL_PRODUCT_ZPP_MARK": 1,
                "FTS_FLAG": 1,
                "FTS_COUNTRY_NAME": "КИТАЙ, ТУРЦИЯ",
                "FACTORING_MARK": 0,
                "REVENUE_COMPANY": 10_000_000_000,
                "GROUP_ID": "group_1",
                "CITY": "г. Москва",
                "REGION": "Москва",
            },
            {
                "SYNTHETIC_U": "U_2",
                "ORG_TYPE": "КОММ_ОРГ",
                "OKFS_NAME": "ЧАСТНАЯ СОБСТВЕННОСТЬ",
                "COMPANY_AGE_YEARS_GRADATION": "4-7",
                "ECO_MARK_LABEL": "Рождение",
                "MAINOKVED_CODE": "41.20",
                "MAINOKVED_NAME": "Строительство жилых домов",
                "NEGATIVEMARK": 1,
                "AMOUNT_WORKERS_FNS_GRADATION": "16-100",
                "AMOUNT_WORKERS_SPARK_GRADATION": "16-100",
                "CL_TYPE": "PROSPECT",
                "CL_PRODUCT_RKO_MARK": 1,
                "CL_PRODUCT_GAR_MARK": 0,
                "CL_PRODUCT_LOA_MARK": 0,
                "CL_PRODUCT_LEA_MARK": 0,
                "CL_PRODUCT_DEP_MARK": 0,
                "CL_PRODUCT_ZPP_MARK": 0,
                "FTS_FLAG": 0,
                "FTS_COUNTRY_NAME": "",
                "FACTORING_MARK": 0,
                "REVENUE_COMPANY": 500_000_000,
                "GROUP_ID": "group_1",
                "CITY": "г. Казань",
                "REGION": "Республика Татарстан",
            },
        ]
    )


def test_text_and_country_helpers():
    assert clean_text("  ООО\xa0 Ромашка  ") == "ООО Ромашка"
    assert clean_text(float("nan")) == ""
    assert parse_countries("КИТАЙ, турция; КИТАЙ") == ["КИТАЙ", "ТУРЦИЯ"]
    assert numeric_flag("1.0") is True
    assert numeric_flag("0.0") is False
    assert normalize_okved(" 46.51 ") == "46.51"
    assert normalize_okved("bad") == ""


def test_build_company_profiles(catalog, scoring):
    result = build_company_profiles(raw_frame(), catalog, scoring)
    frame = result.companies
    assert len(frame) == 2
    assert result.quality["duplicates_removed"] == 1
    row = frame.set_index("company_id").loc["U_1"]
    assert row["okved_section"] == "G"
    assert row["industry_label"] == "Торговля оптовая и розничная"
    assert row["revenue_rub"] == 20_000_000_000
    assert row["target_segment"] == "LARGE_TARGET"
    assert row["is_exporter"] is True or bool(row["is_exporter"]) is True
    assert "CL_PRODUCT_LOA_MARK" in list(row["product_flags"])
    assert "Кредиты" in list(row["product_labels"])
    assert int(row["group_size"]) == 2
    assert row["region"] == "Москва"
    assert result.quality["target_companies_revenue_ge_15bn"] == 1
    assert result.quality["product_flag_counts"]["CL_PRODUCT_LOA_MARK"] == 1


def test_unknown_okved_is_graceful(catalog, scoring):
    frame = raw_frame().iloc[[2]].copy()
    frame.loc[:, "MAINOKVED_CODE"] = "???"
    frame.loc[:, "MAINOKVED_NAME"] = ""
    result = build_company_profiles(frame, catalog, scoring)
    row = result.companies.iloc[0]
    assert bool(row["missing_okved"]) is True
    assert bool(row["unknown_industry"]) is True
    assert row["industry_label"] == "Неизвестная отрасль"
