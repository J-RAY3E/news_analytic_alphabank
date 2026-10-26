"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useCompanies, useFeed } from "@/lib/api/hooks";
import { useAppState } from "@/lib/store";
import type { FeedItem, NormalizedEvent } from "@/lib/api/types";
import { FeedCard } from "./FeedCard";
import { CompanyProfilePanel } from "@/components/insight/CompanyProfilePanel";
import { NewsTestInput } from "@/components/news/NewsTestInput";
import { FeedCardSkeleton } from "@/components/ui/Skeleton";
import { Button } from "@/components/ui/Button";
import { ROLE_SHORT } from "@/lib/api/types";
import { cn, pluralRu } from "@/lib/utils";

const PERIODS = [
  { key: "day", label: "Сегодня", days: 1 },
  { key: "week", label: "Неделя", days: 7 },
  { key: "month", label: "Месяц", days: 30 },
  { key: "all", label: "Всё время", days: null },
] as const;

type PeriodKey = (typeof PERIODS)[number]["key"];

export function FeedPanel({
  selectedEventId,
  onSelect,
  onIngestedEvent,
}: {
  selectedEventId: string | null;
  onSelect: (item: FeedItem) => void;
  onIngestedEvent: (event: NormalizedEvent) => void;
}) {
  const { companyId, role } = useAppState();
  const companies = useCompanies();
  const feed = useFeed(companyId, role);
  const [period, setPeriod] = useState<PeriodKey>("all");
  const [hidden, setHidden] = useState<Set<string>>(new Set());
  const [showHidden, setShowHidden] = useState(false);

  const company =
    feed.data?.company ??
    companies.data?.find((c) => c.company_id === companyId) ??
    null;

  const items = useMemo(() => {
    const all = feed.data?.items ?? [];
    const cfg = PERIODS.find((p) => p.key === period);
    if (!cfg || cfg.days == null) return all;
    const cutoff = Date.now() - cfg.days * 86400000;
    return all.filter((item) => {
      const iso = item.event.published_at;
      if (!iso) return true;
      const t = new Date(iso).getTime();
      return Number.isNaN(t) ? true : t >= cutoff;
    });
  }, [feed.data, period]);

  const visible = items.filter((item) => !hidden.has(item.event.event_id));
  const hiddenItems = items.filter((item) => hidden.has(item.event.event_id));

  const freshness = useMemo(() => {
    if (!feed.dataUpdatedAt) return "";
    const mins = Math.max(0, Math.round((Date.now() - feed.dataUpdatedAt) / 60000));
    if (mins === 0) return "Обновлено только что";
    return `Обновлено ${mins} ${pluralRu(mins, "минуту", "минуты", "минут")} назад`;
  }, [feed.dataUpdatedAt]);

  const hide = (id: string) =>
    setHidden((prev) => new Set(prev).add(id));
  const unhide = (id: string) =>
    setHidden((prev) => {
      const next = new Set(prev);
      next.delete(id);
      return next;
    });

  return (
    <div className="flex flex-col gap-4">
      <CompanyProfilePanel company={company} compact />

      <div className="flex items-center justify-between gap-2">
        <span className="text-micro text-ink-mute">{freshness}</span>
        <Link href="/radar/history" className="text-caption text-blue-deep underline">
          История
        </Link>
      </div>

      <div className="flex flex-wrap gap-1" role="tablist" aria-label="Период">
        {PERIODS.map((p) => (
          <button
            key={p.key}
            type="button"
            role="tab"
            aria-selected={period === p.key}
            onClick={() => setPeriod(p.key)}
            className={cn(
              "min-h-[32px] rounded-pill px-3 text-caption transition-colors",
              period === p.key
                ? "bg-surface-dark-raised text-on-primary"
                : "bg-canvas-track text-ink-secondary hover:bg-canvas-grey"
            )}
          >
            {p.label}
          </button>
        ))}
      </div>

      {feed.isLoading && (
        <div className="space-y-3" aria-label="Загрузка ленты">
          <FeedCardSkeleton />
          <FeedCardSkeleton />
          <FeedCardSkeleton />
        </div>
      )}

      {feed.isError && (
        <div className="rounded-lg border border-hairline bg-canvas p-6">
          <p className="text-heading-md text-ink">Лента недоступна</p>
          <p className="mt-2 text-body-md text-ink-secondary">
            Сервер не вернул события. Проверьте, что backend запущен, и повторите
            попытку.
          </p>
          <div className="mt-4">
            <Button variant="secondary" onClick={() => feed.refetch()}>
              Повторить
            </Button>
          </div>
        </div>
      )}

      {feed.data && items.length === 0 && (
        <div className="rounded-lg border border-hairline bg-canvas p-6">
          <p className="text-display-md text-ink">Событий нет</p>
          <p className="mt-2 text-body-md text-ink-secondary">
            Для выбранного клиента, роли и периода релевантных событий не найдено.
          </p>
        </div>
      )}

      {visible.length > 0 && (
        <div className="space-y-3">
          {visible.map((item) => (
            <FeedCard
              key={item.event.event_id}
              item={item}
              selected={item.event.event_id === selectedEventId}
              onSelect={() => onSelect(item)}
              onHide={() => hide(item.event.event_id)}
            />
          ))}
        </div>
      )}

      {hiddenItems.length > 0 && (
        <div>
          <button
            type="button"
            onClick={() => setShowHidden((v) => !v)}
            className="text-caption text-ink-secondary underline"
          >
            {showHidden
              ? "Скрыть скрытые"
              : `Показать скрытые (${hiddenItems.length})`}
          </button>
          {showHidden && (
            <div className="mt-2 space-y-2">
              {hiddenItems.map((item) => (
                <div
                  key={item.event.event_id}
                  className="flex items-center justify-between gap-3 rounded-lg bg-canvas-soft px-4 py-3"
                >
                  <span className="truncate text-body-md text-ink-mute">
                    {item.event.title}
                  </span>
                  <button
                    type="button"
                    onClick={() => unhide(item.event.event_id)}
                    className="shrink-0 text-caption text-blue-deep underline"
                  >
                    Показать
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      <NewsTestInput
        companyId={companyId}
        role={ROLE_SHORT[role]}
        onInsightReady={onIngestedEvent}
      />
    </div>
  );
}
