// Server-only BFF helper. Attaches the engine credential server-side so the browser never
// sees it: a per-user SSO JWT from the session if present, else the shared dev API key.
import "server-only";
import { getSession } from "./auth";

const ENGINE_URL = process.env.ENGINE_URL ?? "http://127.0.0.1:8000";
const ENGINE_API_KEY = process.env.ENGINE_API_KEY ?? "";

async function authHeaders(): Promise<Record<string, string> | null> {
  const session = await getSession();
  if (session?.engineToken) return { Authorization: `Bearer ${session.engineToken}` };
  if (ENGINE_API_KEY) return { "X-API-Key": ENGINE_API_KEY };
  return null;
}

export async function hasEngineCredential(): Promise<boolean> {
  return (await authHeaders()) !== null;
}

export async function engineFetch(path: string, init?: RequestInit): Promise<Response> {
  const auth = await authHeaders();
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");
  if (auth) {
    for (const [k, v] of Object.entries(auth)) headers.set(k, v);
  }
  return fetch(`${ENGINE_URL}${path}`, { ...init, headers, cache: "no-store" });
}
