import { PlusCircle } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";

export default function NewDecisionPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">New decision</h1>
        <p className="text-sm text-muted">Bring a decision to TrueNorth for a judgment.</p>
      </div>
      <EmptyState
        icon={<PlusCircle className="h-6 w-6" />}
        title="Submission stepper arrives in UI-3"
        description="Release go/no-go and discount approval, wired to POST /v1/decisions."
      />
    </div>
  );
}
