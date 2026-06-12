import { ShieldCheck } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";

export default function ReviewsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Reviews</h1>
        <p className="text-sm text-muted">High-stakes decisions awaiting your sign-off.</p>
      </div>
      <EmptyState
        icon={<ShieldCheck className="h-6 w-6" />}
        title="Review queue arrives in UI-5"
        description="Approve or reject pending decisions; actions append to the audit chain."
      />
    </div>
  );
}
