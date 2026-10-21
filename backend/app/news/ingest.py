from __future__ import annotations

from datetime import datetime, timezone

from app.api.schemas import IngestResponse
from app.config import Settings
from app.contracts import NormalizedEvent
from app.core.errors import BadRequest
from app.data.industries import load_industry_catalog
from app.data.store import DataStore
from app.agents.a2_news import A2NewsIntake
from app.news.extract import extract_event, fetch_url
from app.news.normalize import find_duplicate


def ingest_event(
    store: DataStore,
    settings: Settings,
    text: str | None = None,
    url: str | None = None,
    title: str | None = None,
) -> IngestResponse:
    catalog = load_industry_catalog(settings.industries_config)
    resolved_title = title
    summary = ""
    source_name: str | None = None
    if url:
        try:
            page_title, description, page_text, final_url = fetch_url(url)
        except Exception as exc:
            raise BadRequest(f"could not fetch url: {exc}") from exc
        if not page_text.strip():
            raise BadRequest("fetched page has no readable text")
        text = page_text
        summary = description
        source_name = final_url.split("/")[2] if "//" in final_url else final_url
        resolved_title = title or page_title
        url = final_url
    if not text or not text.strip():
        raise BadRequest("provide non-empty text or url")

    event = extract_event(
        text=text,
        title=resolved_title,
        source_url=url,
        source_name=source_name,
        published_at=datetime.now(timezone.utc),
        summary=summary,
        catalog=catalog,
    )

    if settings.llm_enabled:
        extraction = A2NewsIntake(settings).extract(event, text)
        event = extraction.event

    existing = store.events_or_empty()
    duplicate, score = find_duplicate(event, existing)
    if duplicate is not None:
        return IngestResponse(
            event=duplicate,
            duplicate_of=duplicate.event_id,
        )

    store.append_event(event)
    return IngestResponse(event=event, duplicate_of=None)
