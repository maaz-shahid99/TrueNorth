import { Users } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";

export default function MembersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Members & API keys</h1>
        <p className="text-sm text-muted">Manage who can access this workspace.</p>
      </div>
      <EmptyState
        icon={<Users className="h-6 w-6" />}
        title="Member & key management arrives in UI-7"
        description="Mint, list, and revoke API keys and roles, backed by the engine KeyStore."
      />
    </div>
  );
}
