"use client";

import { useRouter } from "next/navigation";
import * as React from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field, Input, Select, Textarea } from "@/components/ui/Input";
import { Stepper } from "@/components/ui/Stepper";
import { cn } from "@/lib/utils";

type DType = "release_go_no_go" | "discount_approval";

const typeInfo: Record<DType, { label: string; blurb: string }> = {
  release_go_no_go: {
    label: "Release go/no-go",
    blurb: "Judge ship-readiness from GitHub signals (open bugs, CI, PRs).",
  },
  discount_approval: {
    label: "Discount approval",
    blurb: "Judge a pricing discount from the deal facts you supply.",
  },
};

const discountFields: { key: string; label: string; placeholder: string }[] = [
  { key: "discount_pct", label: "Requested discount (%)", placeholder: "35" },
  { key: "gross_margin_pct", label: "Resulting gross margin (%)", placeholder: "12" },
  { key: "deal_value", label: "Deal value (USD)", placeholder: "500000" },
  { key: "customer_tier", label: "Customer tier", placeholder: "mid-market, non-strategic" },
  { key: "competitor", label: "Competitive pressure", placeholder: "incumbent renewal" },
  { key: "contract_term_months", label: "Contract term (months)", placeholder: "12" },
  { key: "approver_limit_pct", label: "Self-approve limit (%)", placeholder: "15" },
];

const steps = ["Type", "Details", "Review"];

export function NewDecisionForm() {
  const router = useRouter();
  const [step, setStep] = React.useState(0);
  const [type, setType] = React.useState<DType>("release_go_no_go");
  const [question, setQuestion] = React.useState("");
  const [context, setContext] = React.useState("");
  const [stakes, setStakes] = React.useState("");
  const [repo, setRepo] = React.useState("");
  const [inputs, setInputs] = React.useState<Record<string, string>>({});
  const [submitting, setSubmitting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  async function submit() {
    setSubmitting(true);
    setError(null);
    try {
      const body = {
        decision_type: type,
        question,
        context,
        stakes: stakes || null,
        repo: type === "release_go_no_go" ? repo || null : null,
        inputs:
          type === "discount_approval"
            ? Object.fromEntries(Object.entries(inputs).filter(([, v]) => v.trim()))
            : {},
        options: [],
      };
      const res = await fetch("/api/decisions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.detail ?? "Failed to submit decision.");
      router.push(`/decisions/${data.id}`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to submit decision.");
      setSubmitting(false);
    }
  }

  return (
    <Card className="p-6">
      <Stepper steps={steps} current={step} />
      <div className="mt-6">
        {step === 0 && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {(Object.keys(typeInfo) as DType[]).map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setType(t)}
                className={cn(
                  "rounded-xl border p-4 text-left transition-colors",
                  type === t ? "border-brand-500 bg-brand-50" : "border-line bg-surface hover:bg-app",
                )}
              >
                <p className="font-medium text-ink">{typeInfo[t].label}</p>
                <p className="mt-1 text-sm text-muted">{typeInfo[t].blurb}</p>
              </button>
            ))}
          </div>
        )}

        {step === 1 && (
          <div className="space-y-4">
            <Field label="Decision">
              <Textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Should we ship release 2.4 tonight ahead of the launch event?"
              />
            </Field>
            <Field label="Context (optional)">
              <Textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                placeholder="Any background the judges should weigh."
              />
            </Field>
            <Field label="Stakes (optional — the engine classifies if left on auto)">
              <Select value={stakes} onChange={(e) => setStakes(e.target.value)}>
                <option value="">Auto-classify</option>
                <option value="S1">S1 · Existential</option>
                <option value="S2">S2 · Executive</option>
                <option value="S3">S3 · Departmental</option>
                <option value="S4">S4 · Routine</option>
              </Select>
            </Field>

            {type === "release_go_no_go" ? (
              <Field label="GitHub repository (optional)" hint="owner/name — supplies release evidence.">
                <Input value={repo} onChange={(e) => setRepo(e.target.value)} placeholder="acme/app" />
              </Field>
            ) : (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                {discountFields.map((f) => (
                  <Field key={f.key} label={f.label}>
                    <Input
                      value={inputs[f.key] ?? ""}
                      onChange={(e) => setInputs((prev) => ({ ...prev, [f.key]: e.target.value }))}
                      placeholder={f.placeholder}
                    />
                  </Field>
                ))}
              </div>
            )}
          </div>
        )}

        {step === 2 && (
          <dl className="space-y-2.5 text-sm">
            <ReviewRow k="Type" v={typeInfo[type].label} />
            <ReviewRow k="Decision" v={question || "—"} />
            <ReviewRow k="Stakes" v={stakes || "Auto-classify"} />
            {type === "release_go_no_go" && <ReviewRow k="Repository" v={repo || "—"} />}
            {type === "discount_approval" &&
              discountFields
                .filter((f) => inputs[f.key]?.trim())
                .map((f) => <ReviewRow key={f.key} k={f.label} v={inputs[f.key]} />)}
            {error && <p className="pt-2 text-sm text-verdict-oppose">{error}</p>}
          </dl>
        )}
      </div>

      <div className="mt-6 flex items-center justify-between">
        <Button
          variant="secondary"
          onClick={() => setStep((s) => Math.max(0, s - 1))}
          disabled={step === 0 || submitting}
        >
          Back
        </Button>
        {step < 2 ? (
          <Button onClick={() => setStep((s) => s + 1)} disabled={step === 1 && !question.trim()}>
            Continue
          </Button>
        ) : (
          <Button onClick={submit} disabled={submitting || !question.trim()}>
            {submitting ? "Judging…" : "Submit for judgment"}
          </Button>
        )}
      </div>
    </Card>
  );
}

function ReviewRow({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex items-start justify-between gap-4 border-b border-line pb-2 last:border-0">
      <dt className="text-muted">{k}</dt>
      <dd className="max-w-md text-right font-medium text-ink">{v}</dd>
    </div>
  );
}
