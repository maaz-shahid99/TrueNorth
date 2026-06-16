import Link from "next/link";
import { VerifyChainCard } from "@/components/audit/VerifyChainCard";
import { ReviewPill, VerdictPill } from "@/components/ui/Badge";
import { SectionCard } from "@/components/ui/Card";
import { Table, Td, Th, Thead, Tr } from "@/components/ui/Table";
import { listDecisions } from "@/lib/data";
import { formatDateTime } from "@/lib/format";

export default async function AuditPage() {
  const decisions = await listDecisions();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold">Audit</h1>
        <p className="text-sm text-muted">The tamper-evident decision ledger (GV-3).</p>
      </div>

      <VerifyChainCard />

      <SectionCard title="Ledger" bodyClassName="p-0">
        <Table>
          <Thead>
            <tr className="border-b border-line">
              <Th className="pl-5">Decision</Th>
              <Th>Verdict</Th>
              <Th>Review</Th>
              <Th className="pr-5">Recorded</Th>
            </tr>
          </Thead>
          <tbody>
            {decisions.map((d) => (
              <Tr key={d.id}>
                <Td className="max-w-md pl-5">
                  <Link
                    href={`/decisions/${d.id}`}
                    className="line-clamp-1 text-ink hover:text-brand-700"
                  >
                    {d.request.question}
                  </Link>
                </Td>
                <Td>
                  <VerdictPill verdict={d.recommendation.verdict} />
                </Td>
                <Td>
                  <ReviewPill state={d.review_state} />
                </Td>
                <Td className="whitespace-nowrap pr-5 text-muted">
                  {formatDateTime(d.created_at)}
                </Td>
              </Tr>
            ))}
          </tbody>
        </Table>
      </SectionCard>
    </div>
  );
}
