"use client";

import { formatRub } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { useBudget } from "@/lib/api/hooks";

export function BudgetMeter() {
  const budget = useBudget();
  const spentRub = budget.data?.spent_rub ?? 0;
  const budgetRub = budget.data?.budget_rub ?? 500;
  const model = budget.data?.model ?? "—";
  const cacheHits = budget.data?.cache_hits ?? 0;
  const ratio = budgetRub > 0 ? Math.min(spentRub / budgetRub, 1) : 0;
  const pct = (ratio * 100).toLocaleString("ru-RU", { maximumFractionDigits: 0 });
  const status = budget.isLoading ? "загрузка" : budget.isError ? "нет данных" : "live";

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <span className="text-caption text-ink-secondary">Бюджет моделей за день</span>
        <span className="rounded-pill bg-canvas-soft px-2 py-[2px] text-micro text-ink-secondary">
          {status}
        </span>
      </div>
      <div className="mt-2 flex items-baseline gap-2 tnum">
        <span className="text-heading-sm">{formatRub(spentRub)}</span>
        <span className="text-caption text-ink-mute">из {formatRub(budgetRub)}</span>
      </div>
      <div
        className="mt-3 h-1.5 w-full rounded-pill bg-hairline"
        role="progressbar"
        aria-valuenow={Math.round(ratio * 100)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label="Использованный дневной бюджет"
      >
        <div className="h-1.5 rounded-pill bg-blue" style={{ width: `${pct}%` }} />
      </div>
      <div className="mt-3 flex items-center justify-between text-caption text-ink-secondary">
        <span>Модель: {model}</span>
        <span className="tnum">Кэш-попаданий: {cacheHits}</span>
      </div>
    </Card>
  );
}
