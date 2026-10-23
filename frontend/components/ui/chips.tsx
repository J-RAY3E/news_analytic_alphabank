import { cn } from "@/lib/utils";
import type { ClaimType, RiskOpportunity } from "@/lib/api/types";
import {
  CLAIM_TYPE_LABELS,
  CLAIM_TYPE_TOOLTIPS,
} from "@/lib/api/types";
import { IconBank, IconCheck, IconDot, IconExternal, IconSpark } from "./icons";

export function ScoreBadge({
  score,
  onClick,
  active,
}: {
  score: number;
  onClick?: () => void;
  active?: boolean;
}) {
  const label = score.toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const content = (
    <span
      className={cn(
        "inline-flex items-center rounded-pill bg-blue-bg px-2 py-1 text-caption tnum text-blue-deep",
        onClick && "cursor-pointer hover:brightness-95",
        active && "ring-2 ring-blue"
      )}
      title="Оценка релевантности: нажмите для разбора"
    >
      {label}
    </span>
  );
  if (!onClick) return content;
  return (
    <button type="button" onClick={onClick} aria-expanded={active} className="rounded-pill">
      {content}
    </button>
  );
}

export function ReasonChip({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-pill bg-canvas-soft px-2 py-1 text-caption text-ink-secondary">
      {children}
    </span>
  );
}

export function FeatureChip({ name }: { name: string }) {
  return (
    <span
      className="inline-flex items-center rounded-pill bg-canvas-soft px-2 py-1 text-caption font-mono text-ink-secondary"
      title="Признак компании, который повлиял на вывод"
    >
      {name}
    </span>
  );
}

export function RiskChip() {
  return (
    <span className="inline-flex items-center gap-1 rounded-pill bg-risk-bg px-2 py-1 text-caption text-ink">
      <IconDot size={8} className="text-primary" />
      Риск
    </span>
  );
}

export function OpportunityChip() {
  return (
    <span className="inline-flex items-center gap-1 rounded-pill bg-success-bg px-2 py-1 text-caption text-ink">
      <IconDot size={8} className="text-success" />
      Возможность
    </span>
  );
}

export function SourceChip({
  label,
  onClick,
  external,
}: {
  label: string;
  onClick?: () => void;
  external?: boolean;
}) {
  const inner = (
    <span className="inline-flex items-center gap-1 rounded-pill bg-canvas-soft px-2 py-1 text-caption text-blue-deep">
      {external && <IconExternal size={12} />}
      {label}
    </span>
  );
  if (!onClick) return inner;
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-pill hover:brightness-95"
      title="Открыть источник"
    >
      {inner}
    </button>
  );
}

const CLAIM_STYLES: Record<
  ClaimType,
  { bg: string; text: string; icon: React.ReactNode }
> = {
  FACT: {
    bg: "bg-success-bg",
    text: "text-ink",
    icon: <IconCheck size={12} />,
  },
  BANK_VIEW: {
    bg: "bg-blue-bg",
    text: "text-blue-deep",
    icon: <IconBank size={12} />,
  },
  AI_INFERENCE: {
    bg: "bg-lilac-soft",
    text: "text-ink",
    icon: <IconSpark size={12} />,
  },
};

export function ClaimLabel({ type }: { type: ClaimType }) {
  const style = CLAIM_STYLES[type];
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-pill px-2 py-[2px] text-label-claim",
        style.bg,
        style.text
      )}
      title={CLAIM_TYPE_TOOLTIPS[type]}
    >
      {style.icon}
      {CLAIM_TYPE_LABELS[type]}
    </span>
  );
}

export function CriticBadge({ status }: { status: "OK" | "FAILED" }) {
  const pass = status === "OK";
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-pill px-2 py-[2px] text-label-claim text-on-primary",
        pass ? "bg-success" : "bg-danger"
      )}
    >
      {pass ? "Проверено" : "Не пройдено"}
    </span>
  );
}

export function DirectionChip({ direction }: { direction: RiskOpportunity }) {
  if (direction === "RISK") return <RiskChip />;
  if (direction === "OPPORTUNITY") return <OpportunityChip />;
  return null;
}
