from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Query, Request

from app.api.mappers import insight_to_response, row_to_company
from app.api.schemas import (
    CompanyListResponse,
    ErrorResponse,
    EventDetailResponse,
    FeedbackRequest,
    FeedbackResponse,
    FeedResponse,
    IngestRequest,
    IngestResponse,
    InsightRequest,
    InsightResponse,
    TraceResponse,
)
from app.config import Settings
from app.core.errors import BadRequest, DataNotReady, NotFound, NotImplementedYet
from app.data.store import DataStore
from app.contracts import Role

router = APIRouter()

TRACE_ID_PATTERN = re.compile(r"^trace:[A-Za-z0-9_.-]{1,64}$")


def get_store(request: Request) -> DataStore:
    return request.app.state.store


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


@router.get("/health", tags=["ops"])
def health(request: Request) -> dict[str, Any]:
    store = get_store(request)
    settings = get_app_settings(request)
    return {
        "status": "ok",
        "environment": settings.app_env,
        "data": {
            "companies": store.companies_path.exists(),
            "graph": store.graph_path.exists(),
            "news": store.news_path.exists(),
        },
    }


@router.get(
    "/companies",
    response_model=CompanyListResponse,
    responses={503: {"model": ErrorResponse}},
    tags=["companies"],
)
def list_companies(
    request: Request,
    q: str | None = Query(default=None, max_length=200),
    target_only: bool = Query(default=False),
    limit: int = Query(default=50, ge=1, le=500),
) -> CompanyListResponse:
    frame = get_store(request).companies
    if target_only and "revenue_rub" in frame.columns:
        frame = frame[frame["revenue_rub"] >= 15_000_000_000]
    if q:
        needle = q.casefold()
        mask = (
            frame["display_name"].fillna("").str.casefold().str.contains(needle, regex=False)
            | frame["okved_name"].fillna("").str.casefold().str.contains(needle, regex=False)
            | frame["region"].fillna("").str.casefold().str.contains(needle, regex=False)
            | frame["company_id"].fillna("").str.casefold().str.contains(needle, regex=False)
        )
        frame = frame[mask]
    total = int(len(frame))
    frame = frame.sort_values("revenue_rub", ascending=False).head(limit)
    return CompanyListResponse(
        items=[row_to_company(row) for _, row in frame.iterrows()],
        total=total,
    )


@router.get(
    "/companies/{company_id}",
    response_model=CompanyListResponse,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
    tags=["companies"],
)
def get_company(request: Request, company_id: str) -> CompanyListResponse:
    store = get_store(request)
    row = store.company(company_id)
    return CompanyListResponse(items=[row_to_company(row)], total=1)


@router.get(
    "/feed",
    response_model=FeedResponse,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
    tags=["feed"],
)
def get_feed(
    request: Request,
    company_id: str = Query(min_length=1),
    role: Role = Query(default=Role.CEO),
    limit: int = Query(default=10, ge=1, le=50),
) -> FeedResponse:
    store = get_store(request)
    settings = get_app_settings(request)
    store.company(company_id)
    try:
        from app.services.feed import build_feed
    except ImportError as exc:
        raise NotImplementedYet("feed service is not available yet") from exc
    return build_feed(store, settings, company_id=company_id, role=role, limit=limit)


@router.get(
    "/events/{event_id}",
    response_model=EventDetailResponse,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
    tags=["news"],
)
def get_event(request: Request, event_id: str) -> EventDetailResponse:
    event = get_store(request).event(event_id)
    return EventDetailResponse(event=event)


@router.post(
    "/ingest",
    response_model=IngestResponse,
    responses={400: {"model": ErrorResponse}},
    tags=["news"],
)
def ingest(request: Request, payload: IngestRequest) -> IngestResponse:
    if not payload.text and not payload.url:
        raise BadRequest("provide text or url")
    try:
        from app.news.ingest import ingest_event
    except ImportError as exc:
        raise NotImplementedYet("ingest service is not available yet") from exc
    return ingest_event(
        get_store(request),
        get_app_settings(request),
        text=payload.text,
        url=payload.url,
        title=payload.title,
    )


@router.post(
    "/insight",
    response_model=InsightResponse,
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
    tags=["insight"],
)
def create_insight(request: Request, payload: InsightRequest) -> InsightResponse:
    store = get_store(request)
    settings = get_app_settings(request)
    store.company(payload.company_id)
    store.event(payload.event_id)
    try:
        from app.services.insight import build_insight
    except ImportError as exc:
        raise NotImplementedYet("insight service is not available yet") from exc
    insight = build_insight(
        store,
        settings,
        company_id=payload.company_id,
        event_id=payload.event_id,
        role=payload.role,
    )
    return insight_to_response(insight)


@router.get(
    "/trace/{trace_id}",
    response_model=TraceResponse,
    responses={404: {"model": ErrorResponse}},
    tags=["insight"],
)
def get_trace(request: Request, trace_id: str) -> TraceResponse:
    if not TRACE_ID_PATTERN.match(trace_id):
        raise BadRequest("invalid trace id format")
    path = get_app_settings(request).path("traces", f"{trace_id}.json")
    if not path.exists():
        raise NotFound(f"trace not found: {trace_id}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return TraceResponse(
        trace_id=payload.get("trace_id", trace_id),
        events=payload.get("events", []),
    )


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    tags=["feedback"],
)
def submit_feedback(request: Request, payload: FeedbackRequest) -> FeedbackResponse:
    feedback_id = f"feedback:{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
    directory = get_app_settings(request).path("feedback")
    directory.mkdir(parents=True, exist_ok=True)
    record = payload.model_dump(mode="json")
    record["feedback_id"] = feedback_id
    record["created_at"] = datetime.now(timezone.utc).isoformat()
    with (directory / "feedback.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return FeedbackResponse(stored=True, feedback_id=feedback_id)
