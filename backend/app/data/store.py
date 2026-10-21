from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from app.config import Settings
from app.contracts import NormalizedEvent
from app.core.errors import DataNotReady, NotFound


class DataStore:
    def __init__(
        self,
        settings: Settings,
        companies_path: Path | None = None,
        graph_path: Path | None = None,
        news_path: Path | None = None,
    ) -> None:
        self.settings = settings
        self.companies_path = companies_path or settings.path("processed", "companies.parquet")
        self.graph_path = graph_path or settings.path("processed", "graph_features.parquet")
        self.news_path = news_path or settings.path("news", "events.jsonl")
        self._companies: pd.DataFrame | None = None
        self._graph: pd.DataFrame | None = None
        self._events: list[NormalizedEvent] | None = None

    def reset(self) -> None:
        self._companies = None
        self._graph = None
        self._events = None

    @property
    def companies(self) -> pd.DataFrame:
        if self._companies is None:
            if not self.companies_path.exists():
                raise DataNotReady(
                    "companies.parquet is missing; run pipelines/build_features.py",
                    {"path": str(self.companies_path)},
                )
            self._companies = pd.read_parquet(self.companies_path)
            self._companies = self._companies.set_index("company_id", drop=False)
        return self._companies

    @property
    def graph(self) -> pd.DataFrame:
        if self._graph is None:
            if not self.graph_path.exists():
                raise DataNotReady(
                    "graph_features.parquet is missing; run pipelines/build_features.py",
                    {"path": str(self.graph_path)},
                )
            self._graph = pd.read_parquet(self.graph_path)
            self._graph = self._graph.set_index("company_id", drop=False)
        return self._graph

    @property
    def events(self) -> list[NormalizedEvent]:
        if self._events is None:
            if not self.news_path.exists():
                raise DataNotReady(
                    "events.jsonl is missing; run pipelines/load_synthetic_news.py",
                    {"path": str(self.news_path)},
                )
            events: list[NormalizedEvent] = []
            with self.news_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if line:
                        events.append(NormalizedEvent.model_validate(json.loads(line)))
            self._events = events
        return self._events

    def events_or_empty(self) -> list[NormalizedEvent]:
        try:
            return self.events
        except DataNotReady:
            return []

    def append_event(self, event: NormalizedEvent) -> None:
        self.news_path.parent.mkdir(parents=True, exist_ok=True)
        with self.news_path.open("a", encoding="utf-8") as handle:
            handle.write(event.model_dump_json() + "\n")
        if self._events is not None:
            self._events.append(event)

    def company(self, company_id: str) -> dict[str, Any]:
        frame = self.companies
        if company_id not in frame.index:
            raise NotFound(f"company not found: {company_id}")
        row = frame.loc[company_id]
        if isinstance(row, pd.DataFrame):
            row = row.iloc[0]
        return row.to_dict()

    def event(self, event_id: str) -> NormalizedEvent:
        for event in self.events:
            if event.event_id == event_id:
                return event
        raise NotFound(f"event not found: {event_id}")
