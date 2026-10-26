"use client";

import { cn } from "@/lib/utils";
import type { Claim, ClaimType } from "@/lib/api/types";
import { ClaimLabel, FeatureChip, ImpactChip, SourceChip } from "@/components/ui/chips";

function effectiveType(claim: Claim): ClaimType {
  if (claim.type === "FACT" && claim.source_ids.length === 0) {
    return "AI_INFERENCE";
  }
  return claim.type;
}

export function ClaimBlock({
  claim,
  onOpenSource,
}: {
  claim: Claim;
  onOpenSource?: (sourceId: string) => void;
}) {
  const type = effectiveType(claim);
  const missing = claim.company_features?.filter((f) => f.startsWith("missing:")) ?? [];
  const present = claim.company_features?.filter((f) => !f.startsWith("missing:")) ?? [];

  return (
    <div
      className={cn(
        "rounded-md border border-hairline bg-canvas px-4 py-3",
        type === "AI_INFERENCE" && "border-l-[3px] border-l-lilac-deep"
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <ClaimLabel type={type} />
        <span className="flex items-center gap-2">
          {claim.impact && <ImpactChip impact={claim.impact} />}
          {(type === "AI_INFERENCE" || type === "HYPOTHESIS") && (
            <span className="text-caption tnum text-ink-mute">
              Уверенность {claim.confidence.toLocaleString("ru-RU", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
          )}
        </span>
      </div>
      <p className="mt-2 text-body-md text-ink">{claim.text}</p>
      {(claim.source_ids.length > 0 || present.length > 0 || missing.length > 0) && (
        <div className="mt-3 flex flex-wrap items-center gap-1.5">
          {claim.source_ids.map((sid) => (
            <SourceChip
              key={sid}
              label={sid}
              onClick={onOpenSource ? () => onOpenSource(sid) : undefined}
            />
          ))}
          {present.map((f) => (
            <FeatureChip key={f} name={f} />
          ))}
          {missing.map((f) => (
            <span
              key={f}
              className="inline-flex items-center rounded-pill bg-canvas-soft px-2 py-1 text-caption text-ink-secondary"
            >
              Нет данных: {f.replace("missing:", "")}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
