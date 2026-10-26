from __future__ import annotations

from typing import Any

from app.contracts import MacroFactor, NormalizedEvent, ProductOffer
from app.products.catalog import ProductCatalog
from app.scoring.config import ScoringConfig

MACRO_LABELS = {
    MacroFactor.KEY_RATE: "ключевая ставка",
    MacroFactor.INFLATION: "инфляция",
    MacroFactor.FX_RATE: "курс рубля",
    MacroFactor.BOND_YIELD: "доходность облигаций",
    MacroFactor.COMMODITY_PRICE: "сырьевые цены",
    MacroFactor.DEMAND: "спрос",
    MacroFactor.SUPPLY_CHAIN: "цепочки поставок",
    MacroFactor.REGULATION: "регулирование",
    MacroFactor.TAX: "налоги",
    MacroFactor.SANCTIONS: "санкции",
    MacroFactor.LABOR_COST: "стоимость труда",
    MacroFactor.CREDIT_ACCESS: "доступ к кредиту",
}


def _has_feature(company: dict[str, Any], feature: str) -> bool:
    if feature == "FTS_FLAG":
        return bool(company.get("is_exporter")) or bool(company.get("fts_flag"))
    value = company.get(feature)
    try:
        if float(value) > 0:
            return True
    except (TypeError, ValueError):
        if bool(value):
            return True
    flags = company.get("product_flags")
    if hasattr(flags, "tolist"):
        flags = flags.tolist()
    if isinstance(flags, str):
        flags = [part.strip() for part in flags.replace(";", ",").split(",")]
    if isinstance(flags, (list, tuple, set)):
        return feature in {str(item).strip() for item in flags}
    return False


def select_offer(
    company: dict[str, Any],
    event: NormalizedEvent,
    config: ScoringConfig,
    catalog: ProductCatalog,
) -> ProductOffer | None:
    """Pick at most one relevant product offer for a company × event (FAQ 50).

    Relevance = the event's macro factors intersect the product's `when_macro`
    (and, for flag-backed products, the company actually uses/needs the feature).
    """
    event_macros = {factor.value for factor in event.macro_factors}
    if not event_macros:
        return None

    best = None
    best_score = 0.0
    best_macros: list[str] = []
    for product in catalog.products:
        triggers = sorted(set(product.when_macro) & event_macros)
        if not triggers:
            continue
        if product.features and not any(
            _has_feature(company, feature) for feature in product.features
        ):
            continue
        score = 0.0
        for macro in triggers:
            try:
                factor = MacroFactor(macro)
            except ValueError:
                continue
            mapping = config.product.factor_features.get(factor, {})
            for feature in product.features:
                score = max(score, mapping.get(feature, 0.0))
        if not product.features:
            score = 0.5
        if score > best_score:
            best_score = score
            best = product
            best_macros = triggers

    if best is None:
        return None

    labels = [
        MACRO_LABELS.get(MacroFactor(macro), macro)
        for macro in best_macros
        if macro in {factor.value for factor in MacroFactor}
    ]
    reason = "Релевантно событию: " + (", ".join(labels) if labels else "рыночная ситуация")
    return ProductOffer(
        id=best.id,
        name=best.name,
        short=best.short,
        url=best.url,
        reason=reason,
    )
