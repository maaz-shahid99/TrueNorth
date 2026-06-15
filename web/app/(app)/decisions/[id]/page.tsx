import { ArrowLeft } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ConditionsList } from "@/components/decision/ConditionsList";
import { DevilsAdvocatePanel } from "@/components/decision/DevilsAdvocatePanel";
import { EvidenceList } from "@/components/decision/EvidenceList";
import { LensCard } from "@/components/decision/LensCard";
import { MinorityReport } from "@/components/decision/MinorityReport";
import { OutcomePanel } from "@/components/decision/OutcomePanel";
import { ReviewPanel } from "@/components/decision/ReviewPanel";
import { VerdictBanner } from "@/components/decision/VerdictBanner";
import { Badge, ReviewPill, StakesPill } from "@/components/ui/Badge";
import { SectionCard } from "@/components/ui/Card";
import { getDecision, getOutcomes } from "@/lib/data";
import { formatCurrency, formatDateTime, formatTokens } from "@/lib/format";
import { decisionTypeLabel } from "@/lib/verdict";

export default async function DecisionDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const d = await getDecision(id);
  if (!d) notFound();
  const outcomes = await getOutcomes(d.id);

  const typeLabel = decisionTypeLabel[d.request.decision_type] ?? d.request.decision_type;

  return (
    <div className="space-y-6">
      <div>
        <Link
          href="/decisions"
          className="inline-flex items-center gap-1 text-sm text-muted hover:text-ink"
        >
          <ArrowLeft className="h-4 w-4" />
          Decisions
        </Link>
        <h1 className="mt-2 max-w-3xl text-xl font-semibold">{d.request.question}</h1>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <Badge className="border border-line bg-app text-muted">{typeLabel}</Badge>
          <StakesPill stakes={d.stakes} />
          <ReviewPill state={d.review_state} />
          <span className="text-xs text-muted">{formatDateTime(d.created_at)}</span>
        </div>
      </div>

      <VerdictBanner recommendation={d.recommendation} />

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
        <div className="space-y-6 xl:col-span-2">
          <MinorityReport text={d.recommendation.minority_report} />
          <ConditionsList conditions={d.recommendation.conditions} />
          <div>
            <h3 className="mb-3 text-sm font-semibold text-ink">Lens assessments</h3>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {d.lenses.map((l) => (
                <LensCard key={l.lens} scored={l} />
              ))}
            </div>
          </div>
          <DevilsAdvocatePanel devil={d.devils_advocate} />
          <EvidenceList evidence={d.evidence} />
        </div>

        <div className="space-y-6">
          <ReviewPanel decision={d} />
          <OutcomePanel decisionId={d.id} initialOutcomes={outcomes} />
          <SectionCard title="Details">
            <dl className="space-y-2.5 text-sm">
              <Row k="Decision type" v={typeLabel} />
              <Row k="Stakes" v={d.stakes} />
              <Row k="Model" v={d.model_used} />
              <Row k="Engine" v={`v${d.engine_version}`} />
              <Row k="Decided" v={formatDateTime(d.created_at)} />
            </dl>
          </SectionCard>
          <SectionCard title="Cost & usage">
            <dl className="space-y-2.5 text-sm">
              <Row k="Cost" v={formatCurrency(d.usage.total_cost_usd)} />
              <Row k="Input tokens" v={formatTokens(d.usage.total_input_tokens)} />
              <Row k="Output tokens" v={formatTokens(d.usage.total_output_tokens)} />
              <Row k="Latency" v={`${(d.usage.total_latency_ms / 1000).toFixed(1)}s`} />
            </dl>
          </SectionCard>
        </div>
      </div>
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <dt className="text-muted">{k}</dt>
      <dd className="text-right font-medium text-ink">{v}</dd>
    </div>
  );
}
