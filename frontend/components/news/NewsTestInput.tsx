"use client";

import { useEffect, useRef, useState } from "react";
import { useIngest } from "@/lib/api/hooks";
import type { NormalizedEvent } from "@/lib/api/types";
import { Button } from "@/components/ui/Button";
import { Input, Textarea } from "@/components/ui/Input";
import { IconCheck } from "@/components/ui/icons";
import { cn } from "@/lib/utils";

const STEPS = [
  "Нормализация",
  "Извлечение фактов",
  "Оценка релевантности",
  "Анализ агентом",
  "Проверка Critic",
] as const;

export function NewsTestInput({
  onInsightReady,
  companyId,
  role,
}: {
  onInsightReady: (event: NormalizedEvent) => void;
  companyId: string | null;
  role: string;
}) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<number | null>(null);
  const ingest = useIngest();
  const timersRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => {
      if (timersRef.current) clearInterval(timersRef.current);
    };
  }, []);

  const startStepper = (totalMs: number) => {
    const started = Date.now();
    setStep(0);
    timersRef.current = setInterval(() => {
      const elapsed = Date.now() - started;
      const idx = Math.min(Math.floor((elapsed / totalMs) * STEPS.length), STEPS.length - 1);
      setStep(idx);
    }, 400);
  };

  const stopStepper = () => {
    if (timersRef.current) clearInterval(timersRef.current);
    timersRef.current = null;
  };

  const submit = async () => {
    setError(null);
    if (!text.trim() && !url.trim()) {
      setError("Вставьте текст новости или ссылку");
      return;
    }
    startStepper(4000);
    try {
      const res = await ingest.mutateAsync({ text: text.trim() || null, url: url.trim() || null });
      await new Promise((r) => setTimeout(r, 2200));
      setStep(STEPS.length - 1);
      stopStepper();
      setStep(null);
      setText("");
      setUrl("");
      setOpen(false);
      onInsightReady(res.event);
    } catch {
      stopStepper();
      setStep(null);
      setError("Не удалось обработать новость. Попробуйте ещё раз.");
    }
  };

  if (!open) {
    return (
      <div className="mt-4">
        <Button
          variant="secondary"
          className="w-full"
          onClick={() => setOpen(true)}
          disabled={!companyId}
        >
          Проверить новую новость
        </Button>
        {!companyId && (
          <p className="mt-2 text-micro text-ink-mute">Сначала выберите клиента</p>
        )}
      </div>
    );
  }

  return (
    <div className="mt-4 rounded-lg border border-hairline bg-canvas p-4">
      <div className="flex items-center justify-between">
        <span className="text-heading-sm text-ink">Проверка новой новости</span>
        <button
          type="button"
          onClick={() => {
            setOpen(false);
            setStep(null);
            setError(null);
          }}
          className="min-h-[36px] rounded-sm px-2 text-caption text-ink-secondary hover:bg-canvas-soft"
        >
          Скрыть
        </button>
      </div>
      <p className="mt-1 text-micro text-ink-mute">
        Полный цикл: нормализация, извлечение, оценка и проверка. Роль: {role}.
      </p>

      <div className="mt-3 flex flex-col gap-3">
        <Textarea
          label="Текст новости"
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Вставьте текст новости или её заголовок"
          error={error}
        />
        <Input
          label="Или ссылка на новость"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://"
          type="url"
        />
        <Button variant="primary" onClick={submit} disabled={ingest.isPending}>
          {ingest.isPending ? "Обработка..." : "Проверить новость"}
        </Button>
      </div>

      {step !== null && (
        <ol className="mt-4 space-y-2" aria-label="Прогресс обработки">
          {STEPS.map((label, i) => {
            const done = i < step;
            const current = i === step;
            return (
              <li key={label} className="flex items-center gap-2">
                <span
                  className={cn(
                    "flex h-5 w-5 items-center justify-center rounded-pill",
                    done && "bg-success text-on-primary",
                    current && "bg-blue text-on-primary",
                    !done && !current && "bg-canvas-track text-ink-secondary"
                  )}
                >
                  {done ? <IconCheck size={12} /> : <span className="text-micro tnum">{i + 1}</span>}
                </span>
                <span
                  className={cn(
                    "text-caption",
                    current ? "text-blue" : done ? "text-ink-secondary" : "text-ink-mute"
                  )}
                >
                  {label}
                </span>
              </li>
            );
          })}
        </ol>
      )}
    </div>
  );
}
