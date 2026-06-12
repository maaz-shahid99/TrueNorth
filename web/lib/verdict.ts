// Shared visual mapping for the verdict scale, review states, and stakes tiers.
// Class names are written as full literals so Tailwind's scanner picks them up.
import type { ReviewState, StakesTier, Verdict } from "./types";

export const verdictStyles: Record<
  Verdict,
  { text: string; bg: string; dot: string; label: string }
> = {
  Endorse: {
    text: "text-verdict-endorse",
    bg: "bg-verdict-endorse-bg",
    dot: "bg-verdict-endorse",
    label: "Endorse",
  },
  "Endorse-with-conditions": {
    text: "text-verdict-conditions",
    bg: "bg-verdict-conditions-bg",
    dot: "bg-verdict-conditions",
    label: "Endorse with conditions",
  },
  Caution: {
    text: "text-verdict-caution",
    bg: "bg-verdict-caution-bg",
    dot: "bg-verdict-caution",
    label: "Caution",
  },
  Oppose: {
    text: "text-verdict-oppose",
    bg: "bg-verdict-oppose-bg",
    dot: "bg-verdict-oppose",
    label: "Oppose",
  },
};

export const reviewStyles: Record<
  ReviewState,
  { text: string; bg: string; label: string }
> = {
  not_required: { text: "text-muted", bg: "bg-line", label: "Not required" },
  pending: { text: "text-verdict-caution", bg: "bg-verdict-caution-bg", label: "Pending review" },
  approved: { text: "text-verdict-endorse", bg: "bg-verdict-endorse-bg", label: "Approved" },
  rejected: { text: "text-verdict-oppose", bg: "bg-verdict-oppose-bg", label: "Rejected" },
};

export const stakesLabel: Record<StakesTier, string> = {
  S1: "S1 · Existential",
  S2: "S2 · Executive",
  S3: "S3 · Departmental",
  S4: "S4 · Routine",
};

export const decisionTypeLabel: Record<string, string> = {
  release_go_no_go: "Release go/no-go",
  discount_approval: "Discount approval",
};
