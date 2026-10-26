from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin

from app.news.extract import extract_text_from_html
from app.news.sources.base import HttpClient, RawItem, Source

MIN_LINK_TEXT = 15


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self._href = dict(attrs).get("href")

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href is not None:
            text = " ".join(" ".join(self._text).split())
            self.links.append((self._href, text))
            self._href = None
            self._text = []


def extract_links(html: str) -> list[tuple[str, str]]:
    parser = _LinkParser()
    parser.feed(html)
    return parser.links


def fetch(source: Source, http: HttpClient, limit: int = 5) -> list[RawItem]:
    if not source.url or not http.allowed_by_robots(source.url):
        return []
    html = http.get_bytes(source.url, source.rate_limit_per_minute).decode("utf-8", "replace")
    pattern = source.options.get("link_pattern")
    seen: set[str] = set()
    items: list[RawItem] = []
    for href, text in extract_links(html):
        if len(items) >= max(limit, 0):
            break
        if not href or len(text) < MIN_LINK_TEXT:
            continue
        url = urljoin(source.url, href)
        if pattern and pattern not in url:
            continue
        if url in seen or not http.allowed_by_robots(url):
            continue
        seen.add(url)
        try:
            article = http.get_bytes(url, source.rate_limit_per_minute).decode("utf-8", "replace")
        except Exception:
            continue
        title, description, body = extract_text_from_html(article)
        title = " ".join((title or text).split())
        if not title:
            continue
        items.append(
            RawItem(
                title=title,
                summary=" ".join((description or body).split())[:1000],
                url=url,
                source_name=source.name,
                source_id=f"{source.id}:{url}",
                published_at=datetime.now(timezone.utc),
                tags=source.tags,
            )
        )
    return items
