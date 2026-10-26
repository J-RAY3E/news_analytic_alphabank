"use client";

import { useCallback, useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { Workspace } from "@/components/layout/Workspace";
import { FeedPanel } from "@/components/feed/FeedPanel";
import { InsightView } from "@/components/insight/InsightView";
import { SourceDrawer } from "@/components/insight/SourceDrawer";
import { TracePanel } from "@/components/trace/TracePanel";
import { InsightSectionSkeleton } from "@/components/ui/Skeleton";
import { Button } from "@/components/ui/Button";
import { useCompanies, useInsight } from "@/lib/api/hooks";
import { dataApi } from "@/lib/mocks/api";
import { DisclaimerBanner } from "@/components/ui/DisclaimerBanner";
import { useAppState } from "@/lib/store";
import type { FeedItem, InsightResponse, NormalizedEvent } from "@/lib/api/types";

function cardToEvent(item: FeedItem): NormalizedEvent {
  const e = item.event;
  return {
    event_id: e.event_id,
    title: e.title,
    summary: e.summary,
    event_type: e.event_type,
    sectors: e.sectors,
    regions: e.regions,
    countries: e.countries,
    macro_factors: e.macro_factors,
    sentiment: e.sentiment,
    risk_opportunity: e.risk_opportunity,
    source: {
      source_id: e.event_id,
      name: e.source_name,
      url: e.source_url ?? null,
      published_at: e.published_at ?? null,
      language: "ru",
    },
  };
}

export default function RadarPage() {
  const { companyId, user } = useAppState();
  const companies = useCompanies();
  const insightMutation = useInsight();

  const [selectedEvent, setSelectedEvent] = useState<NormalizedEvent | null>(null);
  const [insight, setInsight] = useState<InsightResponse | null>(null);
  const [sourceId, setSourceId] = useState<string | null>(null);

  const requestInsight = useCallback(
    (event: NormalizedEvent) => {
      if (!companyId) return;
      setSelectedEvent(event);
      insightMutation.mutate(
        { company_id: companyId, event_id: event.event_id, role: undefined },
        {
          onSuccess: (data) => setInsight(data),
        }
      );
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [companyId]
  );

  const onSelect = (item: FeedItem) => {
    if (item.event.event_id === selectedEvent?.event_id) return;
    requestInsight(cardToEvent(item));
  };

  useEffect(() => {
    if (!companyId) return;
    const param = new URLSearchParams(window.location.search).get("insight");
    if (param) void openHistoryInsight(param);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [companyId]);

  const openHistoryInsight = useCallback(
    async (insightId: string) => {
      if (!companyId) return;
      try {
        const stored = await dataApi.getInsight(insightId);
        setInsight(stored);
        try {
          const detail = await dataApi.getEvent(stored.event_id);
          setSelectedEvent(detail.event);
        } catch {
          setSelectedEvent(null);
        }
      } catch {
        // ignore: history item could not be loaded
      }
    },
    [companyId]
  );

  const company =
    companies.data?.find((c) => c.company_id === companyId) ?? null;
  const companyName = company?.display_name ?? "Клиент";

  const insightContent = () => {
    if (!selectedEvent) {
      return (
        <div className="rounded-lg border border-hairline bg-canvas p-8">
          <p className="text-display-md text-ink">Выберите событие</p>
          <p className="mt-2 text-body-md text-ink-secondary">
            Откройте событие из ленты слева: здесь появятся шесть ответов с метками Факт, Позиция
            банка и Вывод ИИ, а справа шаги агента.
          </p>
        </div>
      );
    }
    if (insightMutation.isPending) {
      return (
        <div className="space-y-4" aria-label="Формирование вывода">
          <InsightSectionSkeleton />
          <InsightSectionSkeleton />
          <InsightSectionSkeleton />
          <p className="text-center text-caption text-ink-mute">
            Агент анализирует событие: обычно это занимает до 30 секунд.
          </p>
        </div>
      );
    }
    if (insightMutation.isError || !insight) {
      return (
        <div className="rounded-lg border border-hairline bg-canvas p-8">
          <p className="text-heading-md text-ink">Не удалось сформировать вывод</p>
          <p className="mt-2 text-body-md text-ink-secondary">
            {insightMutation.error instanceof Error
              ? insightMutation.error.message
              : "Сервер вернул ошибку."}
          </p>
          <div className="mt-4">
            <Button variant="secondary" onClick={() => requestInsight(selectedEvent)}>
              Повторить
            </Button>
          </div>
        </div>
      );
    }
    return (
      <InsightView
        insight={insight}
        event={selectedEvent}
        company={company}
        companyName={companyName}
        userName={user?.id ?? "guest"}
        onOpenSource={setSourceId}
      />
    );
  };

  return (
    <AppShell>
      <div className="px-4 pt-4 md:px-6">
        <DisclaimerBanner />
      </div>
      <Workspace
        feed={
          <FeedPanel
            selectedEventId={selectedEvent?.event_id ?? null}
            onSelect={onSelect}
            onIngestedEvent={requestInsight}
          />
        }
        insight={insightContent()}
        trace={<TracePanel insight={insight} />}
      />
      <SourceDrawer sourceId={sourceId} onClose={() => setSourceId(null)} />
    </AppShell>
  );
}
