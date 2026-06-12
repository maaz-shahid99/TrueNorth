import { Plug } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";

export default function ConnectorsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Connectors</h1>
        <p className="text-sm text-muted">Evidence sources for each decision type.</p>
      </div>
      <EmptyState
        icon={<Plug className="h-6 w-6" />}
        title="Connector settings arrive in UI-7"
        description="Configure the GitHub token and, later, CRM sources for discount approvals."
      />
    </div>
  );
}
