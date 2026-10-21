from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ModelPricing(BaseModel):
    model_config = ConfigDict(extra="forbid")

    input_rub_per_1m: float = Field(gt=0.0)
    output_rub_per_1m: float = Field(gt=0.0)


class LLMConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    daily_budget_rub: float = Field(gt=0.0)
    cache_ttl_days: int = Field(ge=0)
    request_timeout_seconds: float = Field(gt=0.0)
    total_timeout_seconds: float = Field(default=180.0, gt=0.0)
    routing: dict[str, str]
    models: dict[str, ModelPricing]

    @model_validator(mode="after")
    def routing_models_exist(self) -> LLMConfig:
        for purpose in ("extraction", "reasoning", "fallback", "long"):
            model = self.routing.get(purpose)
            if not model:
                raise ValueError(f"missing routing for {purpose}")
            if model not in self.models:
                raise ValueError(f"routing model without pricing: {model}")
        return self


@lru_cache
def load_llm_config(path: str | Path) -> LLMConfig:
    resolved = Path(path).resolve()
    with resolved.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"llm config must be a mapping: {resolved}")
    return LLMConfig.model_validate(payload)
