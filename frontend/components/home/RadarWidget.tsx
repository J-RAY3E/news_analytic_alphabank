"use client";

import { useRouter } from "next/navigation";
import { useFeed, useCompanies } from "@/lib/api/hooks";
import { useAppState } from "@/lib/store";
import { formatScore, formatTime } from "@/lib/utils";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { ImpactChip } from "@/components/ui/chips";

const SPECIFIC_FACTORS = new Set([
  "product_match",
  "supply_chain_exposure",
  "geo_match",
]);

export function RadarWidget() {
  const router = useRouter();
  const { companyId, setCompanyId } = useAppState();
  const companies = useCompanies();
  const effectiveCompanyId = companyId ?? companies.data?.[0]?.company_id ?? null;

  const feed = useFeed(effectiveCompanyId, "CEO", 3);

  if (!companyId && companies.data?.[0]) {
    setCompanyId(companies.data[0].company_id);
  }

  const items = feed.data?.items ?? [];
  const top =
    items.find((item) =>
      item.factors.some(
        (factor) => SPECIFIC_FACTORS.has(factor.name) && factor.value > 0
      )
    ) ?? items[0];

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
          Персональные выводы из новостей для вашей компании: что произошло, почему
          важно и что делать.
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

        {top && (
          <div className="mt-4 rounded-lg bg-canvas-soft p-4">
            <div className="flex items-start justify-between gap-3">
              <p className="text-body-md text-ink">{top.event.title}</p>
              <span className="shrink-0 rounded-pill bg-blue-bg px-2 py-1 text-caption tnum text-blue-deep">
                Релевантность {formatScore(top.relevance_score)}
              </span>
            </div>
            <p className="mt-2 text-caption text-ink-secondary">{top.reasons[0]}</p>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              {top.impact && <ImpactChip impact={top.impact} />}
              <span className="text-micro text-ink-mute">
                {top.event.source_name}
                {top.event.published_at ? ` · ${formatTime(top.event.published_at)}` : ""}
              </span>
            </div>
          </div>
        )}

        {feed.data && items.length === 0 && (
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
