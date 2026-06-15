import { NextResponse } from "next/server";
import { engineConfigured, engineFetch } from "@/lib/engine";
import { makeDemoDecision } from "@/lib/mock";
import type { DecisionRequest } from "@/lib/types";

// Create + judge a decision. Proxies to the engine when configured; otherwise synthesizes
// a demo record so the submit → detail flow works offline.
export async function POST(request: Request) {
  const body = (await request.json()) as Partial<DecisionRequest>;

  if (!engineConfigured()) {
    return NextResponse.json(makeDemoDecision(body), { status: 201 });
  }

  const res = await engineFetch("/v1/decisions", {
    method: "POST",
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    return NextResponse.json(data ?? { detail: "Engine error" }, { status: res.status });
  }
  return NextResponse.json(data, { status: 201 });
}
