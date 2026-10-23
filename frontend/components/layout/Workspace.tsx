"use client";

import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";
import { IconClose } from "@/components/ui/icons";

export type MobileTab = "feed" | "insight" | "trace" | "chat";

interface WorkspaceProps {
  feed: React.ReactNode;
  insight: React.ReactNode;
  trace: React.ReactNode;
}

function Drawer({
  open,
  onClose,
  side,
  label,
  children,
}: {
  open: boolean;
  onClose: () => void;
  side: "left" | "right";
  label: string;
  children: React.ReactNode;
}) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40 flex" role="dialog" aria-modal="true" aria-label={label}>
      <div className="absolute inset-0 bg-ink/40" onClick={onClose} />
      <div
        className={cn(
          "relative z-10 flex h-full w-[340px] max-w-[85vw] flex-col bg-canvas shadow-level-2",
          side === "left" ? "mr-auto" : "ml-auto"
        )}
      >
        <div className="flex items-center justify-between border-b border-hairline px-4 py-3">
          <span className="text-heading-sm">{label}</span>
          <button
            type="button"
            onClick={onClose}
            className="min-h-[44px] min-w-[44px] rounded-sm text-ink-secondary hover:bg-canvas-soft"
            aria-label="Закрыть панель"
          >
            <IconClose />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto scrollbar-thin">{children}</div>
      </div>
    </div>
  );
}

const TABS: { key: MobileTab; label: string }[] = [
  { key: "feed", label: "Лента" },
  { key: "insight", label: "Анализ" },
  { key: "trace", label: "Trace" },
  { key: "chat", label: "Чат" },
];

export function Workspace({ feed, insight, trace }: WorkspaceProps) {
  const [showTrace, setShowTrace] = useState(false);
  const [showFeed, setShowFeed] = useState(false);
  const [tab, setTab] = useState<MobileTab>("feed");

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setShowTrace(false);
        setShowFeed(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className="relative">
      <div className="hidden gap-4 p-4 min-[1280px]:grid min-[1280px]:grid-cols-[340px_minmax(0,760px)_380px]">
        <div className="overflow-y-auto scrollbar-thin">{feed}</div>
        <div className="overflow-y-auto scrollbar-thin">{insight}</div>
        <div className="overflow-y-auto scrollbar-thin">{trace}</div>
      </div>

      <div className="hidden gap-4 p-4 min-[1024px]:grid min-[1280px]:hidden min-[1024px]:grid-cols-[340px_minmax(0,1fr)]">
        <div className="overflow-y-auto scrollbar-thin">{feed}</div>
        <div className="overflow-y-auto scrollbar-thin">{insight}</div>
        <button
          type="button"
          onClick={() => setShowTrace(true)}
          className="fixed bottom-6 right-6 z-30 min-h-[44px] rounded-pill bg-surface-dark px-5 text-body-md text-on-primary shadow-level-2"
        >
          Trace
        </button>
      </div>

      <div className="hidden min-[768px]:block max-[1023px]:hidden">
        <div className="p-4">
          {insight}
        </div>
        <button
          type="button"
          onClick={() => setShowFeed(true)}
          className="fixed bottom-6 left-6 z-30 min-h-[44px] rounded-pill bg-surface-dark px-5 text-body-md text-on-primary shadow-level-2"
        >
          Лента
        </button>
        <button
          type="button"
          onClick={() => setShowTrace(true)}
          className="fixed bottom-6 right-6 z-30 min-h-[44px] rounded-pill bg-surface-dark px-5 text-body-md text-on-primary shadow-level-2"
        >
          Trace
        </button>
      </div>

      <div className="min-[768px]:hidden pb-16">
        <div
          className={cn(
            "p-4",
            tab === "trace" && "bg-surface-dark min-h-[calc(100vh-4rem)]",
            tab === "feed" && "bg-canvas-soft"
          )}
        >
          {tab === "feed" && feed}
          {tab === "insight" && insight}
          {tab === "trace" && trace}
          {tab === "chat" && insight}
        </div>
        <nav
          className="fixed bottom-0 left-0 right-0 z-30 grid grid-cols-4 border-t border-hairline bg-canvas"
          aria-label="Разделы Radar"
        >
          {TABS.map((t) => (
            <button
              key={t.key}
              type="button"
              onClick={() => setTab(t.key)}
              className={cn(
                "min-h-[44px] text-body-md",
                tab === t.key ? "font-medium text-danger" : "text-ink-secondary"
              )}
              aria-current={tab === t.key ? "page" : undefined}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </div>

      <Drawer open={showFeed} onClose={() => setShowFeed(false)} side="left" label="Лента событий">
        {feed}
      </Drawer>
      <Drawer open={showTrace} onClose={() => setShowTrace(false)} side="right" label="Agent Trace">
        {trace}
      </Drawer>
    </div>
  );
}
