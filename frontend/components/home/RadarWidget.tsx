"use client";

import { useRouter } from "next/navigation";
import { useFeed, useCompanies } from "@/lib/api/hooks";
import { useAppState } from "@/lib/store";
import { formatScore } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";

export function RadarWidget() {
  const router = useRouter();
  const { companyId, setCompanyId } = useAppState();
  const companies = useCompanies();
  const effectiveCompanyId = companyId ?? companies.data?.[0]?.company_id ?? null;

  const feed = useFeed(effectiveCompanyId, "CEO", 1);

  if (!companyId && companies.data?.[0]) {
    setCompanyId(companies.data[0].company_id);
  }

  return (
    <div className="overflow-hidden rounded-xl bg-canvas shadow-level-1">
      <div
        className="h-24 bg-cover bg-center"
        style={{ backgroundImage: "url('/mesh.svg')" }}
        aria-hidden
      />
      <div className="p-6">
        <h2 className="text-heading-lg text-ink">Radar</h2>
        <p className="mt-1 text-body-md text-ink-secondary">
          Персональные выводы из новостей для вашей компании: что произошло, почему важно и что делать.
        </p>

        {effectiveCompanyId === null && companies.isLoading && (
          <div className="mt-4 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        )}

        {feed.isLoading && effectiveCompanyId !== null && (
          <div className="mt-4 space-y-2">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        )}

        {feed.isError && (
          <p className="mt-4 text-body-md text-ink-secondary">
            Не удалось загрузить топ-событие. Откройте Radar, чтобы посмотреть ленту.
          </p>
        )}

        {feed.data && feed.data.items.length > 0 && (
          <div className="mt-4 rounded-lg bg-canvas-soft p-4">
            <div className="flex items-start justify-between gap-3">
              <p className="text-body-md text-ink">{feed.data.items[0].event.title}</p>
              <span className="shrink-0 rounded-pill bg-blue-bg px-2 py-1 text-caption tnum text-blue-deep">
                {formatScore(feed.data.items[0].relevance_score)}
              </span>
            </div>
            <p className="mt-2 text-caption text-ink-secondary">
              {feed.data.items[0].reasons[0]}
            </p>
          </div>
        )}

        {feed.data && feed.data.items.length === 0 && (
          <p className="mt-4 text-body-md text-ink-secondary">
            Для текущего клиента релевантных событий нет.
          </p>
        )}

        <div className="mt-5">
          <Button variant="primary" onClick={() => router.push("/radar")}>
            Открыть Radar
          </Button>
        </div>
      </div>
    </div>
  );
}
