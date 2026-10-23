from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.contracts import ClaimType, EvidenceClaim


@dataclass
class CriticResult:
    passed: bool
    failed: list[str] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)


REQUIRED_BLOCKS = (
    "what_happened",
    "why_it_matters",
    "consequences",
    "actions",
    "basis",
)


def evaluate(
    blocks: dict[str, list[EvidenceClaim]],
    event_id: str,
    bank_chunks: list[dict[str, Any]],
) -> CriticResult:
    failed: list[str] = []
    checks: list[str] = []

    def check(name: str, condition: bool) -> None:
        checks.append(name)
        if not condition:
            failed.append(name)

    bank_chunks = bank_chunks or []
    for block in REQUIRED_BLOCKS:
        check(f"block_not_empty:{block}", bool(blocks.get(block)))
    bank_view = blocks.get("bank_view") or []
    check("bank_view_empty_without_bank", bool(bank_chunks) or not bank_view)

    for name in REQUIRED_BLOCKS:
        for claim in blocks.get(name) or []:
            if claim.type == ClaimType.FACT and not claim.source_ids:
                failed.append(f"fact_without_source:{name}")
    checks.append("fact_has_source")

    for claim in bank_view:
        if claim.type != ClaimType.BANK_VIEW or not any(
            source.startswith("bank:") for source in claim.source_ids
        ):
            failed.append("bank_view_without_bank_source")
    checks.append("bank_view_cites_bank_source")

    what_happened = blocks.get("what_happened") or []
    check(
        "what_happened_cites_event",
        any(
            claim.type == ClaimType.FACT and event_id in claim.source_ids
            for claim in what_happened
        ),
    )

    if any(claim.company_features for claim in blocks.get("why_it_matters") or []):
        check("why_references_company_features", True)
    else:
        failed.append("why_references_company_features")
        checks.append("why_references_company_features")

    contradictions: list[str] = []
    positive_markers = ("выраст", "увел", "повышен", "рост", "улучш")
    negative_markers = ("сниз", "паден", "сократ", "ухудш", "отрицател")
    for claim in (blocks.get("consequences") or []) + (blocks.get("bank_view") or []):
        if claim.type != ClaimType.AI_INFERENCE:
            continue
        for sentence in claim.text.replace(";", ".").split("."):
            lowered = sentence.casefold()
            if any(marker in lowered for marker in positive_markers) and any(
                marker in lowered for marker in negative_markers
            ):
                contradictions.append(claim.text[:120])
                break
    check("no_obvious_contradictions", not contradictions)

    return CriticResult(
        passed=not failed,
        failed=failed,
        checks=checks,
    )
