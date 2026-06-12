import Link from "next/link";
import { ReviewPill, StakesPill, VerdictPill } from "@/components/ui/Badge";
import { SectionCard } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { Table, Td, Th, Thead, Tr } from "@/components/ui/Table";
import { RightPanel } from "@/components/layout/RightPanel";
import { formatDate } from "@/lib/format";
import { mockActivity, mockDecisions } from "@/lib/mock";
import { decisionTypeLabel } from "@/lib/verdict";

export default function DashboardPage() {
  const pending = mockDecisions.filter((d) => d.review_state === "pending");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Overview</h1>
        <p className="text-sm text-muted">Decision activity across your workspace.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Decisions (30d)" value="128" delta={{ value: "+12%", direction: "up" }} tint="blue" />
        <StatCard label="Pending review" value={String(pending.length)} tint="peach" />
        <StatCard label="Endorsed" value="64%" delta={{ value: "+4%", direction: "up" }} tint="mint" />
        <StatCard label="Spend (30d)" value="$42.18" delta={{ value: "-3%", direction: "down" }} tint="lilac" />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <SectionCard
            title="Recent decisions"
            action={
              <Link href="/decisions" className="text-sm text-brand-600 hover:underline">
                View all
              </Link>
            }
            bodyClassName="p-0"
          >
            <Table>
              <Thead>
                <tr className="border-b border-line">
                  <Th className="pl-5">Decision</Th>
                  <Th>Type</Th>
                  <Th>Stakes</Th>
                  <Th>Verdict</Th>
                  <Th>Review</Th>
                  <Th className="pr-5">Date</Th>
                </tr>
              </Thead>
              <tbody>
                {mockDecisions.map((d) => (
                  <Tr key={d.id}>
                    <Td className="max-w-xs pl-5">
                      <Link
                        href={`/decisions/${d.id}`}
                        className="line-clamp-1 font-medium text-ink hover:text-brand-700"
                      >
                        {d.request.question}
                      </Link>
                    </Td>
                    <Td className="text-muted">
                      {decisionTypeLabel[d.request.decision_type] ?? d.request.decision_type}
                    </Td>
                    <Td>
                      <StakesPill stakes={d.stakes} />
                    </Td>
                    <Td>
                      <VerdictPill verdict={d.recommendation.verdict} />
                    </Td>
                    <Td>
                      <ReviewPill state={d.review_state} />
                    </Td>
                    <Td className="whitespace-nowrap pr-5 text-muted">{formatDate(d.created_at)}</Td>
                  </Tr>
                ))}
              </tbody>
            </Table>
          </SectionCard>
        </div>

        <RightPanel pendingReviews={pending} activity={mockActivity} />
      </div>
    </div>
  );
}
