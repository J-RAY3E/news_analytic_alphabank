"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { IconSend } from "@/components/ui/icons";
import { ClaimBlock } from "@/components/claim/ClaimBlock";
import type { Claim } from "@/lib/api/types";
import { useChat } from "@/lib/api/hooks";

interface ChatMessage {
  id: number;
  from: "user" | "agent";
  text?: string;
  claim?: Claim;
}

let nextId = 1;

export function ChatPanel({
  insightId,
  onOpenSource,
}: {
  insightId: string;
  onOpenSource?: (sourceId: string) => void;
}) {
  const chatMutation = useChat();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);

  const send = async (forced?: string) => {
    const question = (forced ?? input).trim();
    if (!question || pending) return;
    setMessages((m) => [...m, { id: nextId++, from: "user", text: question }]);
    setInput("");
    setPending(true);
    try {
      const res = await chatMutation.mutateAsync({ insightId, question });
      if (res.claim) {
        setMessages((m) => [...m, { id: nextId++, from: "agent", claim: res.claim as Claim }]);
      } else {
        setMessages((m) => [...m, { id: nextId++, from: "agent", text: res.text }]);
      }
    } catch {
      setMessages((m) => [
        ...m,
        { id: nextId++, from: "agent", text: "Не удалось получить ответ. Попробуйте ещё раз." },
      ]);
    } finally {
      setPending(false);
    }
  };

  const quickActions = [
    { label: "Открыть источник", q: "Покажи источники" },
    { label: "Другой срез данных", q: "Покажи другой срез данных" },
    { label: "Объяснить подробнее", q: "Объясни подробнее" },
  ];

  return (
    <div className="rounded-lg border border-hairline bg-canvas p-6">
      <h3 className="text-heading-sm text-ink">Уточняющие вопросы</h3>

      {messages.length === 0 && (
        <p className="mt-2 text-body-md text-ink-secondary">
          Задайте вопрос по событию. Ответы с фактами сохраняют метки и источники.
        </p>
      )}

      <div className="mt-4 space-y-3">
        {messages.map((m) =>
          m.from === "user" ? (
            <div key={m.id} className="ml-auto w-fit max-w-[85%] rounded-lg bg-surface-dark-raised px-4 py-3 text-body-md text-on-primary">
              {m.text}
            </div>
          ) : m.claim ? (
            <div key={m.id} className="mr-auto w-fit max-w-[90%]">
              <ClaimBlock claim={m.claim} onOpenSource={onOpenSource} />
            </div>
          ) : (
            <div key={m.id} className="mr-auto w-fit max-w-[85%] rounded-lg bg-canvas-soft px-4 py-3 text-body-md text-ink">
              {m.text}
            </div>
          )
        )}
        {pending && (
          <div className="mr-auto rounded-lg bg-canvas-soft px-4 py-3 text-body-md text-ink-secondary">
            Формируется ответ...
          </div>
        )}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {quickActions.map((qa) => (
          <button
            key={qa.label}
            type="button"
            onClick={() => send(qa.q)}
            className="min-h-[36px] rounded-pill bg-canvas-soft px-3 text-caption text-ink-secondary hover:bg-canvas-track"
          >
            {qa.label}
          </button>
        ))}
      </div>

      <form
        className="mt-4 flex items-end gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          send();
        }}
      >
        <div className="flex-1">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Задайте уточняющий вопрос"
            aria-label="Текст вопроса"
          />
        </div>
        <Button type="submit" variant="primary" disabled={pending || !input.trim()}>
          <IconSend size={14} />
          Отправить
        </Button>
      </form>
    </div>
  );
}
