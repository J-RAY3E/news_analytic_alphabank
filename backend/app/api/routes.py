from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Query, Request

from app.api.mappers import insight_to_response, row_to_company
from app.api.schemas import (
    BudgetResponse,
    ChatRequest,
    ChatResponse,
    ClaimResponse,
    CompanyListResponse,
    ErrorResponse,
    EventDetailResponse,
    FeedbackRequest,
    FeedbackResponse,
    FeedResponse,
    IngestRequest,
    IngestResponse,
    InsightListResponse,
    InsightRequest,
    InsightResponse,
    MetricsResponse,
    SourceResponse,
    TraceResponse,
)
from app.config import Settings
from app.core.errors import BadRequest, DataNotReady, NotFound, NotImplementedYet
from app.llm.config import load_llm_config
from app.llm.governor import CostGovernor
from app.data.store import DataStore
from app.contracts import Insight, Role

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



@router.get(
    "/insights",
    response_model=InsightListResponse,
    tags=["insight"],
)
def list_insights(
    request: Request,
    company_id: str | None = Query(default=None),
    role: Role | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> InsightListResponse:
    from app.services.history import list_insights as list_insights_service

    items, total = list_insights_service(
        get_app_settings(request),
        get_store(request),
        company_id=company_id,
        role=role,
        limit=limit,
    )
    return InsightListResponse(items=items, total=total)


@router.get(
    "/insight/{insight_id}",
    response_model=InsightResponse,
    responses={404: {"model": ErrorResponse}},
    tags=["insight"],
)
def get_insight(request: Request, insight_id: str) -> InsightResponse:
    path = get_app_settings(request).path(
        "insights", insight_id.replace(":", "_") + ".json"
    )
    if not path.exists():
        raise NotFound(f"insight not found: {insight_id}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    insight = Insight.model_validate(payload)
    return insight_to_response(insight)


def _governor(settings: Settings) -> CostGovernor:
    return CostGovernor(
        load_llm_config(settings.llm_config),
        settings.path("cache", "llm_usage.jsonl"),
    )


@router.get(
    "/metrics/budget",
    response_model=BudgetResponse,
    tags=["ops"],
)
def get_budget(request: Request) -> BudgetResponse:
    settings = get_app_settings(request)
    governor = _governor(settings)
    summary = governor.summary()
    cache_hits = 0
    usage_path = settings.path("cache", "llm_usage.jsonl")
    if usage_path.exists():
        day = summary["day"]
        with usage_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("day") == day and record.get("cached"):
                    cache_hits += 1
    routing = load_llm_config(settings.llm_config).routing
    return BudgetResponse(
        day=summary["day"],
        spent_rub=summary["spent_rub"],
        budget_rub=summary["budget_rub"],
        remaining_rub=summary["remaining_rub"],
        model=routing.get("reasoning", ""),
        cache_hits=cache_hits,
    )


@router.get(
    "/sources/{source_id}",
    response_model=SourceResponse,
    tags=["insight"],
)
def get_source(request: Request, source_id: str) -> SourceResponse:
    if len(source_id) > 200:
        raise BadRequest("source id is too long")
    if source_id.startswith("bank:"):
        parts = source_id.split(":")
        doc_id = parts[1] if len(parts) > 1 else ""
        page: int | None = None
        if len(parts) > 2 and parts[2].startswith("p"):
            try:
                page = int(parts[2][1:])
            except ValueError:
                page = None
        title = doc_id.replace("_", " ")
        snippet = None
        index_path = get_app_settings(request).path("index", "research_chunks.jsonl")
        if index_path.exists():
            from app.research.index import load_research_index

            index = load_research_index(str(index_path))
            for chunk in index.chunks:
                if chunk.doc_id != doc_id:
                    continue
                title = chunk.title
                if page is None or chunk.page == page:
                    snippet = chunk.text[:600]
                    if page is None:
                        page = chunk.page
                    break
        return SourceResponse(
            source_id=source_id,
            kind="bank",
            name=title,
            page=page,
            snippet=snippet,
        )
    event = None
    for candidate in get_store(request).events_or_empty():
        if candidate.event_id == source_id or candidate.source.source_id == source_id:
            event = candidate
            break
    if event is None:
        return SourceResponse(
            source_id=source_id,
            kind="unknown",
            name="Источник не найден",
        )
    return SourceResponse(
        source_id=source_id,
        kind="news",
        name=event.source.name or "Новостной источник",
        url=event.source.url,
        published_at=event.source.published_at,
        snippet=(event.summary or event.title)[:600],
    )


@router.post(
    "/insight/{insight_id}/chat",
    response_model=ChatResponse,
    responses={404: {"model": ErrorResponse}},
    tags=["insight"],
)
def chat(request: Request, insight_id: str, payload: ChatRequest) -> ChatResponse:
    path = get_app_settings(request).path(
        "insights", insight_id.replace(":", "_") + ".json"
    )
    if not path.exists():
        raise NotFound(f"insight not found: {insight_id}")
    insight = json.loads(path.read_text(encoding="utf-8"))

    def claims(name: str) -> list[dict[str, Any]]:
        value = insight.get(name)
        return value if isinstance(value, list) else []

    sources: list[str] = []
    for name in (
        "what_happened",
        "why_it_matters",
        "consequences",
        "actions",
        "bank_view",
        "basis",
    ):
        for claim in claims(name):
            for source in claim.get("source_ids") or []:
                if source not in sources:
                    sources.append(source)

    question = payload.question.casefold()
    if "источник" in question:
        listed = ", ".join(sources) if sources else "не указаны"
        return ChatResponse(text="Источники вывода: " + listed + ".")
    if "срез" in question or "данн" in question:
        return ChatResponse(
            text="Доступны срезы по ролям (CEO, CFO, казначей) и по продуктам "
            "банка; смените роль переключателем в ленте."
        )
    if "подробн" in question or "объясн" in question:
        answers = claims("bank_view") or claims("actions") or claims("consequences")
        if answers:
            return ChatResponse(text="", claim=ClaimResponse(**answers[0]))
    what = claims("what_happened")
    summary = what[0]["text"] if what else "Событие без деталей."
    return ChatResponse(
        text="Кратко: "
        + summary
        + " Предложено действий: "
        + str(len(claims("actions")))
        + "."
    )


def _count_feedback(path) -> tuple[int, int]:
    total = 0
    useful = 0
    if not path.exists():
        return total, useful
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                if json.loads(line).get("rating") == "useful":
                    useful += 1
            except json.JSONDecodeError:
                continue
    return total, useful


def _usage_stats(usage_path, audit_path) -> tuple[float | None, float | None]:
    costs: list[float] = []
    if usage_path.exists():
        with usage_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not record.get("cached"):
                    costs.append(float(record.get("estimated_cost_rub", 0.0)))
    latencies: list[float] = []
    if audit_path.exists():
        with audit_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("kind") == "model" and record.get("latency_ms"):
                    latencies.append(float(record["latency_ms"]))
    avg_cost = round(sum(costs) / len(costs), 6) if costs else None
    avg_latency = round(sum(latencies) / len(latencies), 1) if latencies else None
    return avg_cost, avg_latency


@router.get("/metrics", response_model=MetricsResponse, tags=["ops"])
def get_metrics(request: Request) -> MetricsResponse:
    settings = get_app_settings(request)
    store = get_store(request)
    events = store.events_or_empty()
    events_total = len(events)
    covered = sum(1 for event in events if event.source.name and event.source.published_at)
    source_coverage = round(covered / events_total, 4) if events_total else 0.0

    insights_dir = settings.path("insights")
    insights_total = len(list(insights_dir.glob("*.json"))) if insights_dir.exists() else 0

    feedback_total, useful = _count_feedback(settings.path("feedback", "feedback.jsonl"))
    thumbs_up_ratio = round(useful / feedback_total, 4) if feedback_total else None

    avg_cost, avg_latency = _usage_stats(
        settings.path("cache", "llm_usage.jsonl"),
        settings.path("audit", "tool_calls.jsonl"),
    )
    summary = _governor(settings).summary()
    return MetricsResponse(
        generated_at=datetime.now(timezone.utc),
        events_total=events_total,
        insights_total=insights_total,
        feedback_total=feedback_total,
        thumbs_up_ratio=thumbs_up_ratio,
        source_coverage=source_coverage,
        avg_cost_rub=avg_cost,
        avg_latency_ms=avg_latency,
        llm_spent_today_rub=summary["spent_rub"],
        llm_budget_rub=summary["budget_rub"],
    )
