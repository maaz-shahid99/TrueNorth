import { NextResponse } from "next/server";
import { engineFetch, hasEngineCredential } from "@/lib/engine";

// Archive a policy (admin only at the engine; the ledger keeps the history).
export async function DELETE(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  if (!(await hasEngineCredential())) {
    return NextResponse.json({ archived: true });
  }
  const res = await engineFetch(`/v1/policies/${encodeURIComponent(id)}`, { method: "DELETE" });
  const data = await res.json().catch(() => null);
  if (!res.ok) return NextResponse.json(data ?? { detail: "Engine error" }, { status: res.status });
  return NextResponse.json(data);
}
