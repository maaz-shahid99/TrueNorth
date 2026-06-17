import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AlignmentPanel } from "./AlignmentPanel";

describe("AlignmentPanel", () => {
  it("renders the score, rationale, and goal links", () => {
    render(
      <AlignmentPanel
        alignment={{
          score: 0.45,
          rationale: "mixed strategic fit",
          advances: [{ goal_id: "a", title: "Launch on time", relation: "advances", note: "" }],
          conflicts: [{ goal_id: "b", title: "Hold uptime", relation: "conflicts", note: "" }],
        }}
      />,
    );
    expect(screen.getByText("45%")).toBeInTheDocument();
    expect(screen.getByText("mixed strategic fit")).toBeInTheDocument();
    expect(screen.getByText("Launch on time")).toBeInTheDocument();
    expect(screen.getByText("Hold uptime")).toBeInTheDocument();
  });
});
