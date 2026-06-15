import { cn } from "@/lib/utils";

export function Stepper({ steps, current }: { steps: string[]; current: number }) {
  return (
    <ol className="flex flex-wrap items-center gap-2">
      {steps.map((s, i) => (
        <li key={s} className="flex items-center gap-2">
          <span
            className={cn(
              "flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium",
              i <= current ? "bg-brand-600 text-white" : "bg-line text-muted",
            )}
          >
            {i + 1}
          </span>
          <span className={cn("text-sm", i === current ? "font-medium text-ink" : "text-muted")}>
            {s}
          </span>
          {i < steps.length - 1 && <span className="mx-2 h-px w-6 bg-line" />}
        </li>
      ))}
    </ol>
  );
}
