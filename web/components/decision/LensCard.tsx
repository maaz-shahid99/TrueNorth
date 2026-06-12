import { Card } from "@/components/ui/Card";
import { formatPercent } from "@/lib/format";
import type { LensName, ScoredLens } from "@/lib/types";
import { cn } from "@/lib/utils";
import { verdictStyles } from "@/lib/verdict";

const lensLabel: Record<LensName, string> = {
  financial: "Financial",
  strategic: "Strategic",
  risk: "Risk",
  legal: "Legal",
  people: "People",
  customer: "Customer",
  esg: "ESG",
};

export function LensCard({ scored }: { scored: ScoredLens }) {
  const { lens, assessment } = scored;
  const s = verdictStyles[assessment.leaning];

  if (!assessment.applicable) {
    return (
      <Card className="p-4 opacity-60">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-semibold">{lensLabel[lens]}</h4>
          <span className="text-xs text-muted">Not applicable</span>
        </div>
        <p className="mt-2 text-sm text-muted">{assessment.rationale}</p>
      </Card>
    );
  }

  return (
    <Card className="p-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold">{lensLabel[lens]}</h4>
        <span
          className={cn(
            "inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-xs font-medium",
            s.bg,
            s.text,
          )}
        >
          <span className={cn("h-1.5 w-1.5 rounded-full", s.dot)} />
          {s.label}
        </span>
      </div>
      <p className="mt-2 text-sm leading-relaxed text-ink">{assessment.rationale}</p>
      {assessment.key_risks.length > 0 && (
        <div className="mt-3">
          <p className="text-xs font-medium text-muted">Key risks</p>
          <ul className="mt-1 list-disc space-y-0.5 pl-4 text-sm text-ink">
            {assessment.key_risks.map((r, i) => (
              <li key={i}>{r}</li>
            ))}
          </ul>
        </div>
      )}
      {assessment.cited_evidence.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {assessment.cited_evidence.map((c, i) => (
            <span key={i} className="rounded-md bg-app px-2 py-0.5 text-xs text-muted">
              {c}
            </span>
          ))}
        </div>
      )}
      <div className="mt-3 text-xs text-muted">Confidence {formatPercent(assessment.confidence)}</div>
    </Card>
  );
}
