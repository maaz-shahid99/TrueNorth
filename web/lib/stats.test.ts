import { describe, expect, it } from "vitest";
import { mockDecisions } from "./mock";
import { computeStats } from "./stats";

describe("computeStats", () => {
  const stats = computeStats(mockDecisions);

  it("counts every decision", () => {
    expect(stats.total).toBe(mockDecisions.length);
  });

  it("breaks verdicts into the four-value scale that sums to the total", () => {
    expect(stats.verdictCounts).toHaveLength(4);
    const sum = stats.verdictCounts.reduce((a, v) => a + v.count, 0);
    expect(sum).toBe(stats.total);
  });

  it("breaks stakes into S1–S4", () => {
    expect(stats.stakesCounts.map((s) => s.stakes)).toEqual(["S1", "S2", "S3", "S4"]);
  });

  it("reports a 7-day trend and a confidence in [0,1]", () => {
    expect(stats.trend).toHaveLength(7);
    expect(stats.avgConfidence).toBeGreaterThanOrEqual(0);
    expect(stats.avgConfidence).toBeLessThanOrEqual(1);
  });

  it("returns zeroed aggregates for an empty list", () => {
    const empty = computeStats([]);
    expect(empty.total).toBe(0);
    expect(empty.endorsedPct).toBe(0);
    expect(empty.avgConfidence).toBe(0);
  });
});
