"use client";

import * as React from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Dialog } from "@/components/ui/Dialog";
import { Field, Input } from "@/components/ui/Input";
import { Table, Td, Th, Thead, Tr } from "@/components/ui/Table";
import { formatDate } from "@/lib/format";
import type { ApiKeyInfo } from "@/lib/types";

const ALL_ROLES = ["viewer", "requester", "reviewer", "admin"] as const;

export function KeysManager({ initialKeys }: { initialKeys: ApiKeyInfo[] }) {
  const [keys, setKeys] = React.useState<ApiKeyInfo[]>(initialKeys);
  const [open, setOpen] = React.useState(false);
  const [subject, setSubject] = React.useState("");
  const [roles, setRoles] = React.useState<string[]>(["requester"]);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [newKey, setNewKey] = React.useState<string | null>(null);

  function toggleRole(r: string) {
    setRoles((prev) => (prev.includes(r) ? prev.filter((x) => x !== r) : [...prev, r]));
  }

  async function mint() {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/keys", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ subject, roles }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail ?? "Failed to mint key.");
      setKeys((prev) => [data.info as ApiKeyInfo, ...prev]);
      setNewKey(data.key as string);
      setSubject("");
      setRoles(["requester"]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to mint key.");
    } finally {
      setBusy(false);
    }
  }

  async function revoke(id: string) {
    const res = await fetch(`/api/keys/${id}`, { method: "DELETE" });
    if (res.ok) {
      setKeys((prev) => prev.map((k) => (k.id === id ? { ...k, active: false } : k)));
    }
  }

  return (
    <Card>
      <div className="flex items-center justify-between border-b border-line p-4">
        <h3 className="text-sm font-semibold">API keys</h3>
        <Button size="sm" onClick={() => setOpen(true)}>
          Mint key
        </Button>
      </div>

      {newKey && (
        <div className="m-4 rounded-lg border border-brand-200 bg-brand-50 p-3">
          <p className="text-xs font-medium text-brand-700">
            New key — copy it now, it won&apos;t be shown again:
          </p>
          <code className="mt-1 block break-all text-sm text-ink">{newKey}</code>
          <button
            onClick={() => setNewKey(null)}
            className="mt-2 text-xs text-muted hover:text-ink"
          >
            Dismiss
          </button>
        </div>
      )}

      <Table>
        <Thead>
          <tr className="border-b border-line">
            <Th className="pl-5">Subject</Th>
            <Th>Roles</Th>
            <Th>Status</Th>
            <Th>Created</Th>
            <Th className="pr-5" />
          </tr>
        </Thead>
        <tbody>
          {keys.map((k) => (
            <Tr key={k.id}>
              <Td className="pl-5 font-medium text-ink">{k.subject}</Td>
              <Td className="text-muted">{k.roles.join(", ")}</Td>
              <Td>
                {k.active ? (
                  <Badge className="bg-verdict-endorse-bg text-verdict-endorse">active</Badge>
                ) : (
                  <Badge className="bg-line text-muted">revoked</Badge>
                )}
              </Td>
              <Td className="whitespace-nowrap text-muted">{formatDate(k.created_at)}</Td>
              <Td className="pr-5 text-right">
                {k.active && (
                  <Button size="sm" variant="ghost" onClick={() => revoke(k.id)}>
                    Revoke
                  </Button>
                )}
              </Td>
            </Tr>
          ))}
        </tbody>
      </Table>

      <Dialog open={open} onClose={() => setOpen(false)} title="Mint API key">
        <div className="space-y-3">
          <Field label="Subject" hint="A user or service identifier.">
            <Input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="svc@acme" />
          </Field>
          <div>
            <span className="text-xs font-medium text-muted">Roles</span>
            <div className="mt-1 flex flex-wrap gap-2">
              {ALL_ROLES.map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => toggleRole(r)}
                  className={
                    roles.includes(r)
                      ? "rounded-full border border-brand-500 bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700"
                      : "rounded-full border border-line bg-surface px-3 py-1 text-xs text-muted hover:bg-app"
                  }
                >
                  {r}
                </button>
              ))}
            </div>
          </div>
          {error && <p className="text-sm text-verdict-oppose">{error}</p>}
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={mint} disabled={busy || !subject.trim() || roles.length === 0}>
              {busy ? "Minting…" : "Mint key"}
            </Button>
          </div>
        </div>
      </Dialog>
    </Card>
  );
}
