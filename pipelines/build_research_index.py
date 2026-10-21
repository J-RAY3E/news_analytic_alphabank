#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.research.chunker import build_chunks, read_documents  # noqa: E402
from app.research.index import ResearchIndex  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build bank research chunk index")
    parser.add_argument("--research-dir", type=Path, default=ROOT / "data" / "research")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "data" / "index")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    documents = read_documents(args.research_dir)
    chunks = build_chunks(documents)
    index = ResearchIndex(chunks)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    chunks_path = args.out_dir / "research_chunks.jsonl"
    index.to_jsonl(chunks_path)
    manifest = {
        "documents": index.documents(),
        "chunks": len(chunks),
        "research_dir": str(args.research_dir),
    }
    (args.out_dir / "research_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"documents: {len(documents)}")
    print(f"chunks: {len(chunks)}")
    print(f"wrote {chunks_path.relative_to(ROOT)}")
    print(f"wrote {(args.out_dir / 'research_manifest.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
