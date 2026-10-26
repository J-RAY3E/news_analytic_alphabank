"use client";

import { useEffect } from "react";
import { useSource } from "@/lib/api/hooks";
import { Button } from "@/components/ui/Button";
import { IconClose, IconExternal } from "@/components/ui/icons";

export function SourceDrawer({
  sourceId,
  onClose,
}: {
  sourceId: string | null;
  onClose: () => void;
}) {
  const sourceQuery = useSource(sourceId);

  useEffect(() => {
    if (!sourceId) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [sourceId, onClose]);

  if (!sourceId) return null;
  const source = sourceQuery.data;

  return (
    <div className="fixed inset-0 z-50 flex" role="dialog" aria-modal="true" aria-label="Источник">
      <div className="absolute inset-0 bg-ink/40" onClick={onClose} />
      <div className="relative z-10 ml-auto flex h-full w-[420px] max-w-[90vw] flex-col bg-canvas shadow-level-2">
        <div className="flex items-center justify-between border-b border-hairline px-4 py-3">
          <span className="text-heading-sm">Источник</span>
          <button
            type="button"
            onClick={onClose}
            className="min-h-[44px] min-w-[44px] rounded-sm text-ink-secondary hover:bg-canvas-soft"
            aria-label="Закрыть источник"
          >
            <IconClose />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-6 scrollbar-thin">
          {sourceQuery.isError ? (
            <>
              <p className="text-mono-trace text-ink-mute">{sourceId}</p>
              <p className="mt-2 text-body-md text-ink-secondary">
                Источник временно недоступен. Показан текст из кэша, он может быть
                неполным.
              </p>
            </>
          ) : source ? (
            <>
              <p className="text-mono-trace text-ink-mute">{sourceId}</p>
              <h3 className="mt-2 text-heading-md text-ink">{source.name}</h3>
              {source.url ? (
                <a
                  href={source.url}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="mt-4 inline-flex items-center gap-2 text-body-md text-blue-deep underline"
                >
                  <IconExternal size={14} />
                  Открыть оригинал в новой вкладке
                </a>
              ) : (
                <p className="mt-4 text-body-md text-ink-secondary">
                  Документ аналитики Альфа-Банка, страница {source.page}. Полный PDF доступен в
                  библиотеке исследований банка.
                </p>
              )}
              {source.snippet && (
                <p className="mt-4 text-body-md text-ink-secondary">{source.snippet}</p>
              )}
            </>
          ) : (
            <>
              <p className="text-mono-trace text-ink-mute">{sourceId}</p>
              <p className="mt-2 text-body-md text-ink-secondary">
                Описание для этого источника пока не найдено. Идентификатор сохранён в трассировке.
              </p>
            </>
          )}
          <div className="mt-6">
            <Button variant="secondary" size="sm" onClick={onClose}>
              Закрыть
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
