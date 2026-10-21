from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI

from app.config import Settings
from app.llm.config import LLMConfig, load_llm_config
from app.llm.governor import BudgetExceeded, CostGovernor


class LLMError(RuntimeError):
    pass


class LLMClient:
    def __init__(
        self,
        settings: Settings,
        config: LLMConfig | None = None,
        governor: CostGovernor | None = None,
    ) -> None:
        self.settings = settings
        self.config = config or load_llm_config(str(settings.llm_config))
        self.governor = governor or CostGovernor(
            self.config, settings.path("cache", "llm_usage.jsonl")
        )
        self.cache_dir = settings.path("cache", "llm")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.last_usage: dict[str, Any] | None = None

    @property
    def enabled(self) -> bool:
        return self.settings.llm_enabled and bool(self.settings.llm_api_key.strip())

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def _cache_key(
        self, model: str, system: str, user: str, max_tokens: int, temperature: float
    ) -> str:
        digest = hashlib.sha256()
        for part in (model, system, user, str(max_tokens), str(temperature)):
            digest.update(part.encode("utf-8"))
            digest.update(b"\0")
        return digest.hexdigest()

    def _read_cache(self, path: Path, primary_model: str) -> tuple[dict[str, Any], str] | None:
        if self.config.cache_ttl_days <= 0 or not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            created_at = datetime.fromisoformat(payload["created_at"])
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            ttl = timedelta(days=self.config.cache_ttl_days)
            if datetime.now(timezone.utc) - created_at > ttl:
                return None
            response = payload.get("response")
            model = str(payload.get("model") or primary_model)
            return (response, model) if isinstance(response, dict) else None
        except (OSError, ValueError, KeyError, TypeError):
            return None

    def _write_cache(self, path: Path, response: dict[str, Any], model: str) -> None:
        if self.config.cache_ttl_days <= 0:
            return
        payload = {
            "model": model,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "response": response,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def _parse_json(content: str) -> dict[str, Any]:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise LLMError("LLM response does not contain a JSON object")
        try:
            payload = json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise LLMError(f"invalid LLM JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise LLMError("LLM JSON payload must be an object")
        return payload

    def _estimate_cost(
        self, model: str, system: str, user: str, max_tokens: int
    ) -> float:
        pricing = self.config.models[model]
        input_tokens = max(1, (len(system) + len(user)) // 3)
        return (
            input_tokens * pricing.input_rub_per_1m / 1_000_000
            + max_tokens * pricing.output_rub_per_1m / 1_000_000
        )

    def complete_json(
        self,
        purpose: str,
        system: str,
        user: str,
        max_tokens: int = 1800,
        temperature: float = 0.2,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        if not self.enabled:
            raise LLMError("LLM is disabled or API key is missing")
        self.last_usage = None
        primary_model = self.config.routing[purpose]
        fallback_model = self.config.routing["fallback"]
        cache_key = self._cache_key(primary_model, system, user, max_tokens, temperature)
        cache_path = self._cache_path(cache_key)
        if use_cache:
            cached = self._read_cache(cache_path, primary_model)
            if cached is not None:
                cached_payload, cached_model = cached
                self.governor.record_usage(
                    model=cached_model,
                    purpose=purpose,
                    prompt_tokens=0,
                    completion_tokens=0,
                    cost_rub=0.0,
                    cached=True,
                )
                self.last_usage = {
                    "model": cached_model,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "cost_rub": 0.0,
                    "cached": True,
                }
                return cached_payload

        attempts: list[tuple[str, str]] = []
        for model, base_url in (
            (primary_model, self.settings.llm_base_url),
            (fallback_model, self.settings.llm_base_url),
            (fallback_model, self.settings.llm_base_url_fallback),
        ):
            if base_url and (model, base_url) not in attempts:
                attempts.append((model, base_url))

        errors: list[str] = []
        started_total = time.monotonic()
        for model, base_url in attempts:
            if time.monotonic() - started_total > self.config.total_timeout_seconds:
                errors.append("total timeout exceeded")
                break
            estimated = self._estimate_cost(model, system, user, max_tokens)
            self.governor.check(estimated)
            started = time.monotonic()
            try:
                client = OpenAI(
                    api_key=self.settings.llm_api_key,
                    base_url=base_url,
                    timeout=self.config.request_timeout_seconds,
                    max_retries=0,
                )
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                content = response.choices[0].message.content or ""
                payload = self._parse_json(content)
                usage = getattr(response, "usage", None)
                prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
                completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
                pricing = self.config.models[model]
                estimated_actual = (
                    prompt_tokens * pricing.input_rub_per_1m / 1_000_000
                    + completion_tokens * pricing.output_rub_per_1m / 1_000_000
                )
                reported_cost = getattr(usage, "cost", None) if usage else None
                try:
                    reported_cost = float(reported_cost) if reported_cost is not None else None
                except (TypeError, ValueError):
                    reported_cost = None
                cost = reported_cost if reported_cost and reported_cost > 0 else estimated_actual
                self.governor.record_usage(
                    model=model,
                    purpose=purpose,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    cost_rub=cost,
                )
                if use_cache:
                    self._write_cache(cache_path, payload, model)
                self.last_usage = {
                    "model": model,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "cost_rub": round(cost, 6),
                    "cached": False,
                }
                return payload
            except BudgetExceeded:
                raise
            except Exception as exc:
                elapsed = int((time.monotonic() - started) * 1000)
                errors.append(f"{model}@{base_url} after {elapsed}ms: {type(exc).__name__}")
                continue
        raise LLMError("all LLM attempts failed: " + "; ".join(errors))
