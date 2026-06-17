import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { DecisionsTable } from "@/components/decision/DecisionsTable";
import { listDecisions } from "@/lib/data";

const PAGE_SIZE = 25;

export default async function DecisionsHistoryPage({
  searchParams,
}: {
  searchParams: Promise<{ page?: string }>;
}) {
  const { page: pageParam } = await searchParams;
  const page = Math.max(1, Number(pageParam) || 1);
  const offset = (page - 1) * PAGE_SIZE;

  // Fetch one extra row to detect whether a next page exists, then trim.
  const rows = await listDecisions({ limit: PAGE_SIZE + 1, offset });
  const hasNext = rows.length > PAGE_SIZE;
  const decisions = rows.slice(0, PAGE_SIZE);
  const hasPrev = page > 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Decisions</h1>
          <p className="text-sm text-muted">Every decision your workspace has judged.</p>
        </div>
        <Link href="/decisions/new">
          <Button>New decision</Button>
        </Link>
      </div>

      <DecisionsTable decisions={decisions} />

      {(hasPrev || hasNext) && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted">
            Page {page}
            {decisions.length > 0 && (
              <span>
                {" "}
                · showing {offset + 1}–{offset + decisions.length}
              </span>
            )}
          </p>
          <div className="flex gap-2">
            {hasPrev ? (
              <Link href={`/decisions?page=${page - 1}`}>
                <Button variant="secondary" size="sm">
                  Previous
                </Button>
              </Link>
            ) : (
              <Button variant="secondary" size="sm" disabled>
                Previous
              </Button>
            )}
            {hasNext ? (
              <Link href={`/decisions?page=${page + 1}`}>
                <Button variant="secondary" size="sm">
                  Next
                </Button>
              </Link>
            ) : (
              <Button variant="secondary" size="sm" disabled>
                Next
              </Button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
