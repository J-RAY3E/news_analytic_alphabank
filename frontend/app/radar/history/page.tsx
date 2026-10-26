"use client";

import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { Card } from "@/components/ui/Card";
import { HistoryPanel } from "@/components/history/HistoryPanel";
import { useAppState } from "@/lib/store";

export default function HistoryPage() {
  const router = useRouter();
  const { companyId, role } = useAppState();

  return (
    <AppShell>
      <div className="p-4 md:p-8">
        <h1 className="text-display-md text-ink">История и сводка</h1>
        <p className="mt-2 text-body-md text-ink-secondary">
          Сохранённые инсайты для выбранного клиента и роли. Откройте запись,
          чтобы вернуться к анализу, источникам и трассировке.
        </p>

        <div className="mt-6 max-w-3xl">
          <Card className="p-6">
            <HistoryPanel
              companyId={companyId}
              role={role}
              activeId={null}
              onOpen={(insightId) =>
                router.push(`/radar?insight=${encodeURIComponent(insightId)}`)
              }
            />
          </Card>
        </div>

        <p className="mt-4 text-micro text-ink-mute">
          Материалы носят аналитический характер и не являются инвестиционной
          рекомендацией.
        </p>
      </div>
    </AppShell>
  );
}
