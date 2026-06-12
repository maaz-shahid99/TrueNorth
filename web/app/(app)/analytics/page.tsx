import { BarChart3 } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Analytics</h1>
        <p className="text-sm text-muted">Verdict trends, calibration, and spend.</p>
      </div>
      <EmptyState
        icon={<BarChart3 className="h-6 w-6" />}
        title="Analytics arrives in UI-7"
        description="Verdict trends, confidence-vs-outcome calibration, and cost over time."
      />
    </div>
  );
}
