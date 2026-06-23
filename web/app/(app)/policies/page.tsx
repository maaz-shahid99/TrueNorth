import { PoliciesManager } from "@/components/governance/PoliciesManager";
import { listPolicies } from "@/lib/data";

export default async function PoliciesPage() {
  const policies = await listPolicies();
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Policies</h1>
        <p className="text-sm text-muted">
          Decision-rights rules (GV-1/GV-2). When a rule matches, it requires human sign-off or
          flags the decision — on top of the stakes-based default. Admin-managed.
        </p>
      </div>
      <PoliciesManager initialPolicies={policies} />
    </div>
  );
}
