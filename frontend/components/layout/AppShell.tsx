"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAppState } from "@/lib/store";
import { useCompanies } from "@/lib/api/hooks";
import { Button } from "@/components/ui/Button";
import { IconHome, IconRadar } from "@/components/ui/icons";
import { ROLE_SHORT, type Role } from "@/lib/api/types";

const NAV_ITEMS = [
  { href: "/", label: "Главная", icon: IconHome, badge: null as string | null },
  { href: "/radar", label: "Radar", icon: IconRadar, badge: "НОВОЕ" },
];

const MOCK_ITEMS = [
  "Заявки",
  "Новый платёж",
  "Лента операций",
  "Счета",
  "Контрагенты",
  "Справки",
];

const ROLES: Role[] = ["CEO", "CFO", "TREASURER", "CHIEF_ACCOUNTANT", "OTHER"];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, hydrated, setUserId, companyId, setCompanyId, role, setRole } =
    useAppState();
  const companies = useCompanies();
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    if (hydrated && !user) {
      router.replace("/login");
    }
  }, [hydrated, user, router]);

  useEffect(() => {
    const list = companies.data;
    if (!list || list.length === 0) return;
    if (!companyId || !list.some((c) => c.company_id === companyId)) {
      setCompanyId(list[0].company_id);
    }
  }, [companies.data, companyId, setCompanyId]);

  const showToast = (message: string) => {
    setToast(message);
    window.setTimeout(
      () => setToast((current) => (current === message ? null : current)),
      2000
    );
  };

  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex w-60 shrink-0 flex-col bg-surface-dark text-on-primary">
        <div className="px-6 py-6">
          <span className="text-heading-sm font-medium text-on-primary">
            Альфа-Бизнес
          </span>
          <p className="mt-1 text-micro text-on-dark-mute">Демо-оболочка банка</p>
        </div>
        <nav className="flex flex-col gap-1 px-3" aria-label="Основная навигация">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex min-h-[40px] items-center gap-3 rounded-md px-3 text-body-md transition-colors",
                  active
                    ? "bg-surface-dark-raised text-on-primary"
                    : "text-on-dark-mute hover:bg-surface-dark-raised hover:text-on-primary"
                )}
                aria-current={active ? "page" : undefined}
              >
                <Icon size={18} />
                {item.label}
                {item.badge && (
                  <span className="ml-auto rounded-pill bg-primary px-1.5 py-[1px] text-micro text-on-primary">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
          {MOCK_ITEMS.map((label) => (
            <button
              key={label}
              type="button"
              onClick={() => showToast("Раздел недоступен в демо")}
              className="flex min-h-[40px] items-center gap-3 rounded-md px-3 text-left text-body-md text-on-dark-mute transition-colors hover:bg-surface-dark-raised hover:text-on-primary"
            >
              {label}
            </button>
          ))}
        </nav>
        <div className="mt-auto px-6 py-6">
          <Link href="/admin/metrics" className="text-micro text-on-dark-mute hover:text-on-primary">
            Метрики
          </Link>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex flex-wrap items-center justify-between gap-3 bg-surface-dark px-4 py-3 text-on-primary md:px-6">
          <Link href="/" className="text-body-md font-medium md:hidden">
            Альфа-Бизнес
          </Link>
          <div className="hidden text-caption text-on-dark-mute lg:block">
            Интернет-банк для бизнеса
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <label className="sr-only" htmlFor="company-selector">
              Мои компании
            </label>
            <select
              id="company-selector"
              value={companyId ?? ""}
              onChange={(event) => setCompanyId(event.target.value)}
              className="min-h-[36px] max-w-[300px] rounded-pill bg-surface-dark-raised px-3 text-caption text-on-primary"
            >
              {(companies.data ?? []).map((company) => (
                <option key={company.company_id} value={company.company_id}>
                  {company.display_name}
                  {company.industry_label ? ` · ${company.industry_label}` : ""}
                  {company.revenue_band ? ` · ${company.revenue_band}` : ""}
                  {company.group_id ? ` · ${company.group_id}` : ""}
                </option>
              ))}
            </select>

            <div className="flex flex-wrap gap-1" role="tablist" aria-label="Роль пользователя">
              {ROLES.map((item) => (
                <button
                  key={item}
                  type="button"
                  role="tab"
                  aria-selected={role === item}
                  onClick={() => setRole(item)}
                  className={cn(
                    "min-h-[32px] rounded-pill px-2.5 text-micro transition-colors",
                    role === item
                      ? "bg-primary text-on-primary"
                      : "bg-surface-dark-raised text-on-dark-mute hover:text-on-primary"
                  )}
                >
                  {ROLE_SHORT[item]}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="text-caption text-on-dark-mute">{user.name}</span>
                <Button
                  variant="on-dark"
                  size="sm"
                  onClick={() => setUserId("")}
                  className="bg-surface-dark-button text-on-primary hover:bg-hairline-on-dark"
                >
                  Выйти
                </Button>
              </>
            ) : (
              <Link
                href="/login"
                className="inline-flex min-h-[36px] items-center rounded-pill bg-primary px-3 text-button-sm text-on-primary hover:bg-primary-press"
              >
                Войти
              </Link>
            )}
          </div>
        </header>
        <main className="flex-1">{children}</main>
      </div>

      {toast && (
        <div
          className="fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-pill bg-surface-dark px-4 py-2 text-caption text-on-primary shadow-level-2"
          role="status"
        >
          {toast}
        </div>
      )}
    </div>
  );
}
