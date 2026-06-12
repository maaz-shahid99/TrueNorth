import { formatPercent } from "@/lib/format";
import type { Recommendation } from "@/lib/types";
import { cn } from "@/lib/utils";
import { verdictStyles } from "@/lib/verdict";

export function VerdictBanner({ recommendation }: { recommendation: Recommendation }) {
  const s = verdictStyles[recommendation.verdict];
  const pct = Math.round(recommendation.confidence * 100);

  return (
    <div className={cn("rounded-2xl border border-line p-6", s.bg)}>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className={cn("h-3 w-3 rounded-full", s.dot)} />
          <div>
            <p className="text-xs uppercase tracking-wide text-muted">Verdict</p>
            <h2 className={cn("text-2xl font-semibold", s.text)}>{s.label}</h2>
          </div>
        </div>
        <div className="min-w-[180px]">
          <div className="flex items-center justify-between text-xs text-muted">
            <span>Confidence</span>
            <span className="font-medium text-ink">{formatPercent(recommendation.confidence)}</span>
          </div>
          <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-white/70">
            <div className={cn("h-full rounded-full", s.dot)} style={{ width: `${pct}%` }} />
          </div>
        </div>
      </div>
      <p className="mt-4 text-sm leading-relaxed text-ink">{recommendation.reasoning}</p>
    </div>
  );
}
