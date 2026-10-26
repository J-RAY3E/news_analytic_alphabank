from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from typing import Any

from app.contracts import (
    MacroFactor,
    NormalizedEvent,
    RelevanceFactor,
    RelevanceScore,
)
from app.data.industries import IndustryCatalog
from app.scoring.config import ScoringConfig

FACTOR_LABELS = {
    "sector_match": "Совпадение отрасли",
    "supply_chain_exposure": "Экспозиция цепочки поставок",
    "product_match": "Соответствие продуктам банка",
    "geo_match": "Географическое совпадение",
    "scale_weight": "Масштаб компании",
    "recency": "Актуальность новости",
    "event_quality": "Качество источника и сигнала",
}

MACRO_LABELS = {
    MacroFactor.KEY_RATE: "ключевая ставка",
    MacroFactor.INFLATION: "инфляция",
    MacroFactor.FX_RATE: "валютный курс",
    MacroFactor.BOND_YIELD: "доходность облигаций",
    MacroFactor.COMMODITY_PRICE: "сырьевые цены",
    MacroFactor.DEMAND: "потребительский спрос",
    MacroFactor.SUPPLY_CHAIN: "цепочки поставок",
    MacroFactor.REGULATION: "регулирование",
    MacroFactor.TAX: "налоги",
    MacroFactor.SANCTIONS: "санкции",
    MacroFactor.LABOR_COST: "стоимость труда",
    MacroFactor.CREDIT_ACCESS: "доступность кредита",
}

FEATURE_LABELS = {
    "CL_PRODUCT_RKO_MARK": "РКО",
    "CL_PRODUCT_GAR_MARK": "гарантии",
    "CL_PRODUCT_LOA_MARK": "кредиты",
    "CL_PRODUCT_LEA_MARK": "лизинг",
    "CL_PRODUCT_DEP_MARK": "депозиты",
    "CL_PRODUCT_ZPP_MARK": "зарплатный проект",
    "FACTORING_MARK": "факторинг",
    "FTS_FLAG": "внешнеэкономическая деятельность",
}

DIVISION_RE = re.compile(r"^\d{1,2}$")


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return []


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return str(value).strip().casefold() in {"true", "yes", "1"}


def _json_map(value: Any) -> dict[str, float]:
    if isinstance(value, dict):
        return {str(key): float(item) for key, item in value.items()}
    if isinstance(value, str) and value.strip():
        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            return {}
        if isinstance(loaded, dict):
            return {str(key): float(item) for key, item in loaded.items()}
    return {}


def parse_event_sectors(
    event: NormalizedEvent, catalog: IndustryCatalog
) -> tuple[bool, set[str], set[str]]:
    all_sectors = False
    divisions: set[str] = set()
    sections: set[str] = set()
    for token in event.sectors:
        cleaned = str(token).strip().upper()
        if cleaned in {"ALL", "ВСЕ", "*"}:
            all_sectors = True
            continue
        if len(cleaned) == 1 and cleaned in catalog.sections:
            sections.add(cleaned)
            continue
        if DIVISION_RE.match(cleaned):
            division = f"{int(cleaned):02d}"
            divisions.add(division)
            section = catalog.section_of_division(division)
            if section:
                sections.add(section)
            continue
        division = catalog.division_of(cleaned)
        if division:
            divisions.add(division)
            section = catalog.section_of_division(division)
            if section:
                sections.add(section)
        else:
            inferred = catalog.infer_sections_from_text(cleaned)
            sections.update(inferred)
    return all_sectors, divisions, sections


def sector_match(
    company: dict[str, Any],
    event: NormalizedEvent,
    config: ScoringConfig,
    catalog: IndustryCatalog,
) -> tuple[float, str]:
    all_sectors, event_divisions, event_sections = parse_event_sectors(event, catalog)
    if all_sectors:
        return 1.0, "Событие затрагивает все отрасли экономики"
    company_division = catalog.division_of(company.get("okved_code")) or company.get(
        "okved_division"
    )
    company_section = company.get("okved_section") or catalog.section_of_division(
        company_division
    )
    if company_division and company_division in event_divisions:
        label = catalog.section_label(company_section)
        return (
            config.sector.exact_division,
            f"Точное совпадение отрасли: {label}",
        )
    if company_section and company_section in event_sections:
        label = catalog.section_label(company_section)
        return (
            config.sector.same_section,
            f"Событие затрагивает смежную отрасль: {label}",
        )
    return config.sector.unknown, "Отрасль компании не затронута событием"


def supply_chain_exposure(
    event: NormalizedEvent,
    config: ScoringConfig,
    catalog: IndustryCatalog,
    graph_row: dict[str, Any] | None,
) -> tuple[float, str]:
    if not graph_row or not _as_bool(graph_row.get("has_payment_activity")):
        return 0.0, "Нет данных о платежных связях компании"
    all_sectors, event_divisions, event_sections = parse_event_sectors(event, catalog)
    if all_sectors:
        return (
            config.supply_chain.all_sectors,
            "Событие затрагивает все отрасли, компания имеет платежные связи",
        )
    exposed = set(event_divisions)
    for section in event_sections:
        bounds = catalog.division_ranges.get(section)
        if bounds:
            exposed.update(f"{value:02d}" for value in range(bounds[0], bounds[1] + 1))
    if not exposed:
        return 0.0, "В событии не выделены отрасли контрагентов"

    supplier = _json_map(graph_row.get("supplier_division_shares"))
    client = _json_map(graph_row.get("client_division_shares"))
    supplier_hits = {
        division: share
        for division, share in supplier.items()
        if division in exposed and share >= config.supply_chain.min_share
    }
    client_hits = {
        division: share
        for division, share in client.items()
        if division in exposed and share >= config.supply_chain.min_share
    }
    supplier_value = sum(supplier_hits.values())
    client_value = sum(client_hits.values())
    value = min(
        config.supply_chain.counterparty_share_cap,
        max(supplier_value, client_value),
    )
    if value <= 0:
        return 0.0, "Контрагенты компании не представлены в затронутых отраслях"
    side = "поставщиков" if supplier_value >= client_value else "клиентов"
    hits = supplier_hits if supplier_value >= client_value else client_hits
    top_division, top_share = max(hits.items(), key=lambda item: item[1])
    label = catalog.section_label(catalog.section_of_division(top_division))
    return (
        round(value, 6),
        f"Доля {side} в отрасли «{label}»: {top_share:.0%}",
    )


def _feature_present(company: dict[str, Any], feature: str) -> bool:
    if feature == "FTS_FLAG":
        return _as_bool(company.get("is_exporter")) or _as_bool(company.get("fts_flag"))
    if _as_bool(company.get(feature)):
        return True
    flags = company.get("product_flags")
    if hasattr(flags, "tolist"):
        flags = flags.tolist()
    if isinstance(flags, str):
        flags = [part.strip() for part in flags.replace(";", ",").split(",")]
    if isinstance(flags, (list, tuple, set)):
        return feature in {str(item).strip() for item in flags}
    return False


def product_match(
    company: dict[str, Any],
    event: NormalizedEvent,
    config: ScoringConfig,
) -> tuple[float, str]:
    if not event.macro_factors:
        return config.product.default, "В событии не выделены макрофакторы"
    best_value = 0.0
    best_factor: MacroFactor | None = None
    best_features: list[str] = []
    for factor in event.macro_factors:
        mapping = config.product.factor_features.get(factor, {})
        if not mapping:
            continue
        max_weight = max(mapping.values())
        present = [feature for feature in mapping if _feature_present(company, feature)]
        coverage = min(1.0, sum(mapping[feature] for feature in present) / max_weight)
        if coverage > best_value:
            best_value = coverage
            best_factor = factor
            best_features = present
    if best_value <= 0 or best_factor is None:
        return (
            config.product.default,
            "У компании нет продуктов, чувствительных к событию",
        )
    labels = ", ".join(FEATURE_LABELS.get(feature, feature) for feature in best_features)
    return (
        round(best_value, 6),
        f"Событие влияет на «{MACRO_LABELS.get(best_factor, best_factor.value)}»; "
        f"у компании есть {labels}",
    )


def geo_match(
    company: dict[str, Any],
    event: NormalizedEvent,
    config: ScoringConfig,
    catalog: IndustryCatalog,
) -> tuple[float, str]:
    company_region = str(company.get("region") or "").strip().casefold()
    company_city = str(company.get("city") or "").strip().casefold()
    event_regions = {region.strip().casefold() for region in event.regions if region.strip()}
    event_countries = {country.strip().casefold() for country in event.countries if country.strip()}
    fts_countries = {country.casefold() for country in _as_list(company.get("fts_countries"))}
    domestic = config.geo.domestic_country.casefold()
    is_domestic = domestic in event_countries or bool(
        event_countries & {"россия", "russia"}
    )
    foreign_match = bool(event_countries & fts_countries)

    if event_regions:
        if company_region and (company_region in event_regions or company_city in event_regions):
            return config.geo.region_exact, "Компания находится в регионе события"
        if foreign_match:
            return config.geo.country_in_fts, "Страна события совпадает с географией ВЭД компании"
        return config.geo.unknown, "Компания не представлена в регионе события"

    if not company_region and not fts_countries:
        return config.geo.unknown, "География компании не определена"
    if foreign_match:
        return config.geo.country_in_fts, "Страна события совпадает с географией ВЭД компании"
    if is_domestic:
        return config.geo.country_domestic, "Событие общероссийское"
    if not event_countries:
        return config.geo.no_geo, "География события не определена"
    return config.geo.unknown, "География события не совпадает с компанией"


def scale_weight(
    company: dict[str, Any], config: ScoringConfig
) -> tuple[float, str]:
    revenue_value = company.get("scale_value")
    values: list[float] = []
    labels: list[str] = []
    if revenue_value is not None and not (
        isinstance(revenue_value, float) and math.isnan(revenue_value)
    ):
        values.append(float(revenue_value))
        labels.append(str(company.get("revenue_band") or "выручка"))
    lower_bound = company.get("employees_lower_bound")
    if lower_bound is not None and not (
        isinstance(lower_bound, float) and math.isnan(lower_bound)
    ):
        band = None
        for candidate in config.scale.employee_bands:
            if float(lower_bound) >= candidate.min:
                band = candidate
                break
        if band is not None:
            values.append(band.value)
            labels.append(f"{band.label} сотрудников")
    if not values:
        return config.scale.missing, "Масштаб компании не определен"
    if config.scale.aggregation == "mean":
        value = sum(values) / len(values)
    else:
        value = max(values)
    return round(value, 6), "Масштаб: " + ", ".join(labels)


def recency(
    event: NormalizedEvent,
    config: ScoringConfig,
    now: datetime | None = None,
) -> tuple[float, str]:
    published = event.source.published_at
    if published is None:
        return config.recency.missing, "Дата публикации не указана"
    current = now or datetime.now(timezone.utc)
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    age_days = (current - published).total_seconds() / 86400.0
    if age_days < 0:
        return config.recency.future, "Новость опубликована в будущем"
    if age_days > config.recency.max_age_days:
        return 0.0, f"Новость устарела: {age_days:.0f} дней"
    value = math.exp(-math.log(2) * age_days / config.recency.half_life_days)
    return (
        round(min(max(value, 0.0), 1.0), 6),
        f"Опубликовано {age_days:.1f} дней назад",
    )


def event_quality(
    event: NormalizedEvent, config: ScoringConfig
) -> tuple[float, str]:
    rules = config.event_quality
    reliability = rules.source_reliability.get(
        event.source.name, rules.default_reliability
    )
    value = reliability
    value -= event.noise_score * rules.noise_penalty
    if event.is_speculation:
        value -= rules.speculation_penalty
    if event.sectors and all(str(s).strip().upper() in {"ALL", "ВСЕ", "*"} for s in event.sectors):
        value -= rules.generic_all_sectors_penalty
    value = max(0.0, min(value, 1.0))
    notes = [f"Источник: {event.source.name} (надёжность {reliability:.2f})"]
    if event.noise_score > 0.3:
        notes.append(f"шум {event.noise_score:.2f}")
    if event.is_speculation:
        notes.append("спекулятивно")
    return round(value, 6), "; ".join(notes)


def score_event(
    company: dict[str, Any],
    event: NormalizedEvent,
    config: ScoringConfig,
    catalog: IndustryCatalog,
    graph_row: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> RelevanceScore:
    sector_value, sector_explanation = sector_match(company, event, config, catalog)
    chain_value, chain_explanation = supply_chain_exposure(event, config, catalog, graph_row)
    product_value, product_explanation = product_match(company, event, config)
    geo_value, geo_explanation = geo_match(company, event, config, catalog)
    scale_value, scale_explanation = scale_weight(company, config)
    recency_value, recency_explanation = recency(event, config, now=now)
    quality_value, quality_explanation = event_quality(event, config)

    raw = [
        ("sector_match", sector_value, config.weights.sector_match, sector_explanation),
        (
            "supply_chain_exposure",
            chain_value,
            config.weights.supply_chain_exposure,
            chain_explanation,
        ),
        ("product_match", product_value, config.weights.product_match, product_explanation),
        ("geo_match", geo_value, config.weights.geo_match, geo_explanation),
        ("scale_weight", scale_value, config.weights.scale_weight, scale_explanation),
        ("recency", recency_value, config.weights.recency, recency_explanation),
        ("event_quality", quality_value, config.weights.event_quality, quality_explanation),
    ]
    factors = [
        RelevanceFactor(
            name=name,
            value=round(value, 6),
            weight=weight,
            contribution=round(value * weight, 6),
            explanation=explanation,
        )
        for name, value, weight, explanation in raw
    ]
    total = round(sum(factor.contribution for factor in factors), 6)
    return RelevanceScore(
        score=max(0.0, min(total, 1.0)),
        factors=factors,
        config_version=config.version,
    )
