"use client";

import * as React from "react";
import { Button } from "@/components/ui/Button";
import { SectionCard } from "@/components/ui/Card";
import { Dialog } from "@/components/ui/Dialog";
import { Field, Select, Textarea } from "@/components/ui/Input";
import { formatDateTime } from "@/lib/format";
import type { Outcome } from "@/lib/types";

export function OutcomePanel({
  decisionId,
  initialOutcomes,
}: {
  decisionId: string;
  initialOutcomes: Outcome[];
}) {
  const [outcomes, setOutcomes] = React.useState<Outcome[]>(initialOutcomes);
  const [open, setOpen] = React.useState(false);
  const [realized, setRealized] = React.useState("");
  const [success, setSuccess] = React.useState("unknown");
  const [notes, setNotes] = React.useState("");
  const [saving, setSaving] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  async function save() {
    setSaving(true);
    setError(null);
    try {
      const body = {
        realized,
        success: success === "unknown" ? null : success === "yes",
        metrics: {},
        notes,
        recorded_by: "",
      };
      const res = await fetch(`/api/decisions/${decisionId}/outcomes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail ?? "Failed to record outcome.");
      setOutcomes((prev) => [...prev, data as Outcome]);
      setOpen(false);
      setRealized("");
      setNotes("");
      setSuccess("unknown");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to record outcome.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <SectionCard
      title="Outcomes"
      action={
        <Button size="sm" variant="secondary" onClick={() => setOpen(true)}>
          Record
        </Button>
      }
    >
      {outcomes.length === 0 ? (
        <p className="text-sm text-muted">No outcome recorded yet.</p>
      ) : (
        <ul className="space-y-3">
          {outcomes.map((o, i) => (
            <li key={i} className="rounded-lg border border-line p-3">
              <div className="flex items-start justify-between gap-3">
                <span className="text-sm text-ink">{o.realized}</span>
                {o.success !== null && (
                  <span
                    className={
                      o.success
                        ? "shrink-0 text-xs font-medium text-verdict-endorse"
                        : "shrink-0 text-xs font-medium text-verdict-oppose"
                    }
                  >
                    {o.success ? "Success" : "Miss"}
                  </span>
                )}
              </div>
              {o.notes && <p className="mt-1 text-xs text-muted">{o.notes}</p>}
              <p className="mt-1 text-xs text-muted">{formatDateTime(o.recorded_at)}</p>
            </li>
          ))}
        </ul>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} title="Record outcome">
        <div className="space-y-3">
          <Field label="What actually happened?">
            <Textarea
              value={realized}
              onChange={(e) => setRealized(e.target.value)}
              placeholder="Shipped behind a flag; no incidents during the keynote."
            />
          </Field>
          <Field label="Did it match the recommendation?">
            <Select value={success} onChange={(e) => setSuccess(e.target.value)}>
              <option value="unknown">Unknown</option>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </Select>
          </Field>
          <Field label="Notes (optional)">
            <Textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
          </Field>
          {error && <p className="text-sm text-verdict-oppose">{error}</p>}
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={save} disabled={saving || !realized.trim()}>
              {saving ? "Saving…" : "Save outcome"}
            </Button>
          </div>
        </div>
      </Dialog>
    </SectionCard>
  );
}
