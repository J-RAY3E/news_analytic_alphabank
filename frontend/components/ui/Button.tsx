"use client";

import { cn } from "@/lib/utils";
import { forwardRef } from "react";

type Variant = "primary" | "secondary" | "on-dark" | "feedback" | "ghost";
type Size = "md" | "sm";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", type, ...props }, ref) => {
    return (
      <button
        ref={ref}
        type={type ?? "button"}
        className={cn(
          "inline-flex items-center justify-center gap-2 rounded-pill transition-colors select-none",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          size === "md" ? "min-h-[40px] px-4 text-body-md" : "min-h-[36px] px-3 text-caption",
          variant === "primary" &&
            "bg-primary text-on-primary hover:bg-primary-press active:bg-primary-press",
          variant === "secondary" &&
            "bg-canvas text-danger border border-danger hover:bg-risk-bg",
          variant === "on-dark" &&
            "bg-canvas text-ink hover:bg-canvas-soft",
          variant === "feedback" &&
            "bg-canvas text-ink-secondary border border-hairline hover:border-hairline-input",
          variant === "ghost" &&
            "bg-transparent text-ink-secondary hover:bg-canvas-soft",
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";
