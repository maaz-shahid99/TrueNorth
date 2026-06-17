import { describe, expect, it } from "vitest";
import { formatCurrency, formatPercent, formatTokens } from "./format";

describe("formatCurrency", () => {
  it("shows 4 decimals for sub-dollar amounts", () => {
    expect(formatCurrency(0.4413)).toBe("$0.4413");
  });
  it("shows 2 decimals for whole-dollar amounts", () => {
    expect(formatCurrency(12.5)).toBe("$12.50");
    expect(formatCurrency(0)).toBe("$0.00");
  });
});

describe("formatPercent", () => {
  it("rounds a fraction to a whole percent", () => {
    expect(formatPercent(0.62)).toBe("62%");
    expect(formatPercent(1)).toBe("100%");
  });
});

describe("formatTokens", () => {
  it("abbreviates thousands", () => {
    expect(formatTokens(18420)).toBe("18.4k");
    expect(formatTokens(999)).toBe("999");
  });
});
