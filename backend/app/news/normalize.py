from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.contracts import NormalizedEvent

TOKEN_RE = re.compile(r"[a-zA-Zа-яА-ЯёЁ0-9]+")
WHITESPACE_RE = re.compile(r"\s+")

STOPWORDS = {
    "и",
    "в",
    "во",
    "на",
    "с",
    "со",
    "по",
    "для",
    "из",
    "от",
    "до",
    "о",
    "об",
    "при",
    "как",
    "что",
    "это",
    "не",
    "но",
    "а",
    "или",
    "за",
    "к",
    "у",
    "же",
    "бы",
    "ли",
    "the",
    "of",
    "to",
}


def normalize_whitespace(text: str) -> str:
    return WHITESPACE_RE.sub(" ", text.replace("\xa0", " ")).strip()


def canonical_title(title: str) -> str:
    lowered = normalize_whitespace(title).casefold()
    lowered = re.sub(r"[^\w\s-]", " ", lowered, flags=re.UNICODE)
    return normalize_whitespace(lowered)


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in TOKEN_RE.findall(canonical_title(text))
        if len(token) > 2 and token not in STOPWORDS
    ]


def token_set(text: str) -> set[str]:
    return set(tokenize(text))


def jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    intersection = len(left & right)
    union = len(left | right)
    return intersection / union if union else 0.0


def event_similarity(left: NormalizedEvent, right: NormalizedEvent) -> float:
    title_score = jaccard(token_set(left.title), token_set(right.title))
    summary_score = jaccard(
        token_set(left.summary or left.raw_text),
        token_set(right.summary or right.raw_text),
    )
    if canonical_title(left.title) == canonical_title(right.title):
        title_score = 1.0
    return round(0.65 * title_score + 0.35 * summary_score, 6)


@dataclass
class DedupeResult:
    unique: list[NormalizedEvent] = field(default_factory=list)
    duplicates: dict[str, str] = field(default_factory=dict)
    clusters: dict[str, str] = field(default_factory=dict)


def dedupe_events(
    events: list[NormalizedEvent], threshold: float = 0.88
) -> DedupeResult:
    result = DedupeResult()
    for event in events:
        match: NormalizedEvent | None = None
        best_score = 0.0
        for candidate in result.unique:
            score = event_similarity(event, candidate)
            if score > best_score:
                best_score = score
                match = candidate
        if match is not None and best_score >= threshold:
            result.duplicates[event.event_id] = match.event_id
            result.clusters[event.event_id] = result.clusters.get(
                match.event_id, match.event_id
            )
        else:
            result.unique.append(event)
            result.clusters[event.event_id] = event.event_id
    return result


def find_duplicate(
    event: NormalizedEvent, existing: list[NormalizedEvent], threshold: float = 0.88
) -> tuple[NormalizedEvent | None, float]:
    best: NormalizedEvent | None = None
    best_score = 0.0
    for candidate in existing:
        score = event_similarity(event, candidate)
        if score > best_score:
            best = candidate
            best_score = score
    if best is not None and best_score >= threshold:
        return best, best_score
    return None, best_score
