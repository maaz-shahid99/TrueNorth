import { FileSearch } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";

export default async function DecisionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Decision</h1>
        <p className="text-sm text-muted">{id}</p>
      </div>
      <EmptyState
        icon={<FileSearch className="h-6 w-6" />}
        title="The signature Decision Detail view is next (UI-2)"
        description="Verdict banner, lens cards, devil's advocate, evidence, and the minority report — wired to GET /v1/decisions/{id}."
      />
    </div>
  );
}
