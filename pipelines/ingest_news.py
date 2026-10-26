#!/usr/bin/env python3
"""Collect news from free sources (open APIs, RSS/Atom, opt-in scraping).

Feeds the same normalized store the app reads (`data/news/events.jsonl`).
Deterministic classification only: no LLM is used during bulk ingestion.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.contracts import NormalizedEvent  # noqa: E402
from app.data.industries import load_industry_catalog  # noqa: E402
from app.news.normalize import find_duplicate  # noqa: E402
from app.news.sources import (  # noqa: E402
    ADAPTERS,
    HttpClient,
    load_sources,
    raw_to_event,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest news from configured sources")
    parser.add_argument(
        "--sources", type=Path, default=ROOT / "config" / "news_sources.yaml"
    )
    parser.add_argument(
        "--industries", type=Path, default=ROOT / "config" / "industries.yaml"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "data" / "news" / "events.jsonl"
    )
    parser.add_argument(
        "--report", type=Path, default=ROOT / "data" / "news" / "ingest_report.json"
    )
    parser.add_argument("--only", default="", help="comma-separated source ids")
    parser.add_argument("--limit", type=int, default=20, help="max items per source")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def load_existing(path: Path) -> list[NormalizedEvent]:
    if not path.exists():
        return []
    events: list[NormalizedEvent] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                events.append(NormalizedEvent.model_validate_json(line))
    return events


def main() -> None:
    args = parse_args()
    catalog = load_industry_catalog(str(args.industries))
    sources = load_sources(args.sources)
    only = {part.strip() for part in args.only.split(",") if part.strip()}
    selected = [
        source
        for source in sources
        if source.enabled and (not only or source.id in only)
    ]

    http = HttpClient()
    existing = load_existing(args.output)
    known_ids = {event.event_id for event in existing}

    report: dict = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "sources": {},
        "total_new": 0,
        "total_duplicates": 0,
    }

    output_handle = None
    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        output_handle = args.output.open("a", encoding="utf-8")

    try:
        for source in selected:
            stats = {"fetched": 0, "new": 0, "duplicates": 0, "errors": []}
            adapter = ADAPTERS.get(source.kind)
            if adapter is None:
                stats["errors"].append(f"unknown kind: {source.kind}")
                report["sources"][source.id] = stats
                continue
            try:
                items = adapter(source, http, limit=args.limit)
            except Exception as exc:  # noqa: BLE001 - report and continue
                stats["errors"].append(f"{type(exc).__name__}: {str(exc)[:200]}")
                report["sources"][source.id] = stats
                continue
            stats["fetched"] = len(items)
            for item in items:
                try:
                    event = raw_to_event(item, catalog)
                except Exception as exc:  # noqa: BLE001
                    stats["errors"].append(f"extract: {type(exc).__name__}")
                    continue
                if event.event_id in known_ids:
                    stats["duplicates"] += 1
                    continue
                duplicate, _ = find_duplicate(event, existing)
                if duplicate is not None:
                    stats["duplicates"] += 1
                    continue
                existing.append(event)
                known_ids.add(event.event_id)
                stats["new"] += 1
                if output_handle is not None:
                    output_handle.write(event.model_dump_json() + "\n")
            report["sources"][source.id] = stats
            report["total_new"] += stats["new"]
            report["total_duplicates"] += stats["duplicates"]
    finally:
        if output_handle is not None:
            output_handle.close()

    report["finished_at"] = datetime.now(timezone.utc).isoformat()

    if not args.dry_run:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    for source_id, stats in report["sources"].items():
        line = (
            f"{source_id}: fetched={stats['fetched']} "
            f"new={stats['new']} dup={stats['duplicates']}"
        )
        if stats["errors"]:
            line += f" errors={len(stats['errors'])}"
        print(line)
    print(f"total new={report['total_new']} duplicates={report['total_duplicates']}")
    if args.dry_run:
        print("dry-run: nothing written")


if __name__ == "__main__":
    main()
