import { NextResponse } from "next/server";
import { engineConfigured, engineFetch } from "@/lib/engine";

// Approve / reject a decision (DI-7 / GV-2). Proxies to the engine; echoes a computed
// state in demo mode.
export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const body = await request.json();

  if (!engineConfigured()) {
    const state = body.action === "approve" ? "approved" : "rejected";
    return NextResponse.json(
      {
        decision_id: id,
        required: true,
        state,
        history: [
          {
            decision_id: id,
            actor: "dev@truenorth.local",
            action: body.action,
            note: body.note ?? "",
            at: new Date().toISOString(),
          },
        ],
      },
      { status: 201 },
    );
  }

  const res = await engineFetch(`/v1/decisions/${encodeURIComponent(id)}/review`, {
    method: "POST",
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    return NextResponse.json(data ?? { detail: "Engine error" }, { status: res.status });
  }
  return NextResponse.json(data, { status: 201 });
}
