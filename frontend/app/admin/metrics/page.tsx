"use client";

import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/ui/Card";
import { BudgetMeter } from "@/components/home/BudgetMeter";
import { useMetrics } from "@/lib/api/hooks";
import { formatNumber } from "@/lib/utils";

export default function AdminMetricsPage() {
  const metrics = useMetrics();
  const data = metrics.data;

  const cards: { label: string; value: string; hint?: string }[] = [
    {
      label: "Событий в ленте",
      value: formatNumber(data?.events_total ?? 0, 0),
    },
    {
      label: "Сохранённых инсайтов",
      value: formatNumber(data?.insights_total ?? 0, 0),
    },
    {
      label: "Отзывов",
      value: formatNumber(data?.feedback_total ?? 0, 0),
    },
    {
      label: "Доля «Полезно»",
      value:
        data?.thumbs_up_ratio != null
          ? `${formatNumber(data.thumbs_up_ratio * 100, 0)}%`
          : "—",
    },
    {
      label: "Покрытие источниками",
      value: `${formatNumber((data?.source_coverage ?? 0) * 100, 0)}%`,
    },
    {
      label: "Средняя стоимость инсайта",
      value:
        data?.avg_cost_rub != null
          ? `${formatNumber(data.avg_cost_rub, 3)} руб.`
          : "—",
    },
    {
      label: "Средняя задержка",
      value:
        data?.avg_latency_ms != null
          ? `${formatNumber(data.avg_latency_ms / 1000, 1)} с`
          : "—",
    },
  ];

  return (
    <AppShell>
      <div className="p-4 md:p-8">
        <h1 className="text-display-md text-ink">Метрики качества и стоимости</h1>
        <p className="mt-2 text-body-md text-ink-secondary">
          Служебная страница. Недоступна из клиентской части, кроме ссылки в
          подвале. Модели берутся только из согласованного списка.
        </p>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <BudgetMeter />
          {cards.map((card) => (
            <Card key={card.label} className="p-6">
              <p className="text-caption text-ink-secondary">{card.label}</p>
              <p className="mt-1 text-number-score tnum text-ink">{card.value}</p>
            </Card>
          ))}
        </div>

        {metrics.isError && (
          <p className="mt-4 text-body-md text-ink-secondary">
            Не удалось загрузить метрики. Проверьте соединение с сервером.
          </p>
        )}
      </div>
    </AppShell>
  );
}
