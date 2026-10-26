from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class Product(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    category: str = ""
    short: str
    url: str
    features: list[str] = Field(default_factory=list)
    when_macro: list[str] = Field(default_factory=list)


class ProductCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    products: list[Product]


@lru_cache
def load_product_catalog(path: str | Path) -> ProductCatalog:
    resolved = Path(path).resolve()
    with resolved.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"product catalog must be a mapping: {resolved}")
    return ProductCatalog.model_validate(payload)
