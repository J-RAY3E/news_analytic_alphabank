from __future__ import annotations

from app.contracts import MacroFactor, NormalizedEvent
from app.news.extract import extract_event
from app.news.sources.base import RawItem


def _default_macro(tags: dict) -> list[MacroFactor]:
    factors: list[MacroFactor] = []
    for value in tags.get("default_macro", []) or []:
        try:
            factors.append(MacroFactor(str(value).strip().upper()))
        except ValueError:
            continue
    return factors


def raw_to_event(item: RawItem, catalog) -> NormalizedEvent:
    """Turn a collected RawItem into a normalized event (deterministic, no LLM)."""
    text = " ".join(part for part in (item.title, item.summary) if part).strip()
    event = extract_event(
        text=text,
        title=item.title,
        source_url=item.url,
        source_name=item.source_name,
        published_at=item.published_at,
        summary=item.summary,
        catalog=catalog,
    )
    if not event.macro_factors:
        defaults = _default_macro(item.tags)
        if defaults:
            event = event.model_copy(update={"macro_factors": defaults})
    return event
