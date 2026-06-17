import { NextResponse } from "next/server";
import { engineFetch, hasEngineCredential } from "@/lib/engine";

// Extract candidate decisions from a meeting transcript (MI-2). Proposes only — never judges.
// Demo mode (no engine credential) returns a deterministic stub so the flow works offline.
export async function POST(request: Request) {
  const body = await request.json();
  const transcript: string = (body?.transcript ?? "").toString();

  if (!transcript.trim()) {
    return NextResponse.json({ detail: "Transcript is empty." }, { status: 422 });
  }

  if (!(await hasEngineCredential())) {
    return NextResponse.json(demoExtraction(transcript));
  }

  const res = await engineFetch("/v1/meetings/extract", {
    method: "POST",
    body: JSON.stringify({ transcript, title: body?.title ?? "" }),
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) return NextResponse.json(data ?? { detail: "Engine error" }, { status: res.status });
  return NextResponse.json(data);
}

// A believable offline stub: pull the first couple of sentences mentioning a commitment.
function demoExtraction(transcript: string) {
  const sentences = transcript
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
  const cueWords = /(ship|approve|hire|buy|sign|launch|cut|spend|decide|go with|greenlight)/i;
  const picks = sentences.filter((s) => cueWords.test(s)).slice(0, 3);
  const decisions = (picks.length ? picks : sentences.slice(0, 1)).map((s) => ({
    question: s.endsWith("?") ? s : `Should we proceed: ${s.replace(/\.$/, "")}?`,
    decision_type: /discount|approve a/i.test(s)
      ? "discount_approval"
      : /hire|headcount/i.test(s)
        ? "hiring_approval"
        : /ship|release|launch/i.test(s)
          ? "release_go_no_go"
          : "other",
    owner: "",
    deadline: "",
    context: "Extracted from the pasted transcript (demo mode).",
    dissent: "",
  }));
  return {
    summary: "Demo extraction — connect the engine for real meeting analysis.",
    decisions,
  };
}
