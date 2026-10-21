#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.config import get_settings  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Minimal LLM connectivity and budget check")
    parser.add_argument("--model", default=None)
    return parser.parse_args()


def main(model: str | None = None) -> int:
    from openai import OpenAI

    settings = get_settings()
    if not settings.llm_api_key:
        print("LLM_API_KEY is empty; set it in .env", file=sys.stderr)
        return 2
    model = model or settings.llm_model_extraction
    bases = [settings.llm_base_url, settings.llm_base_url_fallback]
    last_error: Exception | None = None
    response = None
    used_base = ""
    for base in bases:
        try:
            client = OpenAI(
                api_key=settings.llm_api_key,
                base_url=base,
                timeout=20.0,
            )
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Answer with one word: ok"}],
                max_tokens=8,
                temperature=0,
            )
            used_base = base
            break
        except Exception as exc:
            last_error = exc
            print(f"base failed: {base} ({type(exc).__name__})", file=sys.stderr)
    if response is None:
        print(f"all bases failed: {type(last_error).__name__}: {last_error}", file=sys.stderr)
        return 1
    usage = response.usage
    print(f"model={model}")
    print(f"base={used_base}")
    print(f"reply={response.choices[0].message.content!r}")
    if usage:
        print(
            f"tokens prompt={usage.prompt_tokens} completion={usage.completion_tokens} "
            f"total={usage.total_tokens}"
        )
    print(f"budget_limit_rub_per_day={settings.llm_daily_budget_rub}")
    return 0


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main(args.model))
