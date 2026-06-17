"use client";

import * as React from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Dialog } from "@/components/ui/Dialog";
import { Field, Input, Select, Textarea } from "@/components/ui/Input";
import { EmptyState } from "@/components/ui/EmptyState";
import { Table, Td, Th, Thead, Tr } from "@/components/ui/Table";
import type { Goal, GoalLevel } from "@/lib/types";

const LEVELS: GoalLevel[] = ["board", "department", "team"];

const levelClass: Record<GoalLevel, string> = {
  board: "bg-brand-50 text-brand-700",
  department: "bg-pastel-blue text-ink",
  team: "bg-line text-muted",
};

export function GoalsManager({ initialGoals }: { initialGoals: Goal[] }) {
  const [goals, setGoals] = React.useState<Goal[]>(initialGoals);
  const [open, setOpen] = React.useState(false);
  const [title, setTitle] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [level, setLevel] = React.useState<GoalLevel>("department");
  const [owner, setOwner] = React.useState("");
  const [metric, setMetric] = React.useState("");
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  function reset() {
    setTitle("");
    setDescription("");
    setLevel("department");
    setOwner("");
    setMetric("");
  }

  async function create() {
    setBusy(true);
    setError(null);
    try {
      const res = await fetch("/api/goals", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title, description, level, owner, metric }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail ?? "Failed to create goal.");
      setGoals((prev) => [data as Goal, ...prev]);
      reset();
      setOpen(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create goal.");
    } finally {
      setBusy(false);
    }
  }

  async function archive(id: string) {
    const res = await fetch(`/api/goals/${id}`, { method: "DELETE" });
    if (res.ok) setGoals((prev) => prev.filter((g) => g.id !== id));
  }

  return (
    <Card>
      <div className="flex items-center justify-between border-b border-line p-4">
        <h3 className="text-sm font-semibold">Active goals</h3>
        <Button size="sm" onClick={() => setOpen(true)}>
          Add goal
        </Button>
      </div>

      {goals.length === 0 ? (
        <div className="p-6">
          <EmptyState title="No goals yet" description="Add the OKRs decisions should be judged against." />
        </div>
      ) : (
        <Table>
          <Thead>
            <tr className="border-b border-line">
              <Th className="pl-5">Goal</Th>
              <Th>Level</Th>
              <Th>Owner</Th>
              <Th>Metric</Th>
              <Th className="pr-5" />
            </tr>
          </Thead>
          <tbody>
            {goals.map((g) => (
              <Tr key={g.id}>
                <Td className="pl-5">
                  <p className="font-medium text-ink">{g.title}</p>
                  {g.description && <p className="text-xs text-muted">{g.description}</p>}
                </Td>
                <Td>
                  <Badge className={levelClass[g.level]}>{g.level}</Badge>
                </Td>
                <Td className="text-muted">{g.owner || "—"}</Td>
                <Td className="text-muted">{g.metric || "—"}</Td>
                <Td className="pr-5 text-right">
                  <Button size="sm" variant="ghost" onClick={() => archive(g.id)}>
                    Archive
                  </Button>
                </Td>
              </Tr>
            ))}
          </tbody>
        </Table>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} title="Add goal">
        <div className="space-y-3">
          <Field label="Title">
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Grow ARR 30% this fiscal year"
            />
          </Field>
          <Field label="Description (optional)">
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="What this goal means and why it matters."
            />
          </Field>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <Field label="Level">
              <Select value={level} onChange={(e) => setLevel(e.target.value as GoalLevel)}>
                {LEVELS.map((l) => (
                  <option key={l} value={l}>
                    {l}
                  </option>
                ))}
              </Select>
            </Field>
            <Field label="Owner (optional)">
              <Input value={owner} onChange={(e) => setOwner(e.target.value)} placeholder="CFO" />
            </Field>
          </div>
          <Field label="Metric (optional)">
            <Input
              value={metric}
              onChange={(e) => setMetric(e.target.value)}
              placeholder="ARR ≥ $30M by FY-end"
            />
          </Field>
          {error && <p className="text-sm text-verdict-oppose">{error}</p>}
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button onClick={create} disabled={busy || !title.trim()}>
              {busy ? "Adding…" : "Add goal"}
            </Button>
          </div>
        </div>
      </Dialog>
    </Card>
  );
}
