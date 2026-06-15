import Link from "next/link";
import { StakesBars } from "@/components/charts/StakesBars";
import { TrendChart } from "@/components/charts/TrendChart";
import { VerdictDonut } from "@/components/charts/VerdictDonut";
import { RightPanel } from "@/components/layout/RightPanel";
import { ReviewPill, StakesPill, VerdictPill } from "@/components/ui/Badge";
import { SectionCard } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { Table, Td, Th, Thead, Tr } from "@/components/ui/Table";
import { listDecisions } from "@/lib/data";
import { formatCurrency, formatDate } from "@/lib/format";
import type { Activity } from "@/lib/mock";
import { computeStats } from "@/lib/stats";
import { decisionTypeLabel, verdictStyles } from "@/lib/verdict";

export default async function DashboardPage() {
  const decisions = await listDecisions();
  const stats = computeStats(decisions);
  const pending = decisions.filter((d) => d.review_state === "pending");
  const recent = decisions.slice(0, 6);
  const activity: Activity[] = decisions.slice(0, 5).map((d) => ({
    id: d.id,
    text: `Judged “${d.request.question}” — ${verdictStyles[d.recommendation.verdict].label}`,
    at: d.created_at,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Overview</h1>
        <p className="text-sm text-muted">Decision activity across your workspace.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Decisions" value={String(stats.total)} tint="blue" />
        <StatCard label="Pending review" value={String(stats.pending)} tint="peach" />
        <StatCard label="Endorsed" value={`${stats.endorsedPct}%`} tint="mint" />
        <StatCard label="Spend" value={formatCurrency(stats.spend)} tint="lilac" />
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="space-y-6 xl:col-span-2">
          <SectionCard title="Decisions over time">
            <TrendChart data={stats.trend} />
          </SectionCard>

          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <SectionCard title="Verdict mix">
              <VerdictDonut data={stats.verdictCounts} />
            </SectionCard>
            <SectionCard title="By stakes">
              <StakesBars data={stats.stakesCounts} />
            </SectionCard>
          </div>

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
                {recent.map((d) => (
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

        <RightPanel pendingReviews={pending} activity={activity} />
      </div>
    </div>
  );
}
