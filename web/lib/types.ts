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

export const VERDICTS: Verdict[] = [
  "Endorse",
  "Endorse-with-conditions",
  "Caution",
  "Oppose",
];
