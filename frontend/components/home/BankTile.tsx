import { Card } from "@/components/ui/Card";
import { formatRub } from "@/lib/utils";

const IN_PROGRESS = [
  "Платёжное поручение — 3",
  "Заявка на банковскую гарантию — 1",
  "Справка для контрагента — 2",
];

export function BankTile() {
  return (
    <Card className="bg-surface-dark p-6 text-on-primary">
      <p className="text-caption text-on-dark-mute">Остаток на счёте (демо)</p>
      <p className="mt-1 text-number-score tnum">{formatRub(12_480_000)}</p>
      <p className="mt-5 text-caption text-on-dark-mute">Дела в работе</p>
      <ul className="mt-1 space-y-1">
        {IN_PROGRESS.map((line) => (
          <li key={line} className="text-body-md text-on-dark-mute">
            · {line}
          </li>
        ))}
      </ul>
      <p className="mt-4 text-micro text-on-dark-mute">
        Демонстрационные данные, не связаны с реальными счетами.
      </p>
    </Card>
  );
}
