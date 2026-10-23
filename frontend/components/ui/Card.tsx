import { cn } from "@/lib/utils";
import { forwardRef } from "react";

export const Card = forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { elevation?: 0 | 1 | 2 }
>(({ className, elevation = 0, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg bg-canvas border border-hairline",
      elevation === 1 && "shadow-level-1 border-transparent",
      elevation === 2 && "shadow-level-2 border-transparent",
      className
    )}
    {...props}
  />
));
Card.displayName = "Card";
