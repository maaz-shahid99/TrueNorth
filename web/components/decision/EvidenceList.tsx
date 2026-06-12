import { Badge } from "@/components/ui/Badge";
import { SectionCard } from "@/components/ui/Card";
import type { EvidencePack } from "@/lib/types";
import { cn } from "@/lib/utils";

const sufficiencyStyle: Record<string, string> = {
  strong: "bg-verdict-endorse-bg text-verdict-endorse",
  adequate: "bg-verdict-endorse-bg text-verdict-endorse",
  thin: "bg-verdict-caution-bg text-verdict-caution",
  unavailable: "bg-verdict-oppose-bg text-verdict-oppose",
  unknown: "bg-line text-muted",
};

export function EvidenceList({ evidence }: { evidence: EvidencePack }) {
  return (
    <SectionCard
      title="Evidence"
      action={
        <Badge className={cn(sufficiencyStyle[evidence.sufficiency] ?? "bg-line text-muted")}>
          {evidence.sufficiency}
        </Badge>
      }
    >
      {evidence.items.length === 0 ? (
        <p className="text-sm text-muted">{evidence.notes || "No evidence gathered."}</p>
      ) : (
        <ul className="divide-y divide-line">
          {evidence.items.map((item, i) => (
            <li key={i} className="flex items-start justify-between gap-4 py-2.5 first:pt-0 last:pb-0">
              <div>
                <p className="text-sm text-ink">{item.claim}</p>
                <p className="text-xs text-muted">{item.source}</p>
              </div>
              <span className="shrink-0 text-sm font-medium text-ink">{item.value}</span>
            </li>
          ))}
        </ul>
      )}
    </SectionCard>
  );
}
