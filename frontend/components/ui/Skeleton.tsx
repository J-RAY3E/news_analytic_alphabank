import { cn } from "@/lib/utils";

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-canvas-track", className)}
      aria-hidden
    />
  );
}

export function FeedCardSkeleton() {
  return (
    <div className="rounded-lg border border-hairline bg-canvas p-6">
      <div className="flex items-center justify-between">
        <Skeleton className="h-3 w-28" />
        <Skeleton className="h-6 w-12 rounded-pill" />
      </div>
      <Skeleton className="mt-4 h-5 w-full" />
      <Skeleton className="mt-2 h-5 w-3/4" />
      <Skeleton className="mt-3 h-3 w-2/3" />
      <div className="mt-4 flex gap-2">
        <Skeleton className="h-6 w-20 rounded-pill" />
        <Skeleton className="h-6 w-24 rounded-pill" />
      </div>
    </div>
  );
}

export function InsightSectionSkeleton() {
  return (
    <div className="rounded-lg border border-hairline bg-canvas p-8">
      <Skeleton className="h-5 w-1/3" />
      <div className="mt-4 space-y-3">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-11/12" />
        <Skeleton className="h-4 w-4/5" />
      </div>
   </div>
  );
}
