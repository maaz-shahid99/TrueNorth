import { NextResponse } from "next/server";
import { engineFetch, hasEngineCredential } from "@/lib/engine";

// Revoke an API key (admin only at the engine).
export async function DELETE(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  if (!(await hasEngineCredential())) {
    return NextResponse.json({ revoked: true });
  }
  const res = await engineFetch(`/v1/keys/${encodeURIComponent(id)}`, { method: "DELETE" });
  const data = await res.json().catch(() => null);
  if (!res.ok) return NextResponse.json(data ?? { detail: "Engine error" }, { status: res.status });
  return NextResponse.json(data);
}
