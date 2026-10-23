"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAppState } from "@/lib/store";
import { Button } from "@/components/ui/Button";
import { IconHome, IconRadar } from "@/components/ui/icons";

const NAV_ITEMS = [
  { href: "/", label: "Главная", icon: IconHome },
  { href: "/radar", label: "Radar", icon: IconRadar },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, setUserId } = useAppState();

  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex w-60 shrink-0 flex-col bg-surface-dark text-on-primary">
        <div className="px-6 py-6">
          <span className="text-heading-sm font-medium text-on-primary">Альфа-Бизнес</span>
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
              </Link>
            );
          })}
        </nav>
        <div className="mt-auto px-6 py-6">
          <p className="text-micro text-on-dark-mute">
            Alfa Radar: новости, влияние, действия
          </p>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between gap-4 bg-surface-dark px-4 py-3 text-on-primary md:px-6">
          <Link href="/" className="text-body-md font-medium md:hidden">
            Альфа-Бизнес
          </Link>
          <div className="hidden text-caption text-on-dark-mute md:block">
            Интернет-банк для бизнеса
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
    </div>
  );
}
