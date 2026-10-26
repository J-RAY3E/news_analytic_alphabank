from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.contracts import EventType, MacroFactor, Role


class WeightSet(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sector_match: float = Field(ge=0.0, le=1.0)
    supply_chain_exposure: float = Field(ge=0.0, le=1.0)
    product_match: float = Field(ge=0.0, le=1.0)
    geo_match: float = Field(ge=0.0, le=1.0)
    scale_weight: float = Field(ge=0.0, le=1.0)
    recency: float = Field(ge=0.0, le=1.0)
    event_quality: float = Field(default=0.0, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def weights_sum_to_one(self) -> WeightSet:
        total = sum(self.model_dump().values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"scoring weights must sum to 1.0, got {total}")
        return self


class SectorRules(BaseModel):
    model_config = ConfigDict(extra="forbid")

    exact_division: float = Field(ge=0.0, le=1.0)
    same_section: float = Field(ge=0.0, le=1.0)
    unknown: float = Field(ge=0.0, le=1.0)


class SupplyChainRules(BaseModel):
    model_config = ConfigDict(extra="forbid")

    counterparty_share_cap: float = Field(gt=0.0, le=1.0)
    min_share: float = Field(ge=0.0, le=1.0)
    all_sectors: float = Field(ge=0.0, le=1.0)


class ProductRules(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default: float = Field(ge=0.0, le=1.0)
    factor_features: dict[MacroFactor, dict[str, float]]

    @model_validator(mode="after")
    def feature_weights_valid(self) -> ProductRules:
        for factor, features in self.factor_features.items():
            if not features:
                raise ValueError(f"empty feature mapping for {factor.value}")
            for name, weight in features.items():
                if not 0.0 < weight <= 1.0:
                    raise ValueError(
                        f"feature weight for {factor.value}/{name} must be in (0, 1]"
                    )
        return self


class GeoRules(BaseModel):
    model_config = ConfigDict(extra="forbid")

    region_exact: float = Field(ge=0.0, le=1.0)
    country_in_fts: float = Field(ge=0.0, le=1.0)
    country_domestic: float = Field(ge=0.0, le=1.0)
    no_geo: float = Field(ge=0.0, le=1.0)
    unknown: float = Field(ge=0.0, le=1.0)
    domestic_country: str = "Россия"


class ScaleBand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min: float = Field(ge=0.0)
    value: float = Field(ge=0.0, le=1.0)
    label: str


class ScaleRules(BaseModel):
    model_config = ConfigDict(extra="forbid")

    aggregation: Literal["max", "mean"]
    missing: float = Field(ge=0.0, le=1.0)
    revenue_bands: list[ScaleBand]
    employee_bands: list[ScaleBand]

    @model_validator(mode="after")
    def bands_sorted_desc(self) -> ScaleRules:
        for name in ("revenue_bands", "employee_bands"):
            bands = getattr(self, name)
            if not bands:
                raise ValueError(f"{name} must not be empty")
            mins = [band.min for band in bands]
            if mins != sorted(mins, reverse=True):
                raise ValueError(f"{name} must be sorted by min descending")
        return self


class RecencyRules(BaseModel):
    model_config = ConfigDict(extra="forbid")

    half_life_days: float = Field(gt=0.0)
    max_age_days: float = Field(gt=0.0)
    missing: float = Field(ge=0.0, le=1.0)
    future: float = Field(ge=0.0, le=1.0)


class EventQualityRules(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_reliability: float = Field(default=0.7, ge=0.0, le=1.0)
    noise_penalty: float = Field(default=1.0, ge=0.0, le=2.0)
    speculation_penalty: float = Field(default=0.3, ge=0.0, le=2.0)
    generic_all_sectors_penalty: float = Field(default=0.0, ge=0.0, le=2.0)
    source_reliability: dict[str, float] = Field(default_factory=dict)


class UrgencyRules(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_score: float = Field(default=0.7, ge=0.0, le=1.0)


class RoleRules(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tie_break_tolerance: float = Field(ge=0.0, le=1.0)
    preferences: dict[Role, list[EventType]]


class ScoringConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    weights: WeightSet
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)
    sector: SectorRules
    supply_chain: SupplyChainRules
    product: ProductRules
    geo: GeoRules
    scale: ScaleRules
    recency: RecencyRules
    external_sources: list[str] = Field(default_factory=list)
    event_quality: EventQualityRules = EventQualityRules()
    urgency: UrgencyRules = UrgencyRules()
    roles: RoleRules


@lru_cache
def load_scoring_config(path: str | Path) -> ScoringConfig:
    resolved = Path(path).resolve()
    with resolved.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"scoring config must be a mapping: {resolved}")
    return ScoringConfig.model_validate(payload)
