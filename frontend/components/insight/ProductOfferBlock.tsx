import type { ProductOffer } from "@/lib/api/types";
import { Card } from "@/components/ui/Card";

export function ProductOfferBlock({ offer }: { offer: ProductOffer }) {
  return (
    <Card className="bg-canvas-soft p-4">
      <span className="inline-flex items-center rounded-pill bg-canvas px-2 py-[2px] text-micro text-ink-mute">
        Реклама
      </span>
      <h3 className="mt-2 text-heading-sm text-ink">{offer.name}</h3>
      <p className="mt-1 text-body-md text-ink-secondary">{offer.short}</p>
      {offer.reason && (
        <p className="mt-1 text-caption text-ink-mute">{offer.reason}</p>
      )}
      <a
        href={offer.url}
        target="_blank"
        rel="noreferrer noopener"
        className="mt-3 inline-flex text-body-md text-blue-deep underline"
      >
        Подробнее
      </a>
      <p className="mt-2 text-micro text-ink-mute">
        Предложение банка, не влияет на анализ.
      </p>
    </Card>
  );
}
