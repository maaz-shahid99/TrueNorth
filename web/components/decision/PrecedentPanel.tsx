import Link from "next/link";
import { VerdictPill } from "@/components/ui/Badge";
import { SectionCard } from "@/components/ui/Card";
import { formatDate, formatPercent } from "@/lib/format";
import type { Precedent } from "@/lib/types";
import { decisionTypeLabel } from "@/lib/verdict";

// Similar past decisions surfaced for this one (KG / DI-2 institutional memory).
export function PrecedentPanel({ precedents }: { precedents: Precedent[] }) {
  if (!precedents.length) return null;
  return (
    <SectionCard title="Precedent — similar past decisions">
      <ul className="divide-y divide-line">
        {precedents.map((p) => (
          <li key={p.decision_id} className="py-3 first:pt-0 last:pb-0">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <Link
                  href={`/decisions/${p.decision_id}`}
                  className="text-sm font-medium text-ink hover:text-brand-700 hover:underline"
                >
                  {p.question}
                </Link>
                <p className="mt-0.5 text-xs text-muted">
                  {decisionTypeLabel[p.decision_type] ?? p.decision_type} · {formatDate(p.created_at)}{" "}
                  · {formatPercent(p.similarity)} similar
                </p>
                {p.outcome_summary && (
                  <p className="mt-1 text-xs text-muted">Outcome — {p.outcome_summary}</p>
                )}
              </div>
              <div className="shrink-0">
                <VerdictPill verdict={p.verdict} />
              </div>
            </div>
          </li>
        ))}
      </ul>
    </SectionCard>
  );
}
