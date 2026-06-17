import { NextResponse } from "next/server";
import { engineFetch, hasEngineCredential } from "@/lib/engine";

// List / create strategic goals. Listing is broad; creation is admin-only at the engine.
export async function GET() {
  if (!(await hasEngineCredential())) {
    const { mockGoals } = await import("@/lib/mock");
    return NextResponse.json(mockGoals);
  }
  const res = await engineFetch("/v1/goals");
  const data = await res.json().catch(() => null);
  if (!res.ok) return NextResponse.json(data ?? { detail: "Engine error" }, { status: res.status });
  return NextResponse.json(data);
}

export async function POST(request: Request) {
  const body = await request.json();
  if (!(await hasEngineCredential())) {
    return NextResponse.json(
      {
        id: `demo-${Math.random().toString(36).slice(2, 10)}`,
        title: body.title ?? "",
        description: body.description ?? "",
        level: body.level ?? "department",
        owner: body.owner ?? "",
        parent_id: body.parent_id ?? null,
        metric: body.metric ?? "",
        status: "active",
        source: "manual",
        created_at: new Date().toISOString(),
      },
      { status: 201 },
    );
  }
  const res = await engineFetch("/v1/goals", { method: "POST", body: JSON.stringify(body) });
  const data = await res.json().catch(() => null);
  if (!res.ok) return NextResponse.json(data ?? { detail: "Engine error" }, { status: res.status });
  return NextResponse.json(data, { status: 201 });
}
