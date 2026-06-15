import { NewDecisionForm } from "@/components/decision/NewDecisionForm";

export default function NewDecisionPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold">New decision</h1>
        <p className="text-sm text-muted">Bring a decision to TrueNorth for a judgment.</p>
      </div>
      <NewDecisionForm />
    </div>
  );
}
