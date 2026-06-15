// Server-side data access for decisions. Calls the engine when a credential is configured;
// otherwise falls back to the bundled fixtures so the UI is fully reviewable offline.
import { engineConfigured, engineFetch } from "./engine";
import { mockDecisions, sampleDecision } from "./mock";
import type { DecisionRecord, Outcome } from "./types";

export async function getDecision(id: string): Promise<DecisionRecord | null> {
  if (!engineConfigured()) {
    const fromMock = mockDecisions.find((d) => d.id === id);
    return fromMock ?? { ...sampleDecision, id };
  }
  const res = await engineFetch(`/v1/decisions/${encodeURIComponent(id)}`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`Engine returned ${res.status} for decision ${id}`);
  return (await res.json()) as DecisionRecord;
}

export async function listDecisions(): Promise<DecisionRecord[]> {
  if (!engineConfigured()) return mockDecisions;
  const res = await engineFetch("/v1/decisions?limit=100");
  if (!res.ok) throw new Error(`Engine returned ${res.status} listing decisions`);
  return (await res.json()) as DecisionRecord[];
}

export async function getOutcomes(id: string): Promise<Outcome[]> {
  if (!engineConfigured()) return [];
  const res = await engineFetch(`/v1/decisions/${encodeURIComponent(id)}/outcomes`);
  if (!res.ok) return [];
  return (await res.json()) as Outcome[];
}
