import { NextResponse } from "next/server";
import { engineFetch, hasEngineCredential } from "@/lib/engine";

// List / create decision-rights policies. Listing is broad; creation is admin-only at the engine.
export async function GET() {
  if (!(await hasEngineCredential())) {
    const { mockPolicies } = await import("@/lib/mock");
    return NextResponse.json(mockPolicies);
  }
  const res = await engineFetch("/v1/policies");
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
        name: body.name ?? "",
        description: body.description ?? "",
        condition: {
          decision_types: body.condition?.decision_types ?? [],
          min_stakes: body.condition?.min_stakes ?? null,
          verdicts: body.condition?.verdicts ?? [],
          on_alignment_conflict: body.condition?.on_alignment_conflict ?? false,
          min_cost_usd: body.condition?.min_cost_usd ?? null,
        },
        effect: body.effect ?? "require_review",
        required_role: body.required_role ?? "reviewer",
        status: "active",
        created_at: new Date().toISOString(),
      },
      { status: 201 },
    );
  }
  const res = await engineFetch("/v1/policies", { method: "POST", body: JSON.stringify(body) });
  const data = await res.json().catch(() => null);
  if (!res.ok) return NextResponse.json(data ?? { detail: "Engine error" }, { status: res.status });
  return NextResponse.json(data, { status: 201 });
}
