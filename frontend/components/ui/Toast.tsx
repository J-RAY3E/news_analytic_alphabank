"use client";

export function Toast({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div
      className="fixed bottom-6 left-1/2 z-50 -translate-x-1/2 rounded-pill bg-surface-dark px-4 py-2 text-caption text-on-primary shadow-level-2"
      role="status"
    >
      {message}
    </div>
  );
}
