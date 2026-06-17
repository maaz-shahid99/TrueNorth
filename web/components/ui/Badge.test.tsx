import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReviewPill, StakesPill, VerdictPill } from "./Badge";

describe("pills", () => {
  it("renders the verdict label", () => {
    render(<VerdictPill verdict="Endorse-with-conditions" />);
    expect(screen.getByText("Endorse with conditions")).toBeInTheDocument();
  });

  it("renders the review state label", () => {
    render(<ReviewPill state="pending" />);
    expect(screen.getByText("Pending review")).toBeInTheDocument();
  });

  it("renders the stakes label", () => {
    render(<StakesPill stakes="S1" />);
    expect(screen.getByText("S1 · Existential")).toBeInTheDocument();
  });
});
