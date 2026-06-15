import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { DecisionsTable } from "@/components/decision/DecisionsTable";
import { listDecisions } from "@/lib/data";

export default async function DecisionsHistoryPage() {
  const decisions = await listDecisions();
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Decisions</h1>
          <p className="text-sm text-muted">Every decision your workspace has judged.</p>
        </div>
        <Link href="/decisions/new">
          <Button>New decision</Button>
        </Link>
      </div>
      <DecisionsTable decisions={decisions} />
    </div>
  );
}
