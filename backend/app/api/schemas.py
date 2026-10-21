from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.contracts import (
    ClaimType,
    EventType,
    MacroFactor,
    NormalizedEvent,
    RiskOpportunity,
    Role,
    Sentiment,
)


class CompanySummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_id: str
    display_name: str
    okved_code: str
    okved_name: str
    okved_division: str | None
    okved_section: str | None
    industry_label: str
    region: str
    city: str
    revenue_rub: float
    revenue_band: str
    employees_band: str
    client_type: str
    product_flags: list[str]
    is_exporter: bool
    fts_countries: list[str]
    group_id: str | None
    group_size: int


class CompanyListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CompanySummary]
    total: int


class FeedEventCard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    title: str
    summary: str
    event_type: EventType
    sectors: list[str]
    regions: list[str]
    countries: list[str]
    macro_factors: list[MacroFactor]
    sentiment: Sentiment
    risk_opportunity: RiskOpportunity
    published_at: datetime | None
    source_name: str
    source_url: str | None


class RelevanceFactorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    value: float
    weight: float
    contribution: float
    explanation: str


class FeedItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event: FeedEventCard
    relevance_score: float
    factors: list[RelevanceFactorResponse]
    reasons: list[str]
    role: Role


class FeedResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company: CompanySummary
    role: Role
    items: list[FeedItem]
    scoring_config_version: str


class EventDetailResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event: NormalizedEvent


class IngestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str | None = Field(default=None, max_length=100_000)
    url: str | None = Field(default=None, max_length=2000)
    title: str | None = Field(default=None, max_length=500)


class IngestResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event: NormalizedEvent
    duplicate_of: str | None = None


class ClaimResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str
    type: ClaimType
    source_ids: list[str]
    company_features: list[str]
    confidence: float


class InsightResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    insight_id: str
    company_id: str
    event_id: str
    role: Role
    created_at: datetime
    what_happened: list[ClaimResponse]
    why_it_matters: list[ClaimResponse]
    consequences: list[ClaimResponse]
    actions: list[ClaimResponse]
    bank_view: list[ClaimResponse]
    basis: list[ClaimResponse]
    relevance_score: float
    scoring_factors: list[RelevanceFactorResponse]
    trace: list[dict[str, Any]]


class InsightRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_id: str
    event_id: str
    role: Role = Role.CEO


class TraceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    trace_id: str
    events: list[dict[str, Any]]


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    insight_id: str
    company_id: str
    user_id: str
    role: Role
    rating: Literal["useful", "not_useful", "wrong"]
    comment: str | None = Field(default=None, max_length=2000)


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stored: bool
    feedback_id: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorBody
