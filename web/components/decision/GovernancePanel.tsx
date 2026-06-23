import { Badge } from "@/components/ui/Badge";
import { SectionCard } from "@/components/ui/Card";
import type { PolicyFlag } from "@/lib/types";

// Decision-rights policies that fired on this decision (GV-1/GV-2).
export function GovernancePanel({ flags }: { flags: PolicyFlag[] }) {
  if (!flags.length) return null;
  return (
    <SectionCard title="Governance — policies triggered">
      <ul className="space-y-2.5">
        {flags.map((f, i) => (
          <li key={i} className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <p className="text-sm font-medium text-ink">{f.name}</p>
              {f.reason && <p className="text-xs text-muted">{f.reason}</p>}
            </div>
            {f.effect === "require_review" ? (
              <Badge className="shrink-0 bg-verdict-caution-bg text-verdict-caution">
                requires {f.required_role}
              </Badge>
            ) : (
              <Badge className="shrink-0 bg-line text-muted">flag</Badge>
            )}
          </li>
        ))}
      </ul>
    </SectionCard>
  );
}
