"use client";

import type { Role } from "@/lib/api/types";
import { useInsights } from "@/lib/api/hooks";
import { cn, formatDateTime, formatScore } from "@/lib/utils";

export function HistoryPanel({
  companyId,
  role,
  activeId,
  onOpen,
}: {
  companyId: string | null;
  role: Role;
  activeId: string | null;
  onOpen: (insightId: string) => void;
}) {
  const history = useInsights(companyId, role, 8);
  if (!companyId) return null;

  return (
    <div className="mt-4">
      <h3 className="text-heading-sm text-ink">История инсайтов</h3>
      {history.isLoading && (
        <p className="mt-2 text-micro text-ink-mute">Загрузка…</p>
      )}
      {history.data && history.data.items.length === 0 && (
        <p className="mt-2 text-micro text-ink-mute">
          Пока нет сохранённых инсайтов для этого клиента и роли.
        </p>
      )}
      <ul className="mt-2 space-y-1.5">
        {history.data?.items.map((item) => (
          <li key={item.insight_id}>
            <button
              type="button"
              onClick={() => onOpen(item.insight_id)}
              className={cn(
                "w-full rounded-md border border-hairline bg-canvas px-3 py-2 text-left transition-shadow hover:shadow-level-1",
                activeId === item.insight_id && "bg-canvas-soft"
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="truncate text-body-md text-ink">
                  {item.event_title ?? item.event_id}
                </span>
                <span className="shrink-0 text-caption tnum text-ink-mute">
                  {formatScore(item.relevance_score)}
                </span>
              </div>
              <span className="mt-0.5 block text-micro text-ink-mute">
                {item.created_at ? formatDateTime(item.created_at) : ""}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
