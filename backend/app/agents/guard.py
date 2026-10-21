from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import Settings
from app.contracts import Role

ALLOWED_TOOLS = {
    "get_company_profile",
    "get_graph_exposure",
    "get_event",
    "search_bank_analytics",
    "get_bank_card",
}

SENSITIVE_COMPANY_FIELDS = {
    "company_id",
    "group_id",
    "inn",
    "ogrn",
    "okpo",
    "kpp",
    "name",
    "short_name",
    "full_name",
    "display_name",
    "address",
}

PRODUCT_FEATURES = (
    "CL_PRODUCT_RKO_MARK",
    "CL_PRODUCT_GAR_MARK",
    "CL_PRODUCT_LOA_MARK",
    "CL_PRODUCT_LEA_MARK",
    "CL_PRODUCT_DEP_MARK",
    "CL_PRODUCT_ZPP_MARK",
    "FACTORING_MARK",
)


class ToolNotAllowed(Exception):
    pass


def prompt_safe_company(company: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in company.items():
        if key in SENSITIVE_COMPANY_FIELDS:
            continue
        if isinstance(value, float) and value != value:
            continue
        safe[key] = value
    safe["company_ref"] = "client"
    return safe


def prompt_safe_graph(graph: dict[str, Any] | None) -> dict[str, Any] | None:
    if not graph:
        return None
    keys = (
        "has_payment_activity",
        "payment_activity_share",
        "supplier_division_shares",
        "client_division_shares",
        "top_supplier_industries",
        "top_client_industries",
        "supplier_hhi",
        "client_hhi",
        "group_payment_share",
        "external_payment_share",
    )
    safe = {key: graph.get(key) for key in keys if graph.get(key) is not None}
    return safe


def _product_flags(company: dict[str, Any]) -> list[str]:
    value = company.get("product_flags")
    if value is None:
        return []
    if hasattr(value, "tolist"):
        value = value.tolist()
    if isinstance(value, str):
        return [part.strip() for part in value.replace(";", ",").split(",") if part.strip()]
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def company_feature_names(
    company: dict[str, Any], graph: dict[str, Any] | None = None
) -> list[str]:
    features: list[str] = []
    flags = _product_flags(company)
    for feature in PRODUCT_FEATURES:
        value = company.get(feature)
        try:
            present = float(value) > 0
        except (TypeError, ValueError):
            present = bool(value)
        if present or feature in flags:
            features.append(feature)
    if company.get("is_exporter") or company.get("fts_flag"):
        features.append("FTS_FLAG")
    if company.get("revenue_band"):
        features.append("revenue_band")
    if company.get("region"):
        features.append("region")
    if company.get("okved_section"):
        features.append("okved_section")
    if graph and graph.get("has_payment_activity"):
        features.append("has_payment_activity")
        if graph.get("supplier_division_shares"):
            features.append("supplier_division_shares")
        if graph.get("client_division_shares"):
            features.append("client_division_shares")
    return features


class Guard:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.audit_path = settings.path("audit", "tool_calls.jsonl")

    def authorize(self, tool: str, role: Role, params: dict[str, Any]) -> None:
        if tool not in ALLOWED_TOOLS:
            raise ToolNotAllowed(f"tool is not allowed: {tool}")
        if role not in set(Role):
            raise ToolNotAllowed(f"unknown role: {role}")
        for key in ("company_id", "event_id"):
            if key in params and not str(params[key]).strip():
                raise ToolNotAllowed(f"empty parameter: {key}")
        if "k" in params and not (1 <= int(params["k"]) <= 10):
            raise ToolNotAllowed("k must be between 1 and 10")

    def audit(
        self,
        tool: str,
        role: Role,
        params: dict[str, Any],
        status: str,
        latency_ms: int,
        result_count: int | None = None,
        error: str | None = None,
    ) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": tool,
            "role": role.value,
            "param_keys": sorted(params.keys()),
            "status": status,
            "latency_ms": latency_ms,
            "result_count": result_count,
            "error": error,
        }
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
