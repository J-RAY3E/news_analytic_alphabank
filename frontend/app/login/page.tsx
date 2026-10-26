"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAppState } from "@/lib/store";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { authenticate } from "@/lib/demoAccounts";

export default function LoginPage() {
  const router = useRouter();
  const { setUserId } = useAppState();
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const close = () => {
    if (typeof window !== "undefined" && window.history.length > 1) {
      router.back();
    } else {
      router.push("/");
    }
  };

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    const account = authenticate(login, password);
    if (!account) {
      setError("Неверный логин или пароль");
      return;
    }
    setError(null);
    setUserId(account.id);
    router.push("/");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-dark p-4">
      <div className="relative w-full max-w-md rounded-xl bg-canvas p-8 shadow-level-2">
        <button
          type="button"
          onClick={close}
          aria-label="Закрыть"
          className="absolute right-4 top-4 flex min-h-[36px] min-w-[36px] items-center justify-center rounded-pill text-ink-secondary hover:bg-canvas-soft"
        >
          ×
        </button>

        <h1 className="text-display-md text-ink">Вход в Альфа-Бизнес (демо)</h1>
        <p className="mt-2 text-body-md text-ink-secondary">
          Демо-режим: войдите с тестовым аккаунтом. Данные компаний анонимизированы.
        </p>

        <form className="mt-6 flex flex-col gap-3" onSubmit={submit}>
          <Input
            label="Логин"
            value={login}
            onChange={(event) => setLogin(event.target.value)}
            aria-label="Логин"
            autoComplete="username"
          />
          <Input
            label="Пароль"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="••••••••"
            autoComplete="current-password"
            error={error}
          />
          <Button type="submit" variant="primary">
            Войти
          </Button>
        </form>

        <p className="mt-6 text-caption text-ink-mute">
          Данные для входа (логин и пароль) указаны в файле README.md.
        </p>
      </div>
    </div>
  );
}
