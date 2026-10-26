from __future__ import annotations

from typing import Callable

from app.news.sources import api, rss, scrape
from app.news.sources.base import (
    DEFAULT_USER_AGENT,
    HttpClient,
    RawItem,
    Source,
    load_sources,
)
from app.news.sources.convert import raw_to_event

ADAPTERS: dict[str, Callable[..., list[RawItem]]] = {
    "rss": rss.fetch,
    "api": api.fetch,
    "scrape": scrape.fetch,
}

__all__ = [
    "ADAPTERS",
    "DEFAULT_USER_AGENT",
    "HttpClient",
    "RawItem",
    "Source",
    "load_sources",
    "raw_to_event",
]
