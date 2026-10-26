from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
import yaml

from app.news.extract import validate_public_url

DEFAULT_USER_AGENT = (
    "AlfaRadarBot/0.1 (+https://github.com/alfa-hack-2026/alfa-radar)"
)
DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_MAX_BYTES = 2_000_000
DEFAULT_RATE_LIMIT_PER_MINUTE = 30

ACCEPT_HEADER = (
    "application/rss+xml, application/atom+xml, application/xml, text/xml, "
    "application/json, text/html;q=0.8, */*;q=0.5"
)


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    kind: str
    url: str | None = None
    api: str | None = None
    language: str = "ru"
    enabled: bool = True
    rate_limit_per_minute: int = DEFAULT_RATE_LIMIT_PER_MINUTE
    tags: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class RawItem:
    title: str
    summary: str
    url: str | None
    source_name: str
    source_id: str
    published_at: datetime | None = None
    tags: dict[str, Any] = field(default_factory=dict)


def load_sources(path: str | Path) -> list[Source]:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"news sources config must be a mapping: {path}")
    defaults = payload.get("defaults", {}) or {}
    sources: list[Source] = []
    for raw in payload.get("sources", []) or []:
        options = raw.get("options", {}) or {}
        sources.append(
            Source(
                id=str(raw["id"]),
                name=str(raw.get("name", raw["id"])),
                kind=str(raw["kind"]).casefold(),
                url=options.get("url") or raw.get("url"),
                api=raw.get("api"),
                language=str(raw.get("language", "ru")),
                enabled=bool(raw.get("enabled", True)),
                rate_limit_per_minute=int(
                    raw.get(
                        "rate_limit_per_minute",
                        defaults.get(
                            "rate_limit_per_minute", DEFAULT_RATE_LIMIT_PER_MINUTE
                        ),
                    )
                ),
                tags=raw.get("tags", {}) or {},
                options=options,
            )
        )
    return sources


class HttpClient:
    """Shared, polite HTTP client for news sources.

    Enforces SSRF protection (via validate_public_url), a per-host rate limit, a
    response size cap and a project User-Agent. Also answers robots.txt queries
    used by the scraping adapter.
    """

    def __init__(
        self,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_bytes: int = DEFAULT_MAX_BYTES,
    ) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self.max_bytes = max_bytes
        self._last_request: dict[str, float] = {}
        self._robots: dict[str, RobotFileParser] = {}

    def _throttle(self, host: str, rate_limit_per_minute: int) -> None:
        interval = 60.0 / max(rate_limit_per_minute, 1)
        elapsed = time.monotonic() - self._last_request.get(host, 0.0)
        if elapsed < interval:
            time.sleep(interval - elapsed)
        self._last_request[host] = time.monotonic()

    def get_bytes(self, url: str, rate_limit_per_minute: int = DEFAULT_RATE_LIMIT_PER_MINUTE) -> bytes:
        validate_public_url(url)
        host = urlparse(url).hostname or ""
        last_error: Exception | None = None
        for attempt in range(2):
            self._throttle(host, rate_limit_per_minute)
            try:
                with httpx.Client(
                    timeout=self.timeout,
                    follow_redirects=True,
                    headers={"User-Agent": self.user_agent, "Accept": ACCEPT_HEADER},
                ) as client:
                    response = client.get(url)
                    response.raise_for_status()
                    return response.content[: self.max_bytes]
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc
                continue
        assert last_error is not None
        raise last_error

    def allowed_by_robots(self, url: str) -> bool:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        parser = self._robots.get(host)
        if parser is None:
            parser = RobotFileParser()
            try:
                robots_url = f"{parsed.scheme}://{host}/robots.txt"
                content = self.get_bytes(robots_url, rate_limit_per_minute=60)
                parser.parse(content.decode("utf-8", "replace").splitlines())
            except Exception:
                parser.allow_all = True
            self._robots[host] = parser
        return parser.can_fetch(self.user_agent, url)
