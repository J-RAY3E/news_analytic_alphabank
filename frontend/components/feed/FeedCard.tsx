"use client";

import { useState } from "react";
import type { FeedItem } from "@/lib/api/types";
import { EVENT_TYPE_LABELS, FACTOR_NAME_LABELS, MACRO_FACTOR_LABELS } from "@/lib/api/types";
import { cn, formatScore, formatTime } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { DirectionChip, ReasonChip, ScoreBadge } from "@/components/ui/chips";

export function ScorePopover({ item, onClose }: { item: FeedItem; onClose: () => void }) {
  return (
    <div
      className="absolute right-0 top-8 z-20 w-72 rounded-lg bg-canvas p-4 shadow-level-2 border border-hairline"
      role="dialog"
      aria-label="Разбор оценки релевантности"
    >
      <div className="flex items-center justify-between">
        <span className="text-caption text-ink-secondary">Вклад факторов</span>
        <button
          type="button"
          onClick={onClose}
          className="min-h-[36px] rounded-sm px-2 text-caption text-ink-secondary hover:bg-canvas-soft"
        >
          Закрыть
        </button>
      </div>
      <table className="mt-2 w-full text-body-tabular">
        <thead>
          <tr className="text-left text-ink-secondary">
            <th className="pb-1 font-normal">Фактор</th>
            <th className="pb-1 font-normal">Вклад</th>
          </tr>
        </thead>
        <tbody className="tnum">
          {item.factors.map((f) => (
            <tr key={f.name} className="border-t border-hairline">
              <td className="py-1.5 pr-2">{FACTOR_NAME_LABELS[f.name] ?? f.name}</td>
              <td className="py-1.5">
                {f.contribution.toLocaleString("ru-RU", { minimumFractionDigits: 3, maximumFractionDigits: 3 })}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-t border-hairline font-medium">
            <td className="py-1.5">Итог</td>
            <td className="py-1.5">{formatScore(item.relevance_score)}</td>
          </tr>
        </tfoot>
      </table>
      <ul className="mt-2 space-y-1">
        {item.factors.map((f) => (
          <li key={f.name} className="text-micro text-ink-mute">
            {FACTOR_NAME_LABELS[f.name] ?? f.name}: {f.explanation}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function FeedCard({
  item,
  selected,
  onSelect,
}: {
  item: FeedItem;
  selected: boolean;
  onSelect: () => void;
}) {
  const [popoverOpen, setPopoverOpen] = useState(false);
  const { event } = item;
  const time = formatTime(event.published_at);

  return (
    <Card
      elevation={selected ? 1 : 0}
      className={cn(
        "relative cursor-pointer p-6 transition-shadow hover:shadow-level-1",
        selected && "border-l-[2px] border-l-primary bg-canvas-soft"
      )}
    >
      <div
        onClick={onSelect}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onSelect();
          }
        }}
        role="button"
        tabIndex={0}
        aria-pressed={selected}
        className="text-left"
      >
        <div className="flex items-center justify-between gap-2">
          <span className="text-caption text-ink-mute">
            {event.source_name}
            {time ? ` · ${time}` : ""}
          </span>
          <div className="relative">
            <ScoreBadge
              score={item.relevance_score}
              active={popoverOpen}
              onClick={() => setPopoverOpen((v) => !v)}
            />
            {popoverOpen && <ScorePopover item={item} onClose={() => setPopoverOpen(false)} />}
          </div>
        </div>

        <h3 className="mt-3 text-heading-md text-ink line-clamp-2">{event.title}</h3>

        <p className="mt-2 text-body-md text-ink-secondary">{item.reasons[0]}</p>

        <div className="mt-3 flex flex-wrap gap-1.5">
          <ReasonChip>{EVENT_TYPE_LABELS[event.event_type]}</ReasonChip>
          {event.macro_factors.slice(0, 2).map((mf) => (
            <ReasonChip key={mf}>{MACRO_FACTOR_LABELS[mf]}</ReasonChip>
          ))}
          <DirectionChip direction={event.risk_opportunity} />
        </div>
      </div>
    </Card>
  );
}
