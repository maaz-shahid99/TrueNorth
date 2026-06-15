import { NextResponse } from "next/server";
import { engineConfigured, engineFetch } from "@/lib/engine";

// Record an outcome for a decision (DI-8). Echoes back in demo mode.
export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const body = await request.json();

  if (!engineConfigured()) {
    return NextResponse.json(
      { decision_id: id, recorded_at: new Date().toISOString(), metrics: {}, ...body },
      { status: 201 },
    );
  }

  const res = await engineFetch(`/v1/decisions/${encodeURIComponent(id)}/outcomes`, {
    method: "POST",
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    return NextResponse.json(data ?? { detail: "Engine error" }, { status: res.status });
  }
  return NextResponse.json(data, { status: 201 });
}
