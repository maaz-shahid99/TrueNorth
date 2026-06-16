import { SectionCard } from "@/components/ui/Card";
import type { ReviewAction, ReviewState } from "@/lib/types";
import { ReviewControl } from "./ReviewControl";

export function ReviewPanel({
  decisionId,
  required,
  initialState,
  initialHistory,
}: {
  decisionId: string;
  required: boolean;
  initialState: ReviewState;
  initialHistory: ReviewAction[];
}) {
  return (
    <SectionCard title="Review">
      <ReviewControl
        decisionId={decisionId}
        required={required}
        initialState={initialState}
        initialHistory={initialHistory}
      />
    </SectionCard>
  );
}
