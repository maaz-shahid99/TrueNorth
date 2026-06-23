"use client";

import * as React from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Dialog } from "@/components/ui/Dialog";
import { EmptyState } from "@/components/ui/EmptyState";
import { Field, Input, Select, Textarea } from "@/components/ui/Input";
import { Table, Td, Th, Thead, Tr } from "@/components/ui/Table";
import type { Policy, PolicyCondition, StakesTier } from "@/lib/types";

function summarize(c: PolicyCondition): string {
  const parts: string[] = [];
  if (c.decision_types.length) parts.push(`type: ${c.decision_types.join("/")}`);
  if (c.min_stakes) parts.push(`stakes ≥ ${c.min_stakes}`);
  if (c.verdicts.length) parts.push(`verdict: ${c.verdicts.join("/")}`);
  if (c.on_alignment_conflict) parts.push("goal conflict");
  if (c.min_cost_usd != null) parts.push(`spend ≥ $${c.min_cost_usd}`);
  return parts.join(" · ") || "always";
}

export function PoliciesManager({ initialPolicies }: { initialPolicies: Policy[] }) {
  const [policies, setPolicies] = React.useState<Policy[]>(initialPolicies);
  const [open, setOpen] = React.useState(false);
  const [name, setName] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [effect, setEffect] = React.useState<"require_review" | "flag">("require_review");
  const [requiredRole, setRequiredRole] = React.useState<"reviewer" | "admin">("reviewer");
  const [minStakes, setMinStakes] = React.useState<"" | StakesTier>("");
  const [onConflict, setOnConflict] = React.useState(false);
  const [minCost, setMinCost] = React.useState("");
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  function reset() {
    setName("");
    setDescription("");
    setEffect("require_review");
    setRequiredRole("reviewer");
    setMinStakes("");
    setOnConflict(false);
    setMinCost("");
  }

  async function create() {
    setBusy(true);
    setError(null);
    try {
      const condition: PolicyCondition = {
        decision_types: [],
        min_stakes: minStakes || null,
        verdicts: [],
        on_alignment_conflict: onConflict,
        min_cost_usd: minCost.trim() ? Number(minCost) : null,
      };
      const res = await fetch("/api/policies", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description, effect, required_role: requiredRole, condition }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail ?? "Failed to create policy.");
      setPolicies((prev) => [data as Policy, ...prev]);
      reset();
      setOpen(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create policy.");
    } finally {
      setBusy(false);
    }
  }

  async function archive(id: string) {
    const res = await fetch(`/api/policies/${id}`, { method: "DELETE" });
    if (res.ok) setPolicies((prev) => prev.filter((p) => p.id !== id));
  }

  return (
    <Card>
      <div className="flex items-center justify-between border-b border-line p-4">
        <h3 className="text-sm font-semibold">Decision-rights policies</h3>
        <Button size="sm" onClick={() => setOpen(true)}>
          Add policy
        </Button>
      </div>

      {policies.length === 0 ? (
        <div className="p-6">
          <EmptyState
            title="No policies yet"
            description="Add rules that require sign-off or flag decisions beyond the stakes default."
          />
        </div>
      ) : (
        <Table>
          <Thead>
            <tr className="border-b border-line">
              <Th className="pl-5">Policy</Th>
              <Th>When</Th>
              <Th>Effect</Th>
              <Th className="pr-5" />
            </tr>
          </Thead>
          <tbody>
            {policies.map((p) => (
              <Tr key={p.id}>
                <Td className="pl-5">
                  <p className="font-medium text-ink">{p.name}</p>
                  {p.description && <p className="text-xs text-muted">{p.description}</p>}
                </Td>
                <Td className="text-muted">{summarize(p.condition)}</Td>
                <Td>
                  {p.effect === "require_review" ? (
                    <Badge className="bg-verdict-caution-bg text-verdict-caution">
                      require {p.required_role}
                    </Badge>
                  ) : (
                    <Badge className="bg-line text-muted">flag</Badge>
                  )}
                </Td>
                <Td className="pr-5 text-right">
                  <Button size="sm" variant="ghost" onClick={() => archive(p.id)}>
                    Archive
                  </Button>
                </Td>
              </Tr>
            ))}
          </tbody>
        </Table>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} title="Add policy">
        <div className="space-y-3">
          <Field label="Name">
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Executive sign-off on S2+" />
          </Field>
          <Field label="Description (optional)">
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Why this rule exists."
            />
          </Field>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Field label="Effect">
              <Select value={effect} onChange={(e) => setEffect(e.target.value as typeof effect)}>
                <option value="require_review">Require review</option>
                <option value="flag">Flag only</option>
              </Select>
            </Field>
            <Field label="Required role">
              <Select
                value={requiredRole}
                onChange={(e) => setRequiredRole(e.target.value as typeof requiredRole)}
              >
                <option value="reviewer">reviewer</option>
                <option value="admin">admin</option>
              </Select>
            </Field>
          </div>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Field label="Min stakes (optional)" hint="Fires at or above this tier.">
              <Select value={minStakes} onChange={(e) => setMinStakes(e.target.value as "" | StakesTier)}>
                <option value="">Any</option>
                <option value="S1">S1 · Existential</option>
                <option value="S2">S2 · Executive</option>
                <option value="S3">S3 · Departmental</option>
                <option value="S4">S4 · Routine</option>
              </Select>
            </Field>
            <Field label="Min model spend USD (optional)">
              <Input value={minCost} onChange={(e) => setMinCost(e.target.value)} placeholder="1.00" />
            </Field>
          </div>
          <label className="flex items-center gap-2 text-sm text-muted">
            <input
              type="checkbox"
              checked={onConflict}
              onChange={(e) => setOnConflict(e.target.checked)}
            />
            Only when the decision conflicts with a goal
          </label>
          {error && <p className="text-sm text-verdict-oppose">{error}</p>}
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={create} disabled={busy || !name.trim()}>
              {busy ? "Adding…" : "Add policy"}
            </Button>
          </div>
        </div>
      </Dialog>
    </Card>
  );
}
