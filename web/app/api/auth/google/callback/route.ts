import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { setSession, type Role } from "@/lib/auth";

const ENGINE_URL = process.env.ENGINE_URL ?? "http://127.0.0.1:8000";

// Google redirects here with a code. Exchange it for an ID token, hand that to the engine
// for a TrueNorth JWT, store the session, and land on the dashboard.
export async function GET(request: Request) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const state = url.searchParams.get("state");
  const saved = (await cookies()).get("g_state")?.value;
  const fail = (reason: string) =>
    NextResponse.redirect(new URL(`/login?error=${reason}`, request.url));

  if (!code || !state || state !== saved) return fail("oauth_state");

  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  if (!clientId || !clientSecret) return fail("google_not_configured");

  const tokenRes = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      code,
      client_id: clientId,
      client_secret: clientSecret,
      redirect_uri: `${url.origin}/api/auth/google/callback`,
      grant_type: "authorization_code",
    }),
  });
  const tokenData = await tokenRes.json().catch(() => null);
  const idToken = tokenData?.id_token as string | undefined;
  if (!idToken) return fail("token_exchange");

  const authRes = await fetch(`${ENGINE_URL}/v1/auth/google`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id_token: idToken }),
  });
  if (!authRes.ok) return fail("engine_auth");
  const { token, principal } = await authRes.json();

  await setSession({
    subject: principal.subject,
    tenant: principal.tenant_id,
    roles: principal.roles as Role[],
    engineToken: token,
  });
  return NextResponse.redirect(new URL("/dashboard", request.url));
}
