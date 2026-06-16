import { Plug } from "lucide-react";
import { Badge } from "@/components/ui/Badge";
import { SectionCard } from "@/components/ui/Card";

const connectors = [
  {
    decisionType: "Release go/no-go",
    name: "GitHub",
    status: "Available",
    statusClass: "bg-verdict-endorse-bg text-verdict-endorse",
    description:
      "Pulls open bug-labelled issues, recent CI pass rate, and open PRs for the repository on the decision. Supply the repo as owner/name when submitting.",
    config: "Set GITHUB_TOKEN in the engine environment for private repos.",
  },
  {
    decisionType: "Discount approval",
    name: "Manual deal facts",
    status: "Available",
    statusClass: "bg-verdict-endorse-bg text-verdict-endorse",
    description:
      "Turns the deal facts you enter (discount %, gross margin, customer tier, etc.) into cited evidence. This is the seam a CRM connector replaces later.",
    config: "No setup required — facts are entered at submission time.",
  },
  {
    decisionType: "Discount approval",
    name: "Salesforce / HubSpot (CRM)",
    status: "Planned",
    statusClass: "bg-line text-muted",
    description:
      "A future connector that reads opportunity, pricing, and account data directly from the CRM, replacing the manual deal-fact entry.",
    config: "Not yet available.",
  },
];

export default function ConnectorsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Connectors</h1>
        <p className="text-sm text-muted">Evidence sources for each decision type (DF-1).</p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {connectors.map((c, i) => (
          <SectionCard
            key={i}
            title={
              <span className="inline-flex items-center gap-2">
                <Plug className="h-4 w-4 text-muted" />
                {c.name}
              </span>
            }
            action={<Badge className={c.statusClass}>{c.status}</Badge>}
          >
            <p className="text-xs font-medium uppercase tracking-wide text-muted">
              {c.decisionType}
            </p>
            <p className="mt-2 text-sm text-ink">{c.description}</p>
            <p className="mt-3 text-xs text-muted">{c.config}</p>
          </SectionCard>
        ))}
      </div>
    </div>
  );
}
