"use client";

import { useState } from "react";
import type { CompanySummary, InsightResponse, NormalizedEvent } from "@/lib/api/types";
import { CLAIM_TYPE_LABELS, ROLE_LABELS } from "@/lib/api/types";
import { formatDateTime, formatScore } from "@/lib/utils";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Toast } from "@/components/ui/Toast";
import { ClaimBlock } from "@/components/claim/ClaimBlock";
import { ClaimLabel, CriticBadge, FeatureChip, SourceChip } from "@/components/ui/chips";
import { FeedbackButtons } from "./FeedbackButtons";
import { CompanyProfilePanel } from "./CompanyProfilePanel";
import { ProductOfferBlock } from "./ProductOfferBlock";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { IconRadar } from "@/components/ui/icons";
import type { TraceEvent } from "@/lib/api/types";

const SECTIONS: { key: keyof InsightResponse; heading: string }[] = [
  { key: "what_happened", heading: "Что произошло" },
  { key: "why_it_matters", heading: "Почему это важно для вашей компании" },
  { key: "consequences", heading: "Возможные последствия" },
  { key: "actions", heading: "Какие действия могут быть актуальны" },
  { key: "bank_view", heading: "Как это оценивает банк" },
];

function parseTrace(raw: Record<string, unknown>[] | undefined): TraceEvent[] {
  if (!raw) return [];
  return raw.filter((e) => typeof e === "object" && e !== null && "kind" in e) as unknown as TraceEvent[];
}

export function InsightView({
  insight,
  event,
  company,
  companyName,
  userName,
  onOpenSource,
}: {
  insight: InsightResponse;
  event: NormalizedEvent | null;
  company?: CompanySummary | null;
  companyName: string;
  userName: string;
  onOpenSource: (sourceId: string) => void;
}) {
  const trace = parseTrace(insight.trace);
  const criticFailed = trace.some((t) => t.kind === "CRITIC_CHECK" && t.status === "FAILED");
  const [toast, setToast] = useState<string | null>(null);
  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(
      () => setToast((current) => (current === message ? null : current)),
      2500
    );
  };

  const allSourceIds = Array.from(
    new Set(
      SECTIONS.flatMap((s) => {
        const claims = insight[s.key] as InsightResponse["what_happened"];
        return claims.flatMap((c) => c.source_ids);
      }).concat(insight.basis.flatMap((c) => c.source_ids))
    )
  );

  const allFeatures = Array.from(
    new Set(
      insight.basis.flatMap((c) => c.company_features ?? []).concat(
        SECTIONS.flatMap((s) => {
          const claims = insight[s.key] as InsightResponse["what_happened"];
          return claims.flatMap((c) => c.company_features ?? []);
        })
      )
    )
  );

  return (
    <div className="space-y-4">
      {company && <CompanyProfilePanel company={company} compact />}

      {criticFailed && (
        <div
          className="rounded-md bg-risk-bg px-4 py-3 text-body-md text-ink"
          role="alert"
        >
          Часть выводов не прошла проверку. Пометки сохранены, ничего не скрыто: детали в Agent Trace.
        </div>
      )}

      <Card className="p-8">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-caption text-ink-mute">
              {companyName} · Для роли: {ROLE_LABELS[insight.role]}
            </p>
            <h1 className="mt-2 text-display-lg text-ink">
              {event?.title ?? insight.event_id}
            </h1>
          </div>
          <div className="shrink-0 rounded-pill bg-blue-bg px-3 py-1.5 text-caption tnum text-blue-deep">
            Релевантность {formatScore(insight.relevance_score)}
          </div>
        </div>
        {event?.summary && <p className="mt-3 text-body-lg text-ink-secondary">{event.summary}</p>}
        {event && (
          <p className="mt-2 text-caption text-ink-mute">
            {event.source.name}
            {event.source.published_at ? ` · ${formatDateTime(event.source.published_at)}` : ""}
          </p>
        )}
      </Card>

      {SECTIONS.map((section) => {
        const claims = insight[section.key] as InsightResponse["what_happened"];
        if (!claims || claims.length === 0) return null;
        return (
          <Card key={section.key} className="p-8">
            <h2 className="text-heading-sm text-ink">{section.heading}</h2>
            {section.key === "bank_view" && (
              <p className="mt-1 text-micro text-ink-mute">
                Раздел содержит только аналитику Альфа-Банка. Внешние выводы помечены метками
                «Вывод ИИ» и «Гипотеза».
              </p>
            )}
            <div className="mt-4 space-y-3">
              {claims.map((claim, i) => (
                <ClaimBlock key={i} claim={claim} onOpenSource={onOpenSource} />
              ))}
            </div>
          </Card>
        );
      })}

      <Card className="p-8">
        <h2 className="text-heading-sm text-ink">На чём основаны выводы</h2>

        <h3 className="mt-4 text-caption text-ink-secondary">Источники</h3>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {allSourceIds.length === 0 && (
            <span className="text-body-md text-ink-mute">Источники не указаны</span>
          )}
          {allSourceIds.map((sid) => (
            <SourceChip key={sid} label={sid} onClick={() => onOpenSource(sid)} />
          ))}
        </div>

        <h3 className="mt-4 text-caption text-ink-secondary">Признаки компании</h3>
        <div className="mt-2 flex flex-wrap gap-1.5">
          {allFeatures.length === 0 && (
            <span className="text-body-md text-ink-mute">Признаки не применялись</span>
          )}
          {allFeatures.map((f) => (
            <FeatureChip key={f} name={f} />
          ))}
        </div>

        <h3 className="mt-4 text-caption text-ink-secondary">Проверка Critic</h3>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          {trace
            .filter((t) => t.kind === "CRITIC_CHECK")
            .map((t, i) => (
              <span key={i} className="inline-flex items-center gap-1.5 rounded-pill bg-canvas-soft px-2 py-1 text-caption text-ink-secondary">
                {t.name}
                <CriticBadge status={t.status === "OK" ? "OK" : "FAILED"} />
              </span>
            ))}
          {trace.length === 0 && (
            <span className="text-body-md text-ink-mute">Трассировка недоступна</span>
          )}
        </div>

        <div className="mt-4 flex flex-wrap gap-4">
          {(["FACT", "BANK_VIEW", "AI_INFERENCE", "HYPOTHESIS"] as const).map((t) => (
            <span key={t} className="inline-flex items-center gap-2">
              <ClaimLabel type={t} />
              <span className="text-micro text-ink-mute">{CLAIM_TYPE_LABELS[t]}</span>
            </span>
          ))}
          <span className="inline-flex items-center gap-2 text-micro text-ink-mute">
            <IconRadar size={14} />
            Метки присваиваются по источникам каждого утверждения
          </span>
        </div>
      </Card>

      <Card className="p-6">
        <FeedbackButtons
          insightId={insight.insight_id}
          companyId={insight.company_id}
          userId={userName}
          role={insight.role}
        />
      </Card>

      <Card className="p-6">
        <h2 className="text-heading-sm text-ink">Следующие шаги</h2>
        <div className="mt-3 flex flex-wrap gap-2">
          <Button variant="primary" size="sm" onClick={() => notify("Запрос менеджеру отправлен (демо)")}>
            Связаться с менеджером
          </Button>
          <Button variant="secondary" size="sm" onClick={() => notify("Заявка отправлена (демо)")}>
            Оставить заявку
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => notify("Обратный звонок запрошен (демо)")}
          >
            Запросить обратный звонок
          </Button>
          <Button
            variant="secondary"
            size="sm"
            disabled={allSourceIds.length === 0}
            onClick={() => allSourceIds[0] && onOpenSource(allSourceIds[0])}
          >
            Открыть источник
          </Button>
        </div>
        <p className="mt-2 text-micro text-ink-mute">
          Демо-действия: при внедрении ведут в CRM банка.
        </p>
      </Card>

      {insight.product_offer && <ProductOfferBlock offer={insight.product_offer} />}

      <Toast message={toast} />

      <p className="text-micro text-ink-mute">
        {insight.disclaimer ?? "Материал не является инвестиционной рекомендацией."}
      </p>

      <ChatPanel insightId={insight.insight_id} onOpenSource={onOpenSource} />
    </div>
  );
}
