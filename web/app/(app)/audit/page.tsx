import { FileCheck2 } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";

export default function AuditPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Audit</h1>
        <p className="text-sm text-muted">The tamper-evident decision ledger.</p>
      </div>
      <EmptyState
        icon={<FileCheck2 className="h-6 w-6" />}
        title="Audit timeline arrives in UI-5"
        description="Per-decision history and a chain-integrity check, wired to GET /v1/audit/verify."
      />
    </div>
  );
}
