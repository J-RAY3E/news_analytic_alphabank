"use client";

import { useState } from "react";
import { useFeedback } from "@/lib/api/hooks";
import { Button } from "@/components/ui/Button";
import { IconNotUseful, IconUseful, IconWrong } from "@/components/ui/icons";
import { cn } from "@/lib/utils";
import type { FeedbackRequest } from "@/lib/api/types";

type Rating = FeedbackRequest["rating"];

const OPTIONS: { key: Rating; label: string; icon: React.ReactNode }[] = [
  { key: "useful", label: "Полезно", icon: <IconUseful size={14} /> },
  { key: "not_useful", label: "Не полезно", icon: <IconNotUseful size={14} /> },
  { key: "wrong", label: "Неверно", icon: <IconWrong size={14} /> },
];

export function FeedbackButtons({
  insightId,
  companyId,
  userId,
  role,
}: {
  insightId: string;
  companyId: string;
  userId: string;
  role: FeedbackRequest["role"];
}) {
  const [selected, setSelected] = useState<Rating | null>(null);
  const feedback = useFeedback();

  const send = (rating: Rating) => {
    setSelected(rating);
    feedback.mutate({ insight_id: insightId, company_id: companyId, user_id: userId, role, rating });
  };

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-caption text-ink-secondary">Был ли вывод полезен?</span>
      {OPTIONS.map((opt) => (
        <Button
          key={opt.key}
          variant="feedback"
          size="sm"
          onClick={() => send(opt.key)}
          aria-pressed={selected === opt.key}
          className={cn(selected === opt.key && "border-blue bg-blue-bg")}
        >
          {opt.icon}
          {opt.label}
        </Button>
      ))}
      {selected && feedback.isSuccess && (
        <span className="text-caption text-ink-mute">Спасибо, отзыв сохранён</span>
      )}
      {feedback.isError && (
        <span className="text-caption text-danger">Отзыв не сохранён. Попробуйте позже.</span>
      )}
    </div>
  );
}
