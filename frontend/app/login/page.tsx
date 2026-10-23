"use client";

import { useRouter } from "next/navigation";
import { useAppState, type DemoUser } from "@/lib/store";
import { Button } from "@/components/ui/Button";
import type { Role } from "@/lib/api/types";

const ACCOUNTS: DemoUser[] = [
  { id: "user-ceo", name: "Директор по стратегии", role: "CEO" as Role },
  { id: "user-cfo", name: "Финансовый директор", role: "CFO" as Role },
];

const ROLE_TEXT: Record<Role, string> = {
  CEO: "Стратегические риски, конкуренты, регулирование",
  CFO: "Стоимость долга, курс рубля, ковенанты",
  TREASURER: "Ликвидность, депозиты, хеджирование",
  CHIEF_ACCOUNTANT: "Налоги и отчётность",
  OTHER: "Операционные события",
};

export default function LoginPage() {
  const router = useRouter();
  const { setUserId } = useAppState();

  const signIn = (user: DemoUser) => {
    setUserId(user.id);
    router.push("/");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-dark p-4">
      <div className="w-full max-w-md rounded-xl bg-canvas p-8 shadow-level-2">
        <h1 className="text-display-md text-ink">Вход в Альфа-Бизнес</h1>
        <p className="mt-2 text-body-md text-ink-secondary">
          Демо-режим: выберите тестовый аккаунт. Данные компаний анонимизированы.
        </p>
        <div className="mt-6 flex flex-col gap-3">
          {ACCOUNTS.map((account) => (
            <button
              key={account.id}
              type="button"
              onClick={() => signIn(account)}
              className="rounded-lg border border-hairline bg-canvas p-4 text-left transition-shadow hover:shadow-level-1 focus:border-blue"
            >
              <span className="text-body-md font-medium text-ink">{account.name}</span>
              <span className="mt-1 block text-caption text-ink-secondary">
                {ROLE_TEXT[account.role]}
              </span>
            </button>
          ))}
        </div>
        <p className="mt-6 text-micro text-ink-mute">
          Роль выбирается вручную в демо-режиме после входа.
        </p>
        <div className="mt-4">
          <Button variant="ghost" size="sm" onClick={() => router.push("/")}>
            Продолжить без входа
          </Button>
        </div>
      </div>
    </div>
  );
}
