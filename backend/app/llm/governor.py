from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from app.llm.config import LLMConfig

MOSCOW = ZoneInfo("Europe/Moscow")


class BudgetExceeded(Exception):
    def __init__(self, spent: float, budget: float, estimated: float) -> None:
        super().__init__(
            f"daily LLM budget exceeded: spent={spent:.4f} budget={budget:.2f} "
            f"estimated={estimated:.4f}"
        )
        self.spent = spent
        self.budget = budget
        self.estimated = estimated


@dataclass(frozen=True)
class UsageRecord:
    day: str
    timestamp: str
    model: str
    purpose: str
    prompt_tokens: int
    completion_tokens: int
    estimated_cost_rub: float
    cached: bool = False


class CostGovernor:
    def __init__(self, config: LLMConfig, usage_path: str | Path) -> None:
        self.config = config
        self.usage_path = Path(usage_path)

    @staticmethod
    def current_day() -> str:
        return datetime.now(MOSCOW).date().isoformat()

    def _records(self) -> list[dict]:
        if not self.usage_path.exists():
            return []
        records: list[dict] = []
        with self.usage_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return records

    def spent_today(self) -> float:
        day = self.current_day()
        return round(
            sum(
                float(record.get("estimated_cost_rub", 0.0))
                for record in self._records()
                if record.get("day") == day
            ),
            6,
        )

    def remaining(self) -> float:
        return round(max(self.config.daily_budget_rub - self.spent_today(), 0.0), 6)

    def check(self, estimated_cost: float = 0.0) -> None:
        spent = self.spent_today()
        if spent + estimated_cost > self.config.daily_budget_rub:
            raise BudgetExceeded(spent, self.config.daily_budget_rub, estimated_cost)

    def record(self, record: UsageRecord) -> None:
        self.usage_path.parent.mkdir(parents=True, exist_ok=True)
        with self.usage_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.__dict__, ensure_ascii=False) + "\n")

    def record_usage(
        self,
        model: str,
        purpose: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_rub: float,
        cached: bool = False,
    ) -> None:
        self.record(
            UsageRecord(
                day=self.current_day(),
                timestamp=datetime.now(timezone.utc).isoformat(),
                model=model,
                purpose=purpose,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                estimated_cost_rub=round(cost_rub, 6),
                cached=cached,
            )
        )

    def summary(self) -> dict:
        spent = self.spent_today()
        return {
            "day": self.current_day(),
            "spent_rub": spent,
            "budget_rub": self.config.daily_budget_rub,
            "remaining_rub": round(max(self.config.daily_budget_rub - spent, 0.0), 6),
        }
