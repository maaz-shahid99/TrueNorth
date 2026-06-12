import Link from "next/link";
import { SectionCard } from "@/components/ui/Card";
import { VerdictPill } from "@/components/ui/Badge";
import { relativeTime } from "@/lib/format";
import type { Activity } from "@/lib/mock";
import type { DecisionRecord } from "@/lib/types";

export function RightPanel({
  pendingReviews,
  activity,
}: {
  pendingReviews: DecisionRecord[];
  activity: Activity[];
}) {
  return (
    <div className="space-y-5">
      <SectionCard title="Pending reviews">
        {pendingReviews.length === 0 ? (
          <p className="text-sm text-muted">Nothing awaiting sign-off.</p>
        ) : (
          <ul className="space-y-2">
            {pendingReviews.map((d) => (
              <li key={d.id}>
                <Link href={`/decisions/${d.id}`} className="block rounded-lg p-2 hover:bg-app">
                  <p className="line-clamp-2 text-sm text-ink">{d.request.question}</p>
                  <div className="mt-1.5">
                    <VerdictPill verdict={d.recommendation.verdict} />
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </SectionCard>
      <SectionCard title="Recent activity">
        <ul className="space-y-3">
          {activity.map((a) => (
            <li key={a.id} className="flex gap-3">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-400" />
              <div>
                <p className="text-sm text-ink">{a.text}</p>
                <p className="text-xs text-muted">{relativeTime(a.at)}</p>
              </div>
            </li>
          ))}
        </ul>
      </SectionCard>
    </div>
  );
}
