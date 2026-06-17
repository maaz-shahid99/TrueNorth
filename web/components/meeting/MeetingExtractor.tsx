"use client";

import { useRouter } from "next/navigation";
import * as React from "react";
import { Button } from "@/components/ui/Button";
import { Card, SectionCard } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Field, Input, Select, Textarea } from "@/components/ui/Input";
import type { ExtractedDecision, MeetingExtraction } from "@/lib/types";
import { decisionTypeLabel } from "@/lib/verdict";

const TYPES = [
  "release_go_no_go",
  "discount_approval",
  "hiring_approval",
  "vendor_procurement",
  "budget_spend",
  "project_go_no_go",
  "other",
];

export function MeetingExtractor() {
  const [title, setTitle] = React.useState("");
  const [transcript, setTranscript] = React.useState("");
  const [consent, setConsent] = React.useState(false);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [result, setResult] = React.useState<MeetingExtraction | null>(null);

  async function extract() {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/meetings/extract", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript, title }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail ?? "Extraction failed.");
      setResult(data as MeetingExtraction);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Extraction failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="space-y-4">
          <Field label="Meeting title (optional)">
            <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Release sync — Apr 12" />
          </Field>
          <Field label="Transcript" hint="Paste the meeting transcript or notes.">
            <Textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              rows={10}
              placeholder="Dana: I think we should ship 2.4 tonight…"
            />
          </Field>
          <label className="flex items-start gap-2 text-sm text-muted">
            <input
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
              className="mt-0.5"
            />
            I confirm participants consented to this transcript being processed (MI-6).
          </label>
          {error && <p className="text-sm text-verdict-oppose">{error}</p>}
          <div className="flex justify-end">
            <Button onClick={extract} disabled={busy || !transcript.trim() || !consent}>
              {busy ? "Reading…" : "Extract decisions"}
            </Button>
          </div>
        </div>
      </Card>

      {result && (
        <div className="space-y-4">
          {result.summary && (
            <SectionCard title="Meeting summary">
              <p className="text-sm text-ink">{result.summary}</p>
            </SectionCard>
          )}
          {result.decisions.length === 0 ? (
            <EmptyState
              title="No decisions found"
              description="The transcript didn't contain a clear decision to judge."
            />
          ) : (
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-ink">
                Candidate decisions ({result.decisions.length}) — review, then send to judgment
              </h3>
              {result.decisions.map((d, i) => (
                <CandidateCard key={i} candidate={d} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function CandidateCard({ candidate }: { candidate: ExtractedDecision }) {
  const router = useRouter();
  const [question, setQuestion] = React.useState(candidate.question);
  const [type, setType] = React.useState(
    TYPES.includes(candidate.decision_type) ? candidate.decision_type : "other",
  );
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  async function judge() {
    setBusy(true);
    setError(null);
    try {
      const context = [candidate.context, candidate.dissent && `Recorded dissent: ${candidate.dissent}`]
        .filter(Boolean)
        .join("\n");
      const res = await fetch("/api/decisions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision_type: type,
          question,
          context,
          stakes: null,
          repo: null,
          inputs: {},
          options: [],
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail ?? "Failed to submit decision.");
      router.push(`/decisions/${data.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to submit decision.");
      setBusy(false);
    }
  }

  return (
    <Card className="p-4">
      <div className="space-y-3">
        <Field label="Decision">
          <Input value={question} onChange={(e) => setQuestion(e.target.value)} />
        </Field>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <Field label="Type">
            <Select value={type} onChange={(e) => setType(e.target.value)}>
              {TYPES.map((t) => (
                <option key={t} value={t}>
                  {decisionTypeLabel[t] ?? t}
                </option>
              ))}
            </Select>
          </Field>
          <div className="flex flex-wrap items-end gap-x-4 gap-y-1 text-xs text-muted">
            {candidate.owner && <span>Owner: {candidate.owner}</span>}
            {candidate.deadline && <span>Deadline: {candidate.deadline}</span>}
          </div>
        </div>
        {candidate.dissent && (
          <p className="text-xs text-verdict-caution">Recorded dissent: {candidate.dissent}</p>
        )}
        {error && <p className="text-sm text-verdict-oppose">{error}</p>}
        <div className="flex justify-end">
          <Button size="sm" onClick={judge} disabled={busy || !question.trim()}>
            {busy ? "Judging…" : "Send to judgment"}
          </Button>
        </div>
      </div>
    </Card>
  );
}
