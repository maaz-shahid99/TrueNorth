import { Swords } from "lucide-react";
import { SectionCard } from "@/components/ui/Card";
import type { DevilsAdvocate } from "@/lib/types";

export function DevilsAdvocatePanel({ devil }: { devil: DevilsAdvocate }) {
  return (
    <SectionCard
      title={
        <span className="inline-flex items-center gap-2">
          <Swords className="h-4 w-4 text-muted" />
          Devil&apos;s advocate
        </span>
      }
    >
      <p className="text-sm leading-relaxed text-ink">{devil.counter_case}</p>
      {devil.failure_conditions.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-medium text-muted">Fails if</p>
          <ul className="mt-1 list-disc space-y-0.5 pl-4 text-sm text-ink">
            {devil.failure_conditions.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        </div>
      )}
      {devil.bias_flags.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {devil.bias_flags.map((b, i) => (
            <span
              key={i}
              className="rounded-full bg-verdict-caution-bg px-2.5 py-1 text-xs font-medium text-verdict-caution"
            >
              {b}
            </span>
          ))}
        </div>
      )}
    </SectionCard>
  );
}
