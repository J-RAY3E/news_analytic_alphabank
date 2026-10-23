"use client";

import { useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { RadarWidget } from "@/components/home/RadarWidget";
import { BudgetMeter } from "@/components/home/BudgetMeter";
import { Card } from "@/components/ui/Card";
import { useCompanies } from "@/lib/api/hooks";
import { useAppState } from "@/lib/store";
import { Skeleton } from "@/components/ui/Skeleton";

export default function HomePage() {
  const companies = useCompanies();
  const { companyId, setCompanyId } = useAppState();

  useEffect(() => {
    if (!companyId && companies.data && companies.data.length > 0) {
      setCompanyId(companies.data[0].company_id);
    }
  }, [companyId, companies.data, setCompanyId]);

  const currentCompany = companies.data?.find((c) => c.company_id === companyId);

  return (
    <AppShell>
      <div className="p-4 md:p-8">
        <h1 className="text-display-md text-ink">Главная</h1>

        <div className="mt-6 grid gap-4 lg:grid-cols-2">
          <div className="lg:col-span-2">
            <RadarWidget />
          </div>

          <Card className="p-6">
            <h2 className="text-heading-sm text-ink">Текущий клиент</h2>
            {companies.isLoading && (
              <div className="mt-3 space-y-2">
                <Skeleton className="h-4 w-1/2" />
                <Skeleton className="h-4 w-1/3" />
              </div>
            )}
            {currentCompany && (
              <dl className="mt-3 space-y-2 text-body-md">
                <div className="flex justify-between gap-4">
                  <dt className="text-ink-secondary">Клиент</dt>
                  <dd className="text-ink">{currentCompany.display_name}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-ink-secondary">Отрасль</dt>
                  <dd className="text-ink">{currentCompany.industry_label}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-ink-secondary">Выручка</dt>
                  <dd className="text-ink tnum">{currentCompany.revenue_band}</dd>
                </div>
                <div className="flex justify-between gap-4">
                  <dt className="text-ink-secondary">Регион</dt>
                  <dd className="text-ink">{currentCompany.region}</dd>
                </div>
              </dl>
            )}
            {companies.isError && (
              <p className="mt-3 text-body-md text-ink-secondary">
                Не удалось загрузить список клиентов. Проверьте соединение с сервером.
              </p>
            )}
          </Card>

          <BudgetMeter spentRub={214.6} budgetRub={500} model="GLM-5.3-Flash" cacheHits={12} />
        </div>
      </div>
    </AppShell>
  );
}
