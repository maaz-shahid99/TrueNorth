import { StakesBars } from "@/components/charts/StakesBars";
import { TrendChart } from "@/components/charts/TrendChart";
import { VerdictDonut } from "@/components/charts/VerdictDonut";
import { VerdictPill } from "@/components/ui/Badge";
import { SectionCard } from "@/components/ui/Card";
import { StatCard } from "@/components/ui/StatCard";
import { getCalibration, listDecisions } from "@/lib/data";
import { formatCurrency, formatPercent } from "@/lib/format";
import { computeStats } from "@/lib/stats";
import { verdictHex } from "@/lib/verdict";

export default async function AnalyticsPage() {
  const decisions = await listDecisions();
  const stats = computeStats(decisions);
  const calibration = await getCalibration();

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

      <div>
        <h2 className="text-lg font-semibold">Calibration &amp; learning</h2>
        <p className="text-sm text-muted">
          How well verdicts and confidence have predicted realized outcomes (DI-8).
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
        <StatCard
          label="Outcome coverage"
          value={formatPercent(calibration.outcome_coverage)}
          tint="blue"
        />
        <StatCard label="Scored outcomes" value={String(calibration.scored_outcomes)} tint="mint" />
        <StatCard
          label="Brier score"
          value={calibration.brier_score === null ? "—" : calibration.brier_score.toFixed(2)}
          tint="lilac"
        />
      </div>

      {calibration.scored_outcomes === 0 ? (
        <SectionCard title="Success by verdict">
          <p className="text-sm text-muted">
            No outcomes recorded yet. Record outcomes on decisions to build the learning loop.
          </p>
        </SectionCard>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <SectionCard title="Success rate by verdict">
            <div className="space-y-3">
              {calibration.by_verdict.map((v) => (
                <div key={v.verdict} className="flex items-center gap-3">
                  <div className="w-44 shrink-0">
                    <VerdictPill verdict={v.verdict} />
                  </div>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-app">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${Math.round((v.success_rate ?? 0) * 100)}%`,
                        background: verdictHex[v.verdict],
                      }}
                    />
                  </div>
                  <span className="w-20 text-right text-sm text-ink">
                    {v.success_rate === null ? "—" : `${formatPercent(v.success_rate)} · ${v.with_outcomes}`}
                  </span>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="Confidence calibration">
            <div className="space-y-3">
              {calibration.confidence_buckets.length === 0 ? (
                <p className="text-sm text-muted">Not enough scored outcomes yet.</p>
              ) : (
                calibration.confidence_buckets.map((b) => (
                  <div key={b.label} className="flex items-center justify-between gap-3 text-sm">
                    <span className="w-20 shrink-0 text-muted">{b.label}</span>
                    <span className="text-ink">
                      predicted {formatPercent(b.predicted_confidence)} · realized{" "}
                      {formatPercent(b.realized_success_rate)}
                    </span>
                    <span className="w-10 text-right text-muted">n={b.n}</span>
                  </div>
                ))
              )}
            </div>
          </SectionCard>
        </div>
      )}
    </div>
  );
}
