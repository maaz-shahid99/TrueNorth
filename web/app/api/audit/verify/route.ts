import { NextResponse } from "next/server";
import { engineFetch, hasEngineCredential } from "@/lib/engine";
import { mockDecisions } from "@/lib/mock";

// Verify the tenant's audit hash chain (GV-3).
export async function GET() {
  if (!(await hasEngineCredential())) {
    return NextResponse.json({
      ok: true,
      entries_checked: mockDecisions.length,
      broken_at_seq: null,
      detail: "Chain intact (demo mode)",
    });
  }
  const res = await engineFetch("/v1/audit/verify");
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    return NextResponse.json(data ?? { detail: "Engine error" }, { status: res.status });
  }
  return NextResponse.json(data);
}
