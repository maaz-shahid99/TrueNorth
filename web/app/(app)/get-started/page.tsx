import {
  FileText,
  PlusCircle,
  Scale,
  ShieldCheck,
  Target,
  type LucideIcon,
} from "lucide-react";
import Link from "next/link";
import { SectionCard } from "@/components/ui/Card";

const steps: { href: string; label: string; blurb: string; icon: LucideIcon }[] = [
  {
    href: "/decisions/new",
    label: "Submit a decision",
    blurb: "Pick a type, describe the call, and get a verdict with reasoning, evidence, and risks.",
    icon: PlusCircle,
  },
  {
    href: "/decisions/from-meeting",
    label: "Extract from a meeting",
    blurb: "Paste a transcript — TrueNorth pulls out the decisions and you send each to judgment.",
    icon: FileText,
  },
  {
    href: "/goals",
    label: "Set your goals",
    blurb: "Add the OKRs decisions should be judged against; each verdict is scored for alignment.",
    icon: Target,
  },
  {
    href: "/policies",
    label: "Add a decision-rights policy",
    blurb: "Require sign-off when stakes, spend, or goal conflicts cross the lines you set.",
    icon: Scale,
  },
  {
    href: "/reviews",
    label: "Review & record outcomes",
    blurb: "Approve gated decisions, then record what happened to power the learning loop.",
    icon: ShieldCheck,
  },
];

const pipeline = [
  "Classify the stakes (S1 existential → S4 routine).",
  "Gather cited evidence from a connector (GitHub, Jira, or facts you enter).",
  "Surface precedent — similar past decisions and how they turned out.",
  "Score strategic alignment against your active goals.",
  "Run independent lenses (financial, risk, customer, legal, …).",
  "Run a devil's advocate that argues the decision is a mistake.",
  "Project what-if scenarios for high-stakes decisions.",
  "Synthesize one verdict + confidence + conditions + a minority report.",
  "Record it to a tamper-evident audit ledger; gate for human review when warranted.",
];

export default function GetStartedPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Get started</h1>
        <p className="text-sm text-muted">
          TrueNorth judges a proposed decision from multiple independent angles and returns a
          structured, auditable recommendation — you always make the final call.
        </p>
      </div>

      <SectionCard title="Your first steps">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {steps.map((s) => {
            const Icon = s.icon;
            return (
              <Link
                key={s.href}
                href={s.href}
                className="flex gap-3 rounded-xl border border-line bg-surface p-4 transition-colors hover:bg-app"
              >
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand-700">
                  <Icon className="h-5 w-5" />
                </span>
                <span>
                  <span className="block text-sm font-medium text-ink">{s.label}</span>
                  <span className="mt-0.5 block text-sm text-muted">{s.blurb}</span>
                </span>
              </Link>
            );
          })}
        </div>
      </SectionCard>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <SectionCard title="How a decision is judged">
          <ol className="list-decimal space-y-1.5 pl-5 text-sm text-ink">
            {pipeline.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ol>
        </SectionCard>

        <SectionCard title="Key concepts">
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="font-medium text-ink">Verdict scale</dt>
              <dd className="text-muted">Endorse · Endorse-with-conditions · Caution · Oppose.</dd>
            </div>
            <div>
              <dt className="font-medium text-ink">Stakes tiers</dt>
              <dd className="text-muted">
                S1 existential → S4 routine. Higher stakes route to stronger models and stricter
                review.
              </dd>
            </div>
            <div>
              <dt className="font-medium text-ink">Human in the loop</dt>
              <dd className="text-muted">
                TrueNorth advises and records; a person approves gated decisions and keeps
                authority.
              </dd>
            </div>
            <div>
              <dt className="font-medium text-ink">Auditable by design</dt>
              <dd className="text-muted">
                Every decision lands in a tamper-evident, hash-chained ledger you can verify.
              </dd>
            </div>
          </dl>
        </SectionCard>
      </div>
    </div>
  );
}
