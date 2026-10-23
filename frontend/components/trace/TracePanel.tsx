"use client";

import { useEffect, useMemo, useState } from "react";
import type { InsightResponse, TraceEvent } from "@/lib/api/types";
import { cn, formatNumber, formatTime } from "@/lib/utils";
import { CriticBadge, FeatureChip, SourceChip } from "@/components/ui/chips";

const KIND_LABELS: Record<TraceEvent["kind"], string> = {
  PLAN: "Планировщик",
  TOOL_CALL: "Executor: вызов инструмента",
  TOOL_RESULT: "Executor: результат",
  CRITIC_CHECK: "Critic",
  RETRY: "Critic: повтор",
  COMPLETED: "Готово",
  ERROR: "Ошибка",
};

function parseTrace(raw: Record<string, unknown>[] | undefined): TraceEvent[] {
  if (!raw) return [];
  return raw.filter((e) => typeof e === "object" && e !== null && "kind" in e) as unknown as TraceEvent[];
}

function oneLineResult(step: TraceEvent): string | null {
  const payload = step.payload;
  if (!payload) return null;
  if (typeof payload.stance === "string") return payload.stance;
  if (typeof payload.issue === "string") return payload.issue;
  if (typeof payload.action === "string") return payload.action;
  if (Array.isArray(payload.steps)) return (payload.steps as string[]).join(" → ");
  if (payload.coverage !== undefined && typeof payload.coverage === "number") {
    return `Покрытие источниками: ${formatNumber(payload.coverage * 100, 0)}%`;
  }
  if (payload.industry) return `Отрасль: ${payload.industry}`;
  if (payload.top_supplier_industries) {
    return `Поставщики: ${(payload.top_supplier_industries as string[]).join(", ")}`;
  }
  return null;
}

export function TracePanel({ insight }: { insight: InsightResponse | null }) {
  const steps = useMemo(() => parseTrace(insight?.trace), [insight]);
  const [visible, setVisible] = useState(0);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  useEffect(() => {
    setVisible(steps.length);
  }, [steps.length]);

  useEffect(() => {
    if (steps.length === 0) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      setVisible(steps.length);
      return;
    }
    setVisible(0);
    const timer = setInterval(() => {
      setVisible((v) => {
        if (v >= steps.length) {
          clearInterval(timer);
          return v;
        }
        return v + 1;
      });
    }, 350);
    return () => clearInterval(timer);
  }, [steps]);

  const totals = useMemo(() => {
    let latency = 0;
    let tokens = 0;
    let failed = 0;
    for (const s of steps) {
      latency += s.latency_ms ?? 0;
      tokens += (s.prompt_tokens ?? 0) + (s.completion_tokens ?? 0);
      if (s.kind === "CRITIC_CHECK" && s.status === "FAILED") failed += 1;
    }
    return { latency, cost: tokens * 0.004, failed };
  }, [steps]);

  if (!insight || steps.length === 0) {
    return (
      <div className="rounded-xl bg-surface-dark p-6 text-on-primary">
        <h2 className="text-heading-lg">Agent Trace</h2>
        <p className="mt-3 text-body-md text-on-dark-mute">
          Выберите событие в ленте: здесь появятся шаги агента, вызовы инструментов и проверки Critic.
        </p>
      </div>
    );
  }

  const toggle = (seq: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(seq)) next.delete(seq);
      else next.add(seq);
      return next;
    });
  };

  return (
    <div className="rounded-xl bg-surface-dark p-6 text-on-primary">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-heading-lg">Agent Trace</h2>
        <div className="text-caption tnum text-on-dark-mute">
          Время: {formatNumber(totals.latency / 1000, 1)} с · Проверок Critic: {steps.filter((s) => s.kind === "CRITIC_CHECK").length}
          {totals.failed > 0 ? ` (с исправлением: ${totals.failed})` : ""} · Стоимость: {formatNumber(totals.cost, 2)} руб.
        </div>
      </div>

      <ol className="mt-4 space-y-2">
        {steps.slice(0, visible).map((step) => {
          const result = oneLineResult(step);
          const isOpen = expanded.has(step.seq);
          const isFailed = step.status === "FAILED";
          const retryNext = steps.find(
            (s) => s.seq > step.seq && s.kind === "RETRY"
          );
          const indented = step.kind === "RETRY";
          return (
            <li key={step.seq} className={cn(indented && "ml-5")}>
              <button
                type="button"
                onClick={() => toggle(step.seq)}
                aria-expanded={isOpen}
                className={cn(
                  "w-full rounded-md px-3 py-2 text-left text-mono-trace transition-colors",
                  "bg-surface-dark-raised text-on-dark-mute hover:text-on-primary",
                  isOpen && "text-on-primary"
                )}
              >
                <span className="flex items-center gap-2">
                  <span className="tnum text-on-dark-mute">{String(step.seq).padStart(2, "0")}</span>
                  <span className="text-on-primary">{KIND_LABELS[step.kind]}</span>
                  <span className="truncate">{step.name}</span>
                  <span className="ml-auto flex shrink-0 items-center gap-2">
                    {(step.kind === "CRITIC_CHECK" || step.status === "FAILED") && step.status && (
                      <CriticBadge status={step.status === "OK" ? "OK" : "FAILED"} />
                    )}
                    {step.latency_ms != null && (
                      <span className="tnum">{formatNumber(step.latency_ms, 0)} мс</span>
                    )}
                  </span>
                </span>
                {result && <span className="mt-1 block truncate text-on-dark-mute">{result}</span>}
              </button>

              {isOpen && (
                <div className="mt-1 rounded-md bg-surface-dark-raised/60 px-3 py-2 text-mono-trace text-on-dark-mute">
                  {step.timestamp && <p>Время: {formatTime(step.timestamp)}</p>}
                  {step.model && <p>Модель: {step.model}</p>}
                  {step.prompt_tokens != null && (
                    <p className="tnum">
                      Токены: {formatNumber(step.prompt_tokens, 0)} запрос /{" "}
                      {formatNumber(step.completion_tokens ?? 0, 0)} ответ
                    </p>
                  )}
                  {step.source_ids && step.source_ids.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {step.source_ids.map((sid) => (
                        <span key={sid} className="[&_span]:bg-hairline-on-dark [&_span]:text-on-primary">
                          <SourceChip label={sid} />
                        </span>
                      ))}
                    </div>
                  )}
                  {step.company_features && step.company_features.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {step.company_features.map((f) => (
                        <span key={f} className="[&_span]:bg-hairline-on-dark [&_span]:text-on-primary">
                          <FeatureChip name={f} />
                        </span>
                      ))}
                    </div>
                  )}
                  {step.payload && (
                    <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-micro text-on-dark-mute">
                      {JSON.stringify(step.payload, null, 2)}
                    </pre>
                  )}
                  {isFailed && retryNext && (
                    <p className="mt-2 text-micro text-on-dark-mute">
                      После этой проверки следует повтор: {retryNext.name}
                    </p>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
