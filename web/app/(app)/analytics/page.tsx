import { StakesBars } from "@/components/charts/StakesBars";
import { TrendChart } from "@/components/charts/TrendChart";
import { VerdictDonut } from "@/components/charts/VerdictDonut";
import { VerdictPill } from "@/components/ui/Badge";
import { SectionCard } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { listDecisions } from "@/lib/data";
import { formatCurrency, formatPercent } from "@/lib/format";
import { computeStats } from "@/lib/stats";
import { verdictHex } from "@/lib/verdict";

export default async function AnalyticsPage() {
  const decisions = await listDecisions();
  const stats = computeStats(decisions);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Analytics</h1>
        <p className="text-sm text-muted">Verdict trends, confidence, and spend.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Decisions" value={String(stats.total)} tint="blue" />
        <StatCard label="Endorsed" value={`${stats.endorsedPct}%`} tint="mint" />
        <StatCard label="Avg confidence" value={formatPercent(stats.avgConfidence)} tint="lilac" />
        <StatCard label="Spend" value={formatCurrency(stats.spend)} tint="peach" />
      </div>

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

      <SectionCard title="Average confidence by verdict">
        <div className="space-y-3">
          {stats.confidenceByVerdict.map((c) => (
            <div key={c.verdict} className="flex items-center gap-3">
              <div className="w-44 shrink-0">
                <VerdictPill verdict={c.verdict} />
              </div>
              <div className="h-2 flex-1 overflow-hidden rounded-full bg-app">
                <div
                  className="h-full rounded-full"
                  style={{ width: `${Math.round(c.avg * 100)}%`, background: verdictHex[c.verdict] }}
                />
              </div>
              <span className="w-20 text-right text-sm text-ink">
                {c.count ? `${formatPercent(c.avg)} · ${c.count}` : "—"}
              </span>
            </div>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}
