import type { CompanySummary } from "@/lib/api/types";
import { formatRub } from "@/lib/utils";
import { Card } from "@/components/ui/Card";

export function CompanyProfilePanel({
  company,
  compact,
}: {
  company: CompanySummary | null;
  compact?: boolean;
}) {
  if (!company) {
    return (
      <Card className="p-4">
        <p className="text-caption text-ink-secondary">Профиль компании недоступен</p>
      </Card>
    );
  }

  const missing: string[] = [];
  if (!company.industry_label) missing.push("отрасль");
  if (!company.region) missing.push("регион");
  if (!company.group_id) missing.push("группа");

  const location = [company.city, company.region].filter(Boolean).join(", ") || "нет данных";
  const group = company.group_id
    ? `${company.group_id} · ${company.group_size} комп. · ${formatRub(company.group_revenue_rub ?? 0)}`
    : "не в группе";

  return (
    <Card className={compact ? "p-4" : "p-6"}>
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-heading-sm text-ink">Профиль компании</h2>
        {company.client_type && (
          <span className="rounded-pill bg-canvas-soft px-2 py-[2px] text-micro text-ink-secondary">
            {company.client_type}
          </span>
        )}
      </div>
      <p className="mt-1 break-words text-body-md text-ink">{company.display_name}</p>
      <dl className="mt-3 grid grid-cols-1 gap-x-4 gap-y-2 text-body-md sm:grid-cols-2">
        <div>
          <dt className="text-caption text-ink-secondary">Отрасль</dt>
          <dd className="text-ink">{company.industry_label || "нет данных"}</dd>
        </div>
        <div>
          <dt className="text-caption text-ink-secondary">Регион</dt>
          <dd className="text-ink">{location}</dd>
        </div>
        <div>
          <dt className="text-caption text-ink-secondary">Масштаб</dt>
          <dd className="text-ink tnum">{company.revenue_band || "нет данных"}</dd>
        </div>
        <div>
          <dt className="text-caption text-ink-secondary">Группа</dt>
          <dd className="text-ink tnum">{group}</dd>
        </div>
      </dl>
      {missing.length > 0 && (
        <p className="mt-2 text-micro text-ink-mute">Нет данных: {missing.join(", ")}</p>
      )}
    </Card>
  );
}
