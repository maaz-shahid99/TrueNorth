import { History } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";

export default function DecisionsHistoryPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Decisions</h1>
        <p className="text-sm text-muted">Every decision your workspace has judged.</p>
      </div>
      <EmptyState
        icon={<History className="h-6 w-6" />}
        title="History table arrives in UI-3"
        description="This will list and filter all recorded decisions, wired to GET /v1/decisions."
      />
    </div>
  );
}
