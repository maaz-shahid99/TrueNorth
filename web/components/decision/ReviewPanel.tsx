import { ReviewPill } from "@/components/ui/Badge";
import { SectionCard } from "@/components/ui/Card";
import type { DecisionRecord } from "@/lib/types";

export function ReviewPanel({ decision }: { decision: DecisionRecord }) {
  return (
    <SectionCard title="Review">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted">Status</span>
        <ReviewPill state={decision.review_state} />
      </div>
      <p className="mt-3 text-xs text-muted">
        {decision.review_required
          ? "Human sign-off is required for this stakes tier."
          : "No sign-off is required at this stakes tier."}
      </p>
      {/* Approve / reject actions land with the review queue (UI-5). */}
    </SectionCard>
  );
}
