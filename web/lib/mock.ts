// Mock data so the shell and pages render without the engine running (UI-1), and a sample
// DecisionRecord that doubles as the offline fixture for the Decision Detail page (UI-2).
import type { ApiKeyInfo, DecisionRecord, DecisionRequest, Goal, StakesTier } from "./types";

export const sampleDecision: DecisionRecord = {
  id: "demo-release-2-4",
  request: {
    decision_type: "release_go_no_go",
    question: "Should we ship release 2.4 tonight ahead of the launch event?",
    options: ["Proceed", "Do nothing"],
    context: "Marketing wants 2.4 live before tomorrow's launch keynote.",
    stakes: "S2",
    repo: "acme/app",
    inputs: {},
  },
  stakes: "S2",
  model_used: "claude-opus-4-8",
  evidence: {
    items: [
      { claim: "Open bug-labelled issues", value: "37", source: "github:acme/app/issues?label=bug" },
      { claim: "Recent CI pass rate (last completed runs)", value: "55% of 20", source: "github:acme/app/actions/runs" },
      { claim: "Open pull requests", value: "14", source: "github:acme/app/pulls" },
    ],
    sufficiency: "adequate",
    notes: "",
  },
  lenses: [
    {
      lens: "risk",
      assessment: {
        leaning: "Oppose",
        rationale:
          "A 55% CI pass rate with 37 open bugs is a weak readiness signal; shipping tonight risks a high-visibility regression during the keynote.",
        key_risks: ["Checkout regression under load", "No tested rollback for the new pricing service"],
        cited_evidence: ["Recent CI pass rate (last completed runs)", "Open bug-labelled issues"],
        confidence: 0.74,
        applicable: true,
      },
    },
    {
      lens: "customer",
      assessment: {
        leaning: "Caution",
        rationale:
          "Customers gain the new dashboard, but an outage during the keynote would damage trust with the exact audience the event targets.",
        key_risks: ["Trust hit if a demo path breaks live"],
        cited_evidence: ["Open bug-labelled issues"],
        confidence: 0.6,
        applicable: true,
      },
    },
    {
      lens: "strategic",
      assessment: {
        leaning: "Endorse-with-conditions",
        rationale:
          "Hitting the keynote has real strategic value; a feature-flagged, gradual rollout captures most upside without betting the event on it.",
        key_risks: ["Slipping the date dampens launch momentum"],
        cited_evidence: [],
        confidence: 0.55,
        applicable: true,
      },
    },
    {
      lens: "people",
      assessment: {
        leaning: "Caution",
        rationale: "A tonight ship implies an on-call scramble during the event for an already-stretched team.",
        key_risks: ["On-call burnout", "Keynote-night firefighting"],
        cited_evidence: [],
        confidence: 0.5,
        applicable: true,
      },
    },
  ],
  devils_advocate: {
    counter_case:
      "The strongest case against shipping: the readiness signals are poor (low CI, high bug count) and the blast radius is maximal precisely because the keynote concentrates attention. A broken demo path costs more than a delayed feature.",
    failure_conditions: [
      "A P1 in checkout or the pricing service surfaces during the event",
      "Rollback is needed but hasn't been rehearsed",
    ],
    bias_flags: ["deadline-driven urgency (anchoring on the event date)"],
  },
  recommendation: {
    verdict: "Endorse-with-conditions",
    reasoning:
      "Strategic value of the keynote is real, but risk and people lenses are clearly uneasy given a 55% CI pass rate and 37 open bugs. Ship only behind a feature flag with a staged rollout and a rehearsed rollback, decoupled from the live demo path.",
    confidence: 0.62,
    conditions: [
      { text: "Ship behind a feature flag at 5% → 25% → 100% over 24h", owner: "Release eng", checkpoint: "pre-keynote" },
      { text: "Rehearse and verify the rollback runbook before go-live", owner: "On-call lead", checkpoint: "T-2h" },
      { text: "Keep the keynote demo on the current stable build", owner: "DevRel", checkpoint: "keynote" },
    ],
    minority_report:
      "If the demo path is fully isolated from 2.4 and the flag truly defaults off, the residual risk may be low enough that a clean Endorse is defensible — the conditions could be over-cautious for a flagged release.",
  },
  review_required: true,
  review_state: "pending",
  precedents: [
    {
      decision_id: "d-release-2-5",
      question: "Ship release 2.5 after a clean QA cycle?",
      decision_type: "release_go_no_go",
      verdict: "Endorse",
      stakes: "S3",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString(),
      similarity: 0.46,
      outcome_summary: "success: shipped with no incidents after a staged rollout",
    },
    {
      decision_id: "d-release-risky",
      question: "Ship release 2.2 the night before a board demo?",
      decision_type: "release_go_no_go",
      verdict: "Oppose",
      stakes: "S2",
      created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 95).toISOString(),
      similarity: 0.39,
      outcome_summary: "miss: a Sev1 surfaced during the demo when shipped anyway",
    },
  ],
  alignment: {
    score: 0.45,
    rationale:
      "Shipping for the keynote advances the launch goal but pulls against the reliability goal given the weak readiness signals.",
    advances: [
      {
        goal_id: "g-launch",
        title: "Land the Q3 platform launch on schedule",
        relation: "advances",
        note: "Hitting the keynote is a direct contribution to the launch goal.",
      },
    ],
    conflicts: [
      {
        goal_id: "g-reliability",
        title: "Hold 99.9% uptime with zero Sev1 incidents",
        relation: "conflicts",
        note: "A 55% CI pass rate and 37 open bugs put the reliability goal at risk.",
      },
    ],
  },
  usage: {
    calls: [],
    total_input_tokens: 18420,
    total_output_tokens: 2110,
    total_cost_usd: 0.4413,
    total_latency_ms: 13720,
  },
  created_at: new Date(Date.now() - 1000 * 60 * 42).toISOString(),
  engine_version: "0.1.0",
};

function variant(
  id: string,
  question: string,
  verdict: DecisionRecord["recommendation"]["verdict"],
  stakes: DecisionRecord["stakes"],
  review_state: DecisionRecord["review_state"],
  minutesAgo: number,
): DecisionRecord {
  return {
    ...sampleDecision,
    id,
    stakes,
    review_required: review_state !== "not_required",
    review_state,
    request: { ...sampleDecision.request, question, stakes },
    recommendation: { ...sampleDecision.recommendation, verdict },
    created_at: new Date(Date.now() - 1000 * 60 * minutesAgo).toISOString(),
  };
}

export const mockDecisions: DecisionRecord[] = [
  sampleDecision,
  variant("d-discount-globex", "Approve a 35% discount on the Globex renewal?", "Caution", "S3", "not_required", 180),
  variant("d-release-2-5", "Ship release 2.5 after a clean QA cycle?", "Endorse", "S3", "not_required", 1440),
  variant("d-vendor-switch", "Switch our primary cloud vendor next quarter?", "Oppose", "S1", "rejected", 2880),
  variant("d-hiring-freeze", "Lift the engineering hiring freeze in Q3?", "Endorse-with-conditions", "S2", "approved", 5760),
];

export interface Activity {
  id: string;
  text: string;
  at: string;
}

export const mockActivity: Activity[] = [
  { id: "a1", text: "Reviewer approved “Lift the engineering hiring freeze”", at: new Date(Date.now() - 1000 * 60 * 9).toISOString() },
  { id: "a2", text: "New decision submitted: ship release 2.4", at: new Date(Date.now() - 1000 * 60 * 42).toISOString() },
  { id: "a3", text: "Outcome recorded for “Switch primary cloud vendor”", at: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString() },
  { id: "a4", text: "Audit chain verified — 128 entries intact", at: new Date(Date.now() - 1000 * 60 * 60 * 7).toISOString() },
];

export const mockKeys: ApiKeyInfo[] = [
  {
    id: "key-root",
    tenant_id: "default",
    subject: "dev@truenorth.local",
    roles: ["admin"],
    active: true,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 9).toISOString(),
  },
  {
    id: "key-ci",
    tenant_id: "default",
    subject: "ci-bot@truenorth.local",
    roles: ["requester"],
    active: true,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3).toISOString(),
  },
  {
    id: "key-old",
    tenant_id: "default",
    subject: "former-lead@truenorth.local",
    roles: ["reviewer"],
    active: false,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 40).toISOString(),
  },
];

export const mockGoals: Goal[] = [
  {
    id: "g-launch",
    title: "Land the Q3 platform launch on schedule",
    description: "Ship the new dashboard and pricing service to GA by the end of Q3.",
    level: "board",
    owner: "CEO",
    parent_id: null,
    metric: "GA by Sep 30",
    status: "active",
    source: "manual",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 60).toISOString(),
  },
  {
    id: "g-reliability",
    title: "Hold 99.9% uptime with zero Sev1 incidents",
    description: "Protect platform reliability through the launch period.",
    level: "department",
    owner: "VP Engineering",
    parent_id: "g-launch",
    metric: "≤ 0 Sev1 / quarter",
    status: "active",
    source: "manual",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 45).toISOString(),
  },
  {
    id: "g-margin",
    title: "Improve gross margin to 75%",
    description: "Grow margin via pricing discipline and infra efficiency.",
    level: "board",
    owner: "CFO",
    parent_id: null,
    metric: "75% GM by FY-end",
    status: "active",
    source: "manual",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 90).toISOString(),
  },
];

// Synthesize a plausible record for the New Decision flow when no engine is configured,
// so the submit → detail experience works fully offline (demo mode only).
export function makeDemoDecision(req: Partial<DecisionRequest>): DecisionRecord {
  const stakes = (req.stakes as StakesTier) || "S3";
  const reviewRequired = stakes === "S1" || stakes === "S2";
  return {
    ...sampleDecision,
    id: `demo-${Math.random().toString(36).slice(2, 10)}`,
    stakes,
    review_required: reviewRequired,
    review_state: reviewRequired ? "pending" : "not_required",
    request: {
      decision_type: req.decision_type || "release_go_no_go",
      question: req.question || "(no question)",
      options: req.options || [],
      context: req.context || "",
      stakes: (req.stakes as StakesTier) ?? null,
      repo: req.repo ?? null,
      inputs: req.inputs || {},
    },
    created_at: new Date().toISOString(),
  };
}

