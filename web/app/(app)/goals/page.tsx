import { GoalsManager } from "@/components/strategy/GoalsManager";
import { listGoals } from "@/lib/data";

export default async function GoalsPage() {
  const goals = await listGoals();
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Goals</h1>
        <p className="text-sm text-muted">
          Strategic goals &amp; OKRs that decisions are scored against (GA-1). Admin-managed; new
          decisions are judged for how they advance or conflict with these.
        </p>
      </div>
      <GoalsManager initialGoals={goals} />
    </div>
  );
}
