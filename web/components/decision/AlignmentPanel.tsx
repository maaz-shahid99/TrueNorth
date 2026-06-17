import { Check, X } from "lucide-react";
import { SectionCard } from "@/components/ui/Card";
import { formatPercent } from "@/lib/format";
import type { GoalAlignment } from "@/lib/types";

// How the decision aligns with active strategic goals (GA-4).
export function AlignmentPanel({ alignment }: { alignment: GoalAlignment }) {
  const pct = Math.round(alignment.score * 100);
  const tone =
    alignment.score >= 0.66
      ? "text-verdict-endorse"
      : alignment.score >= 0.4
        ? "text-verdict-caution"
        : "text-verdict-oppose";

  return (
    <SectionCard
      title="Strategic alignment"
      action={<span className={`text-sm font-semibold ${tone}`}>{formatPercent(alignment.score)}</span>}
    >
      <div className="h-2 w-full overflow-hidden rounded-full bg-app">
        <div
          className="h-full rounded-full bg-brand-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      {alignment.rationale && <p className="mt-3 text-sm text-ink">{alignment.rationale}</p>}

      {alignment.advances.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-medium uppercase tracking-wide text-muted">Advances</p>
          <ul className="mt-2 space-y-2">
            {alignment.advances.map((g, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <Check className="mt-0.5 h-4 w-4 shrink-0 text-verdict-endorse" />
                <span>
                  <span className="font-medium text-ink">{g.title}</span>
                  {g.note && <span className="text-muted"> — {g.note}</span>}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {alignment.conflicts.length > 0 && (
        <div className="mt-4">
          <p className="text-xs font-medium uppercase tracking-wide text-muted">Conflicts with</p>
          <ul className="mt-2 space-y-2">
            {alignment.conflicts.map((g, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                <X className="mt-0.5 h-4 w-4 shrink-0 text-verdict-oppose" />
                <span>
                  <span className="font-medium text-ink">{g.title}</span>
                  {g.note && <span className="text-muted"> — {g.note}</span>}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </SectionCard>
  );
}
