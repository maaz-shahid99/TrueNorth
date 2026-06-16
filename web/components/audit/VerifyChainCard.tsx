"use client";

import { RefreshCw, ShieldAlert, ShieldCheck } from "lucide-react";
import * as React from "react";
import { Button } from "@/components/ui/Button";
import { SectionCard } from "@/components/ui/Card";
import type { ChainVerification } from "@/lib/types";

export function VerifyChainCard() {
  const [result, setResult] = React.useState<ChainVerification | null>(null);
  const [busy, setBusy] = React.useState(false);

  const verify = React.useCallback(async () => {
    setBusy(true);
    try {
      const res = await fetch("/api/audit/verify");
      setResult((await res.json()) as ChainVerification);
    } catch {
      setResult(null);
    } finally {
      setBusy(false);
    }
  }, []);

  React.useEffect(() => {
    verify();
  }, [verify]);

  const ok = result?.ok;

  return (
    <SectionCard
      title="Ledger integrity"
      action={
        <Button size="sm" variant="secondary" onClick={verify} disabled={busy}>
          <RefreshCw className="h-4 w-4" />
          {busy ? "Verifying…" : "Re-verify"}
        </Button>
      }
    >
      {!result ? (
        <p className="text-sm text-muted">Verifying…</p>
      ) : (
        <div className="flex items-start gap-3">
          {ok ? (
            <ShieldCheck className="h-6 w-6 shrink-0 text-verdict-endorse" />
          ) : (
            <ShieldAlert className="h-6 w-6 shrink-0 text-verdict-oppose" />
          )}
          <div>
            <p
              className={
                ok
                  ? "text-sm font-medium text-verdict-endorse"
                  : "text-sm font-medium text-verdict-oppose"
              }
            >
              {ok ? "Chain intact" : "Chain broken"}
            </p>
            <p className="text-sm text-muted">
              {result.entries_checked} entries checked
              {result.broken_at_seq != null ? ` · broken at #${result.broken_at_seq}` : ""}
            </p>
            <p className="mt-1 text-xs text-muted">{result.detail}</p>
          </div>
        </div>
      )}
    </SectionCard>
  );
}
