import { CheckCircle2 } from "lucide-react";
import { SectionCard } from "@/components/ui/Card";
import type { Condition } from "@/lib/types";

export function ConditionsList({ conditions }: { conditions: Condition[] }) {
  if (conditions.length === 0) return null;
  return (
    <SectionCard title="Conditions">
      <ul className="space-y-3">
        {conditions.map((c, i) => (
          <li key={i} className="flex gap-3">
            <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-verdict-conditions" />
            <div>
              <p className="text-sm text-ink">{c.text}</p>
              {(c.owner || c.checkpoint) && (
                <p className="mt-0.5 text-xs text-muted">
                  {[c.owner, c.checkpoint].filter(Boolean).join(" · ")}
                </p>
              )}
            </div>
          </li>
        ))}
      </ul>
    </SectionCard>
  );
}
