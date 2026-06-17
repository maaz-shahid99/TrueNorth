import { describe, expect, it } from "vitest";
import { VERDICTS } from "./types";
import { decisionTypeLabel, verdictHex, verdictStyles } from "./verdict";

describe("verdict mappings", () => {
  it("has a style + hex for every verdict in the scale", () => {
    for (const v of VERDICTS) {
      expect(verdictStyles[v]).toBeDefined();
      expect(verdictStyles[v].label.length).toBeGreaterThan(0);
      expect(verdictHex[v]).toMatch(/^#[0-9A-Fa-f]{6}$/);
    }
  });
});

describe("decisionTypeLabel", () => {
  it("labels the Phase 9 decision types", () => {
    expect(decisionTypeLabel.hiring_approval).toBe("Hiring approval");
    expect(decisionTypeLabel.vendor_procurement).toBe("Vendor / procurement");
    expect(decisionTypeLabel.budget_spend).toBe("Budget / spend");
    expect(decisionTypeLabel.project_go_no_go).toBe("Project go/no-go");
  });
});
