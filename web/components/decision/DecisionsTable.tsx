"use client";

import Link from "next/link";
import * as React from "react";
import { ReviewPill, StakesPill, VerdictPill } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { Input, Select } from "@/components/ui/Input";
import { Table, Td, Th, Thead, Tr } from "@/components/ui/Table";
import { formatDate } from "@/lib/format";
import type { DecisionRecord } from "@/lib/types";
import { VERDICTS } from "@/lib/types";
import { decisionTypeLabel } from "@/lib/verdict";

export function DecisionsTable({ decisions }: { decisions: DecisionRecord[] }) {
  const [q, setQ] = React.useState("");
  const [type, setType] = React.useState("");
  const [verdict, setVerdict] = React.useState("");

  const filtered = decisions.filter((d) => {
    if (q && !d.request.question.toLowerCase().includes(q.toLowerCase())) return false;
    if (type && d.request.decision_type !== type) return false;
    if (verdict && d.recommendation.verdict !== verdict) return false;
    return true;
  });

  return (
    <Card>
      <div className="flex flex-wrap items-center gap-3 border-b border-line p-4">
        <Input
          placeholder="Search decisions…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="mt-0 w-64"
        />
        <Select value={type} onChange={(e) => setType(e.target.value)} className="mt-0 w-44">
          <option value="">All types</option>
          <option value="release_go_no_go">Release go/no-go</option>
          <option value="discount_approval">Discount approval</option>
        </Select>
        <Select value={verdict} onChange={(e) => setVerdict(e.target.value)} className="mt-0 w-52">
          <option value="">All verdicts</option>
          {VERDICTS.map((v) => (
            <option key={v} value={v}>
              {v}
            </option>
          ))}
        </Select>
        <span className="ml-auto text-sm text-muted">
          {filtered.length} of {decisions.length}
        </span>
      </div>

      {filtered.length === 0 ? (
        <div className="p-6">
          <EmptyState title="No decisions match" description="Try clearing the filters." />
        </div>
      ) : (
        <Table>
          <Thead>
            <tr className="border-b border-line">
              <Th className="pl-5">Decision</Th>
              <Th>Type</Th>
              <Th>Stakes</Th>
              <Th>Verdict</Th>
              <Th>Review</Th>
              <Th className="pr-5">Date</Th>
            </tr>
          </Thead>
          <tbody>
            {filtered.map((d) => (
              <Tr key={d.id}>
                <Td className="max-w-xs pl-5">
                  <Link
                    href={`/decisions/${d.id}`}
                    className="line-clamp-1 font-medium text-ink hover:text-brand-700"
                  >
                    {d.request.question}
                  </Link>
                </Td>
                <Td className="text-muted">
                  {decisionTypeLabel[d.request.decision_type] ?? d.request.decision_type}
                </Td>
                <Td>
                  <StakesPill stakes={d.stakes} />
                </Td>
                <Td>
                  <VerdictPill verdict={d.recommendation.verdict} />
                </Td>
                <Td>
                  <ReviewPill state={d.review_state} />
                </Td>
                <Td className="whitespace-nowrap pr-5 text-muted">{formatDate(d.created_at)}</Td>
              </Tr>
            ))}
          </tbody>
        </Table>
      )}
    </Card>
  );
}
