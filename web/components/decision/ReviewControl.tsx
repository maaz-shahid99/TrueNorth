"use client";

import { useRouter } from "next/navigation";
import * as React from "react";
import { ReviewPill } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Input";
import { formatDateTime } from "@/lib/format";
import type { ReviewAction, ReviewState } from "@/lib/types";

export function ReviewControl({
  decisionId,
  required,
  initialState,
  initialHistory = [],
}: {
  decisionId: string;
  required: boolean;
  initialState: ReviewState;
  initialHistory?: ReviewAction[];
}) {
  const router = useRouter();
  const [state, setState] = React.useState<ReviewState>(initialState);
  const [history, setHistory] = React.useState<ReviewAction[]>(initialHistory);
  const [note, setNote] = React.useState("");
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  async function act(action: "approve" | "reject") {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch(`/api/decisions/${decisionId}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, note }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail ?? "Failed to submit review.");
      setState(data.state as ReviewState);
      setHistory((data.history as ReviewAction[]) ?? history);
      setNote("");
      router.refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to submit review.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm text-muted">Status</span>
        <ReviewPill state={state} />
      </div>

      {!required && (
        <p className="text-xs text-muted">No sign-off is required at this stakes tier.</p>
      )}

      {required && state === "pending" && (
        <div className="space-y-2">
          <Textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="Optional note for the record"
            className="mt-0 min-h-[60px]"
          />
          <div className="flex gap-2">
            <Button size="sm" onClick={() => act("approve")} disabled={busy}>
              Approve
            </Button>
            <Button size="sm" variant="danger" onClick={() => act("reject")} disabled={busy}>
              Reject
            </Button>
          </div>
        </div>
      )}

      {error && <p className="text-sm text-verdict-oppose">{error}</p>}

      {history.length > 0 && (
        <ul className="space-y-2 border-t border-line pt-3">
          {history.map((h, i) => (
            <li key={i} className="text-xs text-muted">
              <span className="font-medium text-ink">{h.actor || "reviewer"}</span> {h.action}ed
              {h.note ? ` — “${h.note}”` : ""} · {formatDateTime(h.at)}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
