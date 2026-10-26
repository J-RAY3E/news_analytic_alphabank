from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClaimType(str, Enum):
    FACT = "FACT"
    BANK_VIEW = "BANK_VIEW"
    AI_INFERENCE = "AI_INFERENCE"
    HYPOTHESIS = "HYPOTHESIS"


class Impact(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class EventType(str, Enum):
    MONETARY_POLICY = "MONETARY_POLICY"
    FX = "FX"
    REGULATION = "REGULATION"
    SANCTIONS = "SANCTIONS"
    LOGISTICS = "LOGISTICS"
    COMMODITIES = "COMMODITIES"
    DEMAND = "DEMAND"
    COMPETITION = "COMPETITION"
    TAX = "TAX"
    LABOR = "LABOR"
    TECHNOLOGY = "TECHNOLOGY"
    OTHER = "OTHER"


class MacroFactor(str, Enum):
    KEY_RATE = "KEY_RATE"
    INFLATION = "INFLATION"
    FX_RATE = "FX_RATE"
    BOND_YIELD = "BOND_YIELD"
    COMMODITY_PRICE = "COMMODITY_PRICE"
    DEMAND = "DEMAND"
    SUPPLY_CHAIN = "SUPPLY_CHAIN"
    REGULATION = "REGULATION"
    TAX = "TAX"
    SANCTIONS = "SANCTIONS"
    LABOR_COST = "LABOR_COST"
    CREDIT_ACCESS = "CREDIT_ACCESS"


class Sentiment(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"
    MIXED = "MIXED"


class RiskOpportunity(str, Enum):
    RISK = "RISK"
    OPPORTUNITY = "OPPORTUNITY"
    BOTH = "BOTH"
    NEUTRAL = "NEUTRAL"


class Role(str, Enum):
    CEO = "CEO"
    CFO = "CFO"
    TREASURER = "TREASURER"
    CHIEF_ACCOUNTANT = "CHIEF_ACCOUNTANT"
    OTHER = "OTHER"


class SourceRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    url: str | None = None
    published_at: datetime | None = None
    page: int | None = Field(default=None, ge=1)
    language: str = "ru"


class Figure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1)
    value: float | str
    unit: str | None = None


class NormalizedEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(pattern=r"^news:[A-Za-z0-9_.-]+$")
    title: str = Field(min_length=3, max_length=500)
    summary: str = Field(default="", max_length=4000)
    raw_text: str = Field(default="", max_length=100_000)
    event_type: EventType
    sectors: list[str] = Field(default_factory=list)
    regions: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    macro_factors: list[MacroFactor] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list)
    figures: list[Figure] = Field(default_factory=list)
    sentiment: Sentiment = Sentiment.NEUTRAL
    risk_opportunity: RiskOpportunity = RiskOpportunity.NEUTRAL
    is_speculation: bool = False
    noise_score: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    source: SourceRef
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("sectors", "regions", "countries", "entities")
    @classmethod
    def dedupe_preserve_order(cls, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            cleaned = value.strip()
            key = cleaned.casefold()
            if cleaned and key not in seen:
                seen.add(key)
                result.append(cleaned)
        return result


class EvidenceClaim(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=4000)
    type: ClaimType
    source_ids: list[str] = Field(default_factory=list)
    company_features: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    impact: Impact = Impact.MEDIUM

    @field_validator("source_ids", "company_features")
    @classmethod
    def unique_non_empty(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(item.strip() for item in values if item.strip()))


class RelevanceFactor(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    value: float = Field(ge=0.0, le=1.0)
    weight: float = Field(ge=0.0, le=1.0)
    contribution: float = Field(ge=0.0)
    explanation: str


class RelevanceScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: float = Field(ge=0.0, le=1.0)
    factors: list[RelevanceFactor]
    config_version: str


class TraceStepKind(str, Enum):
    PLAN = "PLAN"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    CRITIC_CHECK = "CRITIC_CHECK"
    RETRY = "RETRY"
    COMPLETED = "COMPLETED"
    ERROR = "ERROR"


class TraceStepStatus(str, Enum):
    OK = "OK"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class TraceEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str = Field(min_length=1)
    seq: int = Field(ge=0)
    kind: TraceStepKind
    name: str = Field(min_length=1)
    status: TraceStepStatus = TraceStepStatus.OK
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_ids: list[str] = Field(default_factory=list)
    company_features: list[str] = Field(default_factory=list)
    model: str | None = None
    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)
    latency_ms: int | None = Field(default=None, ge=0)
    payload: dict[str, Any] = Field(default_factory=dict)


class Insight(BaseModel):
    model_config = ConfigDict(extra="forbid")

    insight_id: str = Field(min_length=1)
    company_id: str = Field(min_length=1)
    event_id: str = Field(min_length=1)
    role: Role
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    what_happened: list[EvidenceClaim]
    why_it_matters: list[EvidenceClaim]
    consequences: list[EvidenceClaim]
    actions: list[EvidenceClaim]
    bank_view: list[EvidenceClaim]
    basis: list[EvidenceClaim]
    relevance_score: RelevanceScore
    trace: list[TraceEvent] = Field(default_factory=list)


class Feedback(BaseModel):
    model_config = ConfigDict(extra="forbid")

    insight_id: str = Field(min_length=1)
    company_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    role: Role
    rating: str = Field(pattern=r"^(useful|not_useful|wrong)$")
    comment: str | None = Field(default=None, max_length=2000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
