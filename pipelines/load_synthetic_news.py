#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.contracts import NormalizedEvent  # noqa: E402
from app.news.normalize import dedupe_events  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load and deduplicate synthetic news")
    parser.add_argument(
        "--input", type=Path, default=ROOT / "data" / "news" / "synthetic_raw.jsonl"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "data" / "news" / "events.jsonl"
    )
    parser.add_argument("--threshold", type=float, default=0.88)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    events: list[NormalizedEvent] = []
    with args.input.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                events.append(NormalizedEvent.model_validate_json(line))

    result = dedupe_events(events, threshold=args.threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for event in result.unique:
            handle.write(event.model_dump_json() + "\n")

    report = {
        "input_events": len(events),
        "unique_events": len(result.unique),
        "duplicates": result.duplicates,
        "clusters": result.clusters,
        "threshold": args.threshold,
    }
    report_path = args.output.parent / "dedupe_report.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"input: {len(events)}")
    print(f"unique: {len(result.unique)}")
    print(f"duplicates: {len(result.duplicates)}")
    print(f"wrote {args.output.relative_to(ROOT)}")
    print(f"wrote {report_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
