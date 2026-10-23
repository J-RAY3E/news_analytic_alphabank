"use client";

import { useCompanies, useFeed } from "@/lib/api/hooks";
import { useAppState } from "@/lib/store";
import type { FeedItem, NormalizedEvent } from "@/lib/api/types";
import { FeedCard } from "./FeedCard";
import { ClientRoleSwitcher } from "./ClientRoleSwitcher";
import { NewsTestInput } from "@/components/news/NewsTestInput";
import { FeedCardSkeleton } from "@/components/ui/Skeleton";
import { Button } from "@/components/ui/Button";
import { ROLE_SHORT } from "@/lib/api/types";

export function FeedPanel({
  selectedEventId,
  onSelect,
  onIngestedEvent,
}: {
  selectedEventId: string | null;
  onSelect: (item: FeedItem) => void;
  onIngestedEvent: (event: NormalizedEvent) => void;
}) {
  const { companyId, setCompanyId, role, setRole } = useAppState();
  const companies = useCompanies();
  const feed = useFeed(companyId, role);

  const company = feed.data?.company ?? companies.data?.find((c) => c.company_id === companyId) ?? null;

  return (
    <div className="flex flex-col gap-4">
      <ClientRoleSwitcher
        company={company}
        companies={companies.data ?? []}
        onCompanyChange={setCompanyId}
        role={role}
        onRoleChange={setRole}
      />

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
            Сервер не вернул события. Проверьте, что backend запущен, и повторите попытку.
          </p>
          <div className="mt-4">
            <Button variant="secondary" onClick={() => feed.refetch()}>
              Повторить
            </Button>
          </div>
        </div>
      )}

      {feed.data && feed.data.items.length === 0 && (
        <div className="rounded-lg border border-hairline bg-canvas p-6">
          <p className="text-display-md text-ink">Событий нет</p>
          <p className="mt-2 text-body-md text-ink-secondary">
            Для выбранного клиента и роли релевантных событий не найдено. Попробуйте сменить клиента.
          </p>
          <div className="mt-4">
            <Button
              variant="secondary"
              onClick={() => {
                const first = companies.data?.[0];
                if (first) setCompanyId(first.company_id);
              }}
            >
              Сменить клиента
            </Button>
          </div>
        </div>
      )}

      {feed.data && (
        <div className="space-y-3">
          {feed.data.items.map((item) => (
            <FeedCard
              key={item.event.event_id}
              item={item}
              selected={item.event.event_id === selectedEventId}
              onSelect={() => onSelect(item)}
            />
          ))}
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
