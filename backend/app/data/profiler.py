from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable

import pandas as pd

from app.data.industries import IndustryCatalog
from app.scoring.config import ScoringConfig

PRODUCT_FLAGS: dict[str, str] = {
    "CL_PRODUCT_RKO_MARK": "РКО",
    "CL_PRODUCT_GAR_MARK": "Гарантии",
    "CL_PRODUCT_LOA_MARK": "Кредиты",
    "CL_PRODUCT_LEA_MARK": "Лизинг",
    "CL_PRODUCT_DEP_MARK": "Депозиты",
    "CL_PRODUCT_ZPP_MARK": "Зарплатный проект",
    "FACTORING_MARK": "Факторинг",
}

CREDIT_FLAGS = (
    "CL_PRODUCT_LOA_MARK",
    "CL_PRODUCT_LEA_MARK",
    "CL_PRODUCT_GAR_MARK",
    "FACTORING_MARK",
)

EMPLOYEE_LOWER_BOUND = {
    "менее 15": 0,
    "16-100": 16,
    "101-250": 101,
    "более 251": 251,
}

AGE_LOWER_BOUND = {
    "0-3": 0,
    "4-7": 4,
    "8-15": 8,
    "16-25": 16,
}

WHITESPACE_RE = re.compile(r"\s+")


def clean_text(value: Any) -> str:
    if value is None or value is pd.NA:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    text = str(value).replace("\xa0", " ").strip()
    if text.casefold() in {"nan", "none", "<na>"}:
        return ""
    return WHITESPACE_RE.sub(" ", text)


def parse_countries(value: Any) -> list[str]:
    text = clean_text(value)
    if not text:
        return []
    parts = re.split(r"[,;/|]+", text)
    countries: list[str] = []
    seen: set[str] = set()
    for part in parts:
        country = clean_text(part).upper()
        if country and country not in seen:
            seen.add(country)
            countries.append(country)
    return countries


def numeric_flag(value: Any) -> bool:
    text = clean_text(value)
    if not text:
        return False
    try:
        return float(text) > 0
    except ValueError:
        return text.casefold() in {"true", "yes", "y", "1"}


def band_for_value(value: float | int | None, bands: Iterable[Any]) -> Any | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    number = float(value)
    for band in bands:
        if number >= float(band.min):
            return band
    return None


def normalize_okved(code: Any) -> str:
    text = clean_text(code)
    match = re.match(r"^(\d{1,2}(?:\.\d+)*)", text)
    return match.group(1) if match else ""


def employee_lower_bound(band: Any) -> int | None:
    return EMPLOYEE_LOWER_BOUND.get(clean_text(band).casefold())


def age_lower_bound(band: Any) -> int | None:
    return AGE_LOWER_BOUND.get(clean_text(band).casefold())


@dataclass(frozen=True)
class ProfileBuildResult:
    companies: pd.DataFrame
    quality: dict[str, Any]


def build_company_profiles(
    raw: pd.DataFrame,
    catalog: IndustryCatalog,
    scoring: ScoringConfig,
) -> ProfileBuildResult:
    frame = raw.copy()
    frame.columns = [column.strip() for column in frame.columns]
    frame["SYNTHETIC_U"] = frame["SYNTHETIC_U"].map(clean_text)
    frame = frame[frame["SYNTHETIC_U"] != ""]
    frame["REVENUE_COMPANY"] = pd.to_numeric(frame["REVENUE_COMPANY"], errors="coerce")

    duplicates_removed = int(frame.duplicated(subset=["SYNTHETIC_U"]).sum())
    frame = frame.sort_values(
        ["SYNTHETIC_U", "REVENUE_COMPANY"], ascending=[True, False], na_position="last"
    ).drop_duplicates(subset=["SYNTHETIC_U"], keep="first")

    frame["okved_code"] = frame["MAINOKVED_CODE"].map(normalize_okved)
    frame["okved_name"] = frame["MAINOKVED_NAME"].map(clean_text)
    frame["okved_division"] = frame["okved_code"].map(catalog.division_of)
    frame["okved_section"] = frame["okved_code"].map(catalog.section_of_okved)
    frame["industry_label"] = frame["okved_section"].map(catalog.section_label)

    frame["region"] = frame["REGION"].map(clean_text).replace("", "Не указан")
    frame["city"] = frame["CITY"].map(clean_text).replace("", "Не указан")
    frame["client_type"] = frame["CL_TYPE"].map(clean_text)
    frame["org_type"] = frame["ORG_TYPE"].map(clean_text)
    frame["ownership_form"] = frame["OKFS_NAME"].map(clean_text)
    frame["eco_mark"] = frame["ECO_MARK_LABEL"].map(clean_text)
    frame["has_negative_mark"] = frame["NEGATIVEMARK"].map(numeric_flag)
    frame["age_band"] = frame["COMPANY_AGE_YEARS_GRADATION"].map(clean_text)
    frame["age_lower_bound"] = frame["age_band"].map(age_lower_bound)
    frame["employees_band"] = frame["AMOUNT_WORKERS_FNS_GRADATION"].map(clean_text).replace(
        "", "Не указан"
    )
    frame["employees_lower_bound"] = frame["employees_band"].map(employee_lower_bound)
    frame["revenue_rub"] = frame["REVENUE_COMPANY"].fillna(0.0).clip(lower=0.0)
    frame["has_revenue"] = frame["REVENUE_COMPANY"].notna()

    revenue_band = frame["revenue_rub"].map(
        lambda value: band_for_value(value, scoring.scale.revenue_bands)
    )
    frame["revenue_band"] = revenue_band.map(lambda band: band.label if band else "Не указан")
    frame["scale_value"] = revenue_band.map(lambda band: band.value if band else scoring.scale.missing)

    for flag in PRODUCT_FLAGS:
        frame[flag] = frame[flag].map(numeric_flag)
    frame["product_flags"] = frame.apply(
        lambda row: [flag for flag in PRODUCT_FLAGS if bool(row[flag])], axis=1
    )
    frame["product_labels"] = frame["product_flags"].map(
        lambda flags: [PRODUCT_FLAGS[flag] for flag in flags]
    )
    frame["product_count"] = frame["product_flags"].map(len)
    frame["has_credit_products"] = frame["product_flags"].map(
        lambda flags: any(flag in CREDIT_FLAGS for flag in flags)
    )

    frame["fts_countries"] = frame["FTS_COUNTRY_NAME"].map(parse_countries)
    frame["fts_flag"] = frame["FTS_FLAG"].map(numeric_flag)
    frame["is_exporter"] = frame["fts_flag"] | frame["fts_countries"].map(bool)

    frame["group_id"] = frame["GROUP_ID"].map(clean_text)
    group_sizes = (
        frame.loc[frame["group_id"] != ""].groupby("group_id")["SYNTHETIC_U"].transform("count")
    )
    frame["group_size"] = group_sizes.reindex(frame.index).fillna(1).astype(int)

    frame["target_segment"] = (frame["revenue_rub"] >= 15_000_000_000).map(
        {True: "LARGE_TARGET", False: "BELOW_TARGET"}
    )
    short_okved = frame["okved_name"].str.slice(0, 70)
    frame["display_name"] = [
        f"{company_id} · {name}" if name else f"Компания {company_id}"
        for company_id, name in zip(frame["SYNTHETIC_U"], short_okved)
    ]

    frame["missing_okved"] = frame["okved_code"] == ""
    frame["missing_city"] = frame["city"] == "Не указан"
    frame["unknown_industry"] = frame["okved_section"].isna()

    output = pd.DataFrame(
        {
            "company_id": frame["SYNTHETIC_U"],
            "display_name": frame["display_name"],
            "org_type": frame["org_type"],
            "ownership_form": frame["ownership_form"],
            "eco_mark": frame["eco_mark"],
            "age_band": frame["age_band"],
            "age_lower_bound": frame["age_lower_bound"],
            "okved_code": frame["okved_code"],
            "okved_name": frame["okved_name"],
            "okved_division": frame["okved_division"],
            "okved_section": frame["okved_section"],
            "industry_label": frame["industry_label"],
            "employees_band": frame["employees_band"],
            "employees_lower_bound": frame["employees_lower_bound"],
            "client_type": frame["client_type"],
            "product_flags": frame["product_flags"],
            "product_labels": frame["product_labels"],
            "product_count": frame["product_count"],
            "has_credit_products": frame["has_credit_products"],
            "fts_flag": frame["fts_flag"],
            "is_exporter": frame["is_exporter"],
            "fts_countries": frame["fts_countries"],
            "has_negative_mark": frame["has_negative_mark"],
            "revenue_rub": frame["revenue_rub"],
            "has_revenue": frame["has_revenue"],
            "revenue_band": frame["revenue_band"],
            "scale_value": frame["scale_value"],
            "target_segment": frame["target_segment"],
            "group_id": frame["group_id"],
            "group_size": frame["group_size"],
            "city": frame["city"],
            "region": frame["region"],
            "missing_okved": frame["missing_okved"],
            "missing_city": frame["missing_city"],
            "unknown_industry": frame["unknown_industry"],
        }
    ).reset_index(drop=True)

    quality = build_quality_report(raw, output, duplicates_removed)
    return ProfileBuildResult(companies=output, quality=quality)


def build_quality_report(
    raw: pd.DataFrame, companies: pd.DataFrame, duplicates_removed: int
) -> dict[str, Any]:
    total = len(companies)
    target = int((companies["target_segment"] == "LARGE_TARGET").sum())
    sections = companies["okved_section"].fillna("UNKNOWN").value_counts()
    flags = {
        flag: int(companies["product_flags"].map(lambda values: flag in values).sum())
        for flag in PRODUCT_FLAGS
    }
    return {
        "raw_rows": int(len(raw)),
        "duplicates_removed": duplicates_removed,
        "companies": total,
        "target_companies_revenue_ge_15bn": target,
        "share_target": round(target / total, 6) if total else 0.0,
        "missing_okved": int(companies["missing_okved"].sum()),
        "unknown_industry": int(companies["unknown_industry"].sum()),
        "missing_city": int(companies["missing_city"].sum()),
        "missing_region": int((companies["region"] == "Не указан").sum()),
        "exporters": int(companies["is_exporter"].sum()),
        "companies_in_groups": int((companies["group_id"] != "").sum()),
        "unique_groups": int(companies.loc[companies["group_id"] != "", "group_id"].nunique()),
        "section_distribution": {str(key): int(value) for key, value in sections.items()},
        "product_flag_counts": flags,
        "revenue_rub": {
            "min": float(companies["revenue_rub"].min()),
            "median": float(companies["revenue_rub"].median()),
            "mean": float(companies["revenue_rub"].mean()),
            "max": float(companies["revenue_rub"].max()),
        },
    }
