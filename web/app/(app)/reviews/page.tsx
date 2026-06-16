import { ShieldCheck } from "lucide-react";
import Link from "next/link";
import { ReviewControl } from "@/components/decision/ReviewControl";
import { StakesPill, VerdictPill } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { listDecisions } from "@/lib/data";
import { decisionTypeLabel } from "@/lib/verdict";

export default async function ReviewsPage() {
  const decisions = await listDecisions();
  const pending = decisions.filter((d) => d.review_required && d.review_state === "pending");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Reviews</h1>
        <p className="text-sm text-muted">High-stakes decisions awaiting your sign-off.</p>
      </div>

      {pending.length === 0 ? (
        <EmptyState
          icon={<ShieldCheck className="h-6 w-6" />}
          title="Nothing to review"
          description="No decisions are currently pending sign-off."
        />
      ) : (
        <div className="space-y-4">
          {pending.map((d) => (
            <Card key={d.id} className="p-5">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="max-w-2xl">
                  <Link
                    href={`/decisions/${d.id}`}
                    className="font-medium text-ink hover:text-brand-700"
                  >
                    {d.request.question}
                  </Link>
                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <span className="text-xs text-muted">
                      {decisionTypeLabel[d.request.decision_type] ?? d.request.decision_type}
                    </span>
                    <StakesPill stakes={d.stakes} />
                    <VerdictPill verdict={d.recommendation.verdict} />
                  </div>
                </div>
                <div className="w-full max-w-xs">
                  <ReviewControl decisionId={d.id} required initialState="pending" />
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
