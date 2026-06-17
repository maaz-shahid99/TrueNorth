// Server-side data access for decisions. Calls the engine when a credential is available
// (per-user SSO JWT or shared dev key); otherwise falls back to bundled fixtures so the UI
// is fully reviewable offline.
import { engineFetch, hasEngineCredential } from "./engine";
import { mockDecisions, mockKeys, sampleDecision } from "./mock";
import type { ApiKeyInfo, DecisionRecord, Outcome, ReviewStatus } from "./types";

export async function getDecision(id: string): Promise<DecisionRecord | null> {
  if (!(await hasEngineCredential())) {
    const fromMock = mockDecisions.find((d) => d.id === id);
    return fromMock ?? { ...sampleDecision, id };
  }
  const res = await engineFetch(`/v1/decisions/${encodeURIComponent(id)}`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Engine returned ${res.status} for decision ${id}`);
  return (await res.json()) as DecisionRecord;
}

// List decisions. Defaults to a large page so the dashboard/analytics/reviews/audit
// aggregations see the full set; the history page passes explicit limit/offset to paginate.
export async function listDecisions(
  opts: { limit?: number; offset?: number } = {},
): Promise<DecisionRecord[]> {
  const limit = opts.limit ?? 100;
  const offset = opts.offset ?? 0;
  if (!(await hasEngineCredential())) return mockDecisions.slice(offset, offset + limit);
  const res = await engineFetch(`/v1/decisions?limit=${limit}&offset=${offset}`);
  if (!res.ok) throw new Error(`Engine returned ${res.status} listing decisions`);
  return (await res.json()) as DecisionRecord[];
}

export async function getOutcomes(id: string): Promise<Outcome[]> {
  if (!(await hasEngineCredential())) return [];
  const res = await engineFetch(`/v1/decisions/${encodeURIComponent(id)}/outcomes`);
  if (!res.ok) return [];
  return (await res.json()) as Outcome[];
}

export async function getReview(d: DecisionRecord): Promise<ReviewStatus> {
  const fallback: ReviewStatus = {
    decision_id: d.id,
    required: d.review_required,
    state: d.review_state,
    history: [],
  };
  if (!(await hasEngineCredential())) return fallback;
  const res = await engineFetch(`/v1/decisions/${encodeURIComponent(d.id)}/review`);
  if (!res.ok) return fallback;
  return (await res.json()) as ReviewStatus;
}

export async function getKeys(): Promise<ApiKeyInfo[]> {
  if (!(await hasEngineCredential())) return mockKeys;
  const res = await engineFetch("/v1/keys");
  if (!res.ok) return []; // e.g. 403 for non-admins
  return (await res.json()) as ApiKeyInfo[];
}
