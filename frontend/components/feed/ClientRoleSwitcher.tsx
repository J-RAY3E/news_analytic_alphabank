"use client";

import type { CompanySummary, Role } from "@/lib/api/types";
import { ROLE_SHORT } from "@/lib/api/types";
import { cn } from "@/lib/utils";
import { useId } from "react";

const ROLES: Role[] = ["CEO", "CFO", "TREASURER", "CHIEF_ACCOUNTANT", "OTHER"];

export function ClientRoleSwitcher({
  company,
  companies,
  onCompanyChange,
  role,
  onRoleChange,
}: {
  company: CompanySummary | null;
  companies: CompanySummary[];
  onCompanyChange: (id: string) => void;
  role: Role;
  onRoleChange: (role: Role) => void;
}) {
  const selectId = useId();

  return (
    <div>
      <div className="rounded-pill bg-canvas-track p-1">
        <label htmlFor={selectId} className="sr-only">
          Выбор клиента
        </label>
        <select
          id={selectId}
          value={company?.company_id ?? ""}
          onChange={(e) => onCompanyChange(e.target.value)}
          className="min-h-[40px] w-full rounded-pill border-0 bg-canvas px-3 text-button-sm text-ink focus:border-blue"
        >
          {companies.map((c) => (
            <option key={c.company_id} value={c.company_id}>
              {c.display_name}, {c.industry_label}, {c.revenue_band}
            </option>
          ))}
        </select>
      </div>

      <div className="mt-2 flex flex-wrap gap-1" role="tablist" aria-label="Роль пользователя">
        {ROLES.map((r) => (
          <button
            key={r}
            type="button"
            role="tab"
            aria-selected={role === r}
            onClick={() => onRoleChange(r)}
            className={cn(
              "min-h-[36px] rounded-pill px-3 text-button-sm transition-colors",
              role === r
                ? "bg-surface-dark-raised text-on-primary"
                : "bg-canvas-track text-ink-secondary hover:bg-canvas-grey"
            )}
          >
            {ROLE_SHORT[r]}
          </button>
        ))}
      </div>
      <p className="mt-2 text-micro text-ink-mute">
        Роль выбирается вручную в демо-режиме
      </p>
    </div>
  );
}
