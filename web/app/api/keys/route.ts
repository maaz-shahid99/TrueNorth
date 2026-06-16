import { NextResponse } from "next/server";
import { engineFetch, hasEngineCredential } from "@/lib/engine";

// List / mint API keys (admin only at the engine). Demo mode echoes a synthetic key.
export async function GET() {
  if (!(await hasEngineCredential())) {
    const { mockKeys } = await import("@/lib/mock");
    return NextResponse.json(mockKeys);
  }
  const res = await engineFetch("/v1/keys");
  const data = await res.json().catch(() => null);
  if (!res.ok) return NextResponse.json(data ?? { detail: "Engine error" }, { status: res.status });
  return NextResponse.json(data);
}

export async function POST(request: Request) {
  const body = await request.json();
  if (!(await hasEngineCredential())) {
    const key = `tn_demo_${Math.random().toString(36).slice(2, 14)}`;
    return NextResponse.json(
      {
        key,
        info: {
          id: `demo-${Math.random().toString(36).slice(2, 10)}`,
          tenant_id: "default",
          subject: body.subject ?? "",
          roles: body.roles ?? [],
          active: true,
          created_at: new Date().toISOString(),
        },
      },
      { status: 201 },
    );
  }
  const res = await engineFetch("/v1/keys", { method: "POST", body: JSON.stringify(body) });
  const data = await res.json().catch(() => null);
  if (!res.ok) return NextResponse.json(data ?? { detail: "Engine error" }, { status: res.status });
  return NextResponse.json(data, { status: 201 });
}
