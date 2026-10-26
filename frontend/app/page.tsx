"use client";

import { useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { RadarWidget } from "@/components/home/RadarWidget";
import { BankTile } from "@/components/home/BankTile";
import { CompanyProfilePanel } from "@/components/insight/CompanyProfilePanel";
import { DisclaimerBanner } from "@/components/ui/DisclaimerBanner";
import { Card } from "@/components/ui/Card";
import { useCompanies } from "@/lib/api/hooks";
import { useAppState } from "@/lib/store";
import { Skeleton } from "@/components/ui/Skeleton";

export default function HomePage() {
  const companies = useCompanies();
  const { companyId, setCompanyId } = useAppState();

  useEffect(() => {
    if (
      companyId &&
      companies.data &&
      !companies.data.some((c) => c.company_id === companyId)
    ) {
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

          <div className="lg:col-span-2">
            <DisclaimerBanner />
          </div>

          {companies.isLoading && (
            <Card className="p-6">
              <Skeleton className="h-4 w-1/3" />
              <div className="mt-3 space-y-2">
                <Skeleton className="h-4 w-1/2" />
                <Skeleton className="h-4 w-1/3" />
              </div>
            </Card>
          )}

          {currentCompany && <CompanyProfilePanel company={currentCompany} />}

          <BankTile />

          {companies.isError && (
            <Card className="p-6">
              <p className="text-body-md text-ink-secondary">
                Не удалось загрузить список клиентов. Проверьте соединение с сервером.
              </p>
            </Card>
          )}
        </div>
      </div>
    </AppShell>
  );
}
