from __future__ import annotations

from datetime import datetime, timezone

import feedparser

from app.news.sources.base import HttpClient, RawItem, Source


def _entry_time(entry: dict) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        value = entry.get(key)
        if value:
            try:
                return datetime(*value[:6], tzinfo=timezone.utc)
            except (TypeError, ValueError):
                continue
    return None


def _clean(value: str | None) -> str:
    return " ".join((value or "").split())


def fetch(source: Source, http: HttpClient, limit: int = 30) -> list[RawItem]:
    if not source.url:
        return []
    content = http.get_bytes(source.url, source.rate_limit_per_minute)
    feed = feedparser.parse(content)
    items: list[RawItem] = []
    for entry in feed.entries[: max(limit, 0)]:
        title = _clean(entry.get("title"))
        if not title:
            continue
        summary = _clean(entry.get("summary") or entry.get("description"))
        url = entry.get("link")
        items.append(
            RawItem(
                title=title,
                summary=summary,
                url=url,
                source_name=source.name,
                source_id=f"{source.id}:{entry.get('id') or url or title}",
                published_at=_entry_time(entry),
                tags=source.tags,
            )
        )
    return items
