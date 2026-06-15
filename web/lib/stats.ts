// Dashboard aggregates computed from the decisions list (no dedicated stats endpoint yet).
import type { DecisionRecord, StakesTier, Verdict } from "./types";
import { VERDICTS } from "./types";

export interface DashStats {
  total: number;
  pending: number;
  endorsedPct: number;
  spend: number;
  verdictCounts: { verdict: Verdict; count: number }[];
  stakesCounts: { stakes: StakesTier; count: number }[];
  trend: { label: string; count: number }[];
}

const STAKES: StakesTier[] = ["S1", "S2", "S3", "S4"];

export function computeStats(decisions: DecisionRecord[]): DashStats {
  const total = decisions.length;
  const pending = decisions.filter((d) => d.review_state === "pending").length;
  const endorsed = decisions.filter(
    (d) =>
      d.recommendation.verdict === "Endorse" ||
      d.recommendation.verdict === "Endorse-with-conditions",
  ).length;
  const endorsedPct = total ? Math.round((100 * endorsed) / total) : 0;
  const spend =
    Math.round(decisions.reduce((a, d) => a + (d.usage?.total_cost_usd ?? 0), 0) * 100) / 100;

  const verdictCounts = VERDICTS.map((v) => ({
    verdict: v,
    count: decisions.filter((d) => d.recommendation.verdict === v).length,
  }));
  const stakesCounts = STAKES.map((s) => ({
    stakes: s,
    count: decisions.filter((d) => d.stakes === s).length,
  }));

  // Counts per day over the last 7 calendar days (including empty days).
  const days: { label: string; key: string; count: number }[] = [];
  for (let i = 6; i >= 0; i--) {
    const day = new Date();
    day.setHours(0, 0, 0, 0);
    day.setDate(day.getDate() - i);
    days.push({
      label: day.toLocaleDateString(undefined, { month: "short", day: "numeric" }),
      key: day.toISOString().slice(0, 10),
      count: 0,
    });
  }
  for (const dec of decisions) {
    const key = new Date(dec.created_at).toISOString().slice(0, 10);
    const bucket = days.find((x) => x.key === key);
    if (bucket) bucket.count++;
  }

  return {
    total,
    pending,
    endorsedPct,
    spend,
    verdictCounts,
    stakesCounts,
    trend: days.map(({ label, count }) => ({ label, count })),
  };
}
