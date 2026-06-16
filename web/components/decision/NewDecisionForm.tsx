"use client";

import { useRouter } from "next/navigation";
import * as React from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Field, Input, Select, Textarea } from "@/components/ui/Input";
import { Stepper } from "@/components/ui/Stepper";
import { cn } from "@/lib/utils";

type DType =
  | "release_go_no_go"
  | "discount_approval"
  | "hiring_approval"
  | "vendor_procurement"
  | "budget_spend"
  | "project_go_no_go";

type FactField = { key: string; label: string; placeholder: string };

const typeInfo: Record<DType, { label: string; blurb: string }> = {
  release_go_no_go: {
    label: "Release go/no-go",
    blurb: "Judge ship-readiness from GitHub signals (open bugs, CI, PRs).",
  },
  discount_approval: {
    label: "Discount approval",
    blurb: "Judge a pricing discount from the deal facts you supply.",
  },
  hiring_approval: {
    label: "Hiring approval",
    blurb: "Judge a proposed hire against headcount plan, comp, and team load.",
  },
  vendor_procurement: {
    label: "Vendor / procurement",
    blurb: "Judge a vendor contract on cost, risk, and security exposure.",
  },
  budget_spend: {
    label: "Budget / spend",
    blurb: "Judge a spend request against the budget line and expected return.",
  },
  project_go_no_go: {
    label: "Project go/no-go",
    blurb: "Judge whether to greenlight a project — live Jira signals or a brief you supply.",
  },
};

// Per-type fact fields. Keys must match the engine connectors' recognised inputs.
const fieldsByType: Record<DType, FactField[]> = {
  release_go_no_go: [], // uses the GitHub repo field instead
  discount_approval: [
    { key: "discount_pct", label: "Requested discount (%)", placeholder: "35" },
    { key: "gross_margin_pct", label: "Resulting gross margin (%)", placeholder: "12" },
    { key: "deal_value", label: "Deal value (USD)", placeholder: "500000" },
    { key: "customer_tier", label: "Customer tier", placeholder: "mid-market, non-strategic" },
    { key: "competitor", label: "Competitive pressure", placeholder: "incumbent renewal" },
    { key: "contract_term_months", label: "Contract term (months)", placeholder: "12" },
    { key: "approver_limit_pct", label: "Self-approve limit (%)", placeholder: "15" },
  ],
  hiring_approval: [
    { key: "role", label: "Role / title", placeholder: "Staff Engineer" },
    { key: "level", label: "Level / seniority", placeholder: "L6" },
    { key: "base_salary_usd", label: "Proposed base salary (USD)", placeholder: "210000" },
    { key: "headcount_plan", label: "In headcount plan?", placeholder: "yes / no" },
    { key: "team", label: "Hiring team", placeholder: "Platform" },
    { key: "backfill_or_new", label: "Backfill or net-new", placeholder: "net-new" },
    { key: "business_justification", label: "Business justification", placeholder: "scaling on-call coverage" },
    { key: "comp_band_fit", label: "Fit vs comp band", placeholder: "mid-band" },
  ],
  vendor_procurement: [
    { key: "vendor", label: "Vendor name", placeholder: "Acme Analytics" },
    { key: "annual_cost_usd", label: "Annual cost (USD)", placeholder: "120000" },
    { key: "contract_term_months", label: "Contract term (months)", placeholder: "24" },
    { key: "category", label: "Spend category", placeholder: "data / SaaS" },
    { key: "data_access", label: "Data the vendor accesses", placeholder: "customer PII" },
    { key: "security_review", label: "Security review status", placeholder: "SOC 2 reviewed" },
    { key: "alternatives_considered", label: "Alternatives considered", placeholder: "2 others bid" },
    { key: "lock_in_risk", label: "Switching / lock-in risk", placeholder: "high — proprietary format" },
  ],
  budget_spend: [
    { key: "amount_usd", label: "Requested amount (USD)", placeholder: "50000" },
    { key: "budget_line", label: "Budget line / cost center", placeholder: "Marketing-Q3" },
    { key: "remaining_budget_usd", label: "Remaining on the line (USD)", placeholder: "80000" },
    { key: "period", label: "Period", placeholder: "Q3 FY26" },
    { key: "category", label: "Category", placeholder: "opex" },
    { key: "expected_return", label: "Expected return / outcome", placeholder: "12% pipeline lift" },
    { key: "recurring", label: "One-time or recurring", placeholder: "one-time" },
  ],
  project_go_no_go: [
    { key: "objective", label: "Project objective", placeholder: "Migrate billing to the new platform" },
    { key: "budget_usd", label: "Budget (USD)", placeholder: "250000" },
    { key: "timeline_months", label: "Timeline (months)", placeholder: "6" },
    { key: "team_size", label: "Team size (FTEs)", placeholder: "5" },
    { key: "dependencies", label: "Key dependencies", placeholder: "payments API freeze" },
    { key: "success_metric", label: "Primary success metric", placeholder: "0 billing incidents post-cutover" },
    { key: "risk_summary", label: "Known risks", placeholder: "tight cutover window" },
    { key: "jira_project", label: "Jira project key (optional)", placeholder: "BILL" },
  ],
};

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
      const usesRepo = type === "release_go_no_go";
      const body = {
        decision_type: type,
        question,
        context,
        stakes: stakes || null,
        repo: usesRepo ? repo || null : null,
        inputs: usesRepo
          ? {}
          : Object.fromEntries(Object.entries(inputs).filter(([, v]) => v.trim())),
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
                {fieldsByType[type].map((f) => (
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
            {type !== "release_go_no_go" &&
              fieldsByType[type]
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
