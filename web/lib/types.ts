// Mirrors the engine's Pydantic schemas (snake_case JSON as returned by the API).

export type Verdict =
  | "Endorse"
  | "Endorse-with-conditions"
  | "Caution"
  | "Oppose";

export type StakesTier = "S1" | "S2" | "S3" | "S4";

export type ReviewState = "not_required" | "pending" | "approved" | "rejected";

export type LensName =
  | "financial"
  | "strategic"
  | "risk"
  | "legal"
  | "people"
  | "customer"
  | "esg";

export interface DecisionRequest {
  decision_type: string;
  question: string;
  options: string[];
  context: string;
  stakes: StakesTier | null;
  repo: string | null;
  inputs: Record<string, string>;
}

export interface EvidenceItem {
  claim: string;
  value: string;
  source: string;
}

export interface EvidencePack {
  items: EvidenceItem[];
  sufficiency: string; // strong | adequate | thin | unavailable
  notes: string;
}

export interface LensAssessment {
  leaning: Verdict;
  rationale: string;
  key_risks: string[];
  cited_evidence: string[];
  confidence: number; // 0..1
  applicable: boolean;
}

export interface ScoredLens {
  lens: LensName;
  assessment: LensAssessment;
}

export interface DevilsAdvocate {
  counter_case: string;
  failure_conditions: string[];
  bias_flags: string[];
}

export interface Condition {
  text: string;
  owner: string;
  checkpoint: string;
}

export interface Recommendation {
  verdict: Verdict;
  reasoning: string;
  confidence: number; // 0..1
  conditions: Condition[];
  minority_report: string;
}

export interface CallUsage {
  step: string;
  model: string;
  input_tokens: number;
  output_tokens: number;
  cache_read_tokens: number;
  cache_write_tokens: number;
  latency_ms: number;
  cost_usd: number;
}

export interface UsageSummary {
  calls: CallUsage[];
  total_input_tokens: number;
  total_output_tokens: number;
  total_cost_usd: number;
  total_latency_ms: number;
}

export interface Precedent {
  decision_id: string;
  question: string;
  decision_type: string;
  verdict: Verdict;
  stakes: StakesTier;
  created_at: string;
  similarity: number; // 0..1
  outcome_summary: string;
}

export type GoalLevel = "board" | "department" | "team";

export interface Goal {
  id: string;
  title: string;
  description: string;
  level: GoalLevel;
  owner: string;
  parent_id: string | null;
  metric: string;
  status: "active" | "archived";
  source: string;
  created_at: string;
}

export interface GoalLink {
  goal_id: string;
  title: string;
  relation: "advances" | "conflicts" | "neutral";
  note: string;
}

export interface GoalAlignment {
  score: number; // 0..1
  rationale: string;
  advances: GoalLink[];
  conflicts: GoalLink[];
}

export interface ExtractedDecision {
  question: string;
  decision_type: string;
  owner: string;
  deadline: string;
  context: string;
  dissent: string;
}

export interface MeetingExtraction {
  summary: string;
  decisions: ExtractedDecision[];
}

export interface PolicyCondition {
  decision_types: string[];
  min_stakes: StakesTier | null;
  verdicts: Verdict[];
  on_alignment_conflict: boolean;
  min_cost_usd: number | null;
}

export interface Policy {
  id: string;
  name: string;
  description: string;
  condition: PolicyCondition;
  effect: "require_review" | "flag";
  required_role: "reviewer" | "admin";
  status: "active" | "archived";
  created_at: string;
}

export interface PolicyFlag {
  policy_id: string;
  name: string;
  effect: "require_review" | "flag";
  required_role: string;
  reason: string;
}

export interface Scenario {
  name: string;
  probability: number; // 0..1
  projection: string;
  drivers: string[];
}

export interface ScenarioForecast {
  summary: string;
  scenarios: Scenario[];
}

export interface DecisionRecord {
  id: string;
  request: DecisionRequest;
  stakes: StakesTier;
  model_used: string;
  evidence: EvidencePack;
  lenses: ScoredLens[];
  devils_advocate: DevilsAdvocate;
  recommendation: Recommendation;
  review_required: boolean;
  review_state: ReviewState;
  precedents?: Precedent[];
  alignment?: GoalAlignment | null;
  forecast?: ScenarioForecast | null;
  policy_flags?: PolicyFlag[];
  safety_flags?: string[];
  usage: UsageSummary;
  created_at: string;
  engine_version: string;
}

export interface Outcome {
  decision_id: string;
  realized: string;
  success: boolean | null;
  metrics: Record<string, string>;
  notes: string;
  recorded_by: string;
  recorded_at: string;
}

export interface ReviewAction {
  decision_id: string;
  actor: string;
  action: "approve" | "reject";
  note: string;
  at: string;
}

export interface ReviewStatus {
  decision_id: string;
  required: boolean;
  state: ReviewState;
  history: ReviewAction[];
}

export interface ChainVerification {
  ok: boolean;
  entries_checked: number;
  broken_at_seq: number | null;
  detail: string;
}

export interface ApiKeyInfo {
  id: string;
  tenant_id: string;
  subject: string;
  roles: string[];
  active: boolean;
  created_at: string;
}

export interface VerdictOutcomeStat {
  verdict: Verdict;
  decisions: number;
  with_outcomes: number;
  success_rate: number | null;
}

export interface ConfidenceBucket {
  label: string;
  n: number;
  predicted_confidence: number;
  realized_success_rate: number;
}

export interface CalibrationReport {
  total_decisions: number;
  decisions_with_outcomes: number;
  outcome_coverage: number;
  scored_outcomes: number;
  brier_score: number | null;
  by_verdict: VerdictOutcomeStat[];
  confidence_buckets: ConfidenceBucket[];
}

export interface ValueByType {
  decision_type: string;
  decisions: number;
  spend_usd: number;
}

export interface ValueReport {
  decisions: number;
  decisions_with_outcomes: number;
  model_spend_usd: number;
  realized_value_usd: number;
  net_value_usd: number;
  roi: number | null;
  median_days_to_outcome: number | null;
  by_type: ValueByType[];
}

export const VERDICTS: Verdict[] = [
  "Endorse",
  "Endorse-with-conditions",
  "Caution",
  "Oppose",
];
