import { cn } from "@/lib/utils";
import { forwardRef, useId } from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string | null;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, id, ...props }, ref) => {
    const autoId = useId();
    const inputId = id ?? autoId;
    return (
      <div className="flex flex-col gap-1">
        {label && (
          <label htmlFor={inputId} className="text-caption text-ink-secondary">
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            "w-full rounded-sm border bg-canvas px-3 py-2 text-body-md text-ink",
            "placeholder:text-ink-mute",
            "focus:border-blue focus:ring-[3px] focus:ring-[rgba(38,111,255,0.20)]",
            error ? "border-primary" : "border-hairline-input",
            className
          )}
          aria-invalid={Boolean(error)}
          {...props}
        />
        {error && <span className="text-caption text-danger">{error}</span>}
      </div>
    );
  }
);
Input.displayName = "Input";

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string | null;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, id, ...props }, ref) => {
    const autoId = useId();
    const inputId = id ?? autoId;
    return (
      <div className="flex flex-col gap-1">
        {label && (
          <label htmlFor={inputId} className="text-caption text-ink-secondary">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={inputId}
          className={cn(
            "w-full rounded-sm border bg-canvas px-3 py-2 text-body-md text-ink resize-y",
            "placeholder:text-ink-mute",
            "focus:border-blue focus:ring-[3px] focus:ring-[rgba(38,111,255,0.20)]",
            error ? "border-primary" : "border-hairline-input",
            className
          )}
          aria-invalid={Boolean(error)}
          {...props}
        />
        {error && <span className="text-caption text-danger">{error}</span>}
      </div>
    );
  }
);
Textarea.displayName = "Textarea";
