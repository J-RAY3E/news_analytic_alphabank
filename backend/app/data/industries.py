from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

DIVISION_RE = re.compile(r"^\s*(\d{1,2})")


class IndustryCatalog(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str
    sections: dict[str, str]
    division_ranges: dict[str, list[int]]
    section_keywords: dict[str, list[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def ranges_consistent(self) -> IndustryCatalog:
        for section, bounds in self.division_ranges.items():
            if section not in self.sections:
                raise ValueError(f"division range for unknown section {section}")
            if len(bounds) != 2 or bounds[0] > bounds[1]:
                raise ValueError(f"invalid division range for {section}: {bounds}")
        return self

    def division_of(self, okved: str | None) -> str | None:
        if okved is None:
            return None
        match = DIVISION_RE.match(str(okved))
        if not match:
            return None
        return f"{int(match.group(1)):02d}"

    def section_of_division(self, division: str | int | None) -> str | None:
        if division is None:
            return None
        try:
            value = int(division)
        except (TypeError, ValueError):
            return None
        for section, (low, high) in self.division_ranges.items():
            if low <= value <= high:
                return section
        return None

    def section_of_okved(self, okved: str | None) -> str | None:
        return self.section_of_division(self.division_of(okved))

    def section_label(self, section: str | None) -> str:
        if section is None:
            return "Неизвестная отрасль"
        return self.sections.get(section, "Неизвестная отрасль")

    def infer_sections_from_text(self, text: str) -> list[str]:
        lowered = text.casefold()
        found: list[str] = []
        for section, keywords in self.section_keywords.items():
            if any(keyword.casefold() in lowered for keyword in keywords):
                found.append(section)
        return found

    def sector_labels(self, sections: list[str]) -> list[str]:
        return [self.section_label(section) for section in sections]


@lru_cache
def load_industry_catalog(path: str | Path) -> IndustryCatalog:
    resolved = Path(path).resolve()
    with resolved.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"industry catalog must be a mapping: {resolved}")
    return IndustryCatalog.model_validate(payload)
