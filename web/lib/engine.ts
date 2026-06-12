// Server-only BFF helper: calls the engine with the credential attached server-side so the
// browser never sees it. UI-6 swaps the shared dev key for the per-user JWT from the session.
import "server-only";

const ENGINE_URL = process.env.ENGINE_URL ?? "http://127.0.0.1:8000";
const ENGINE_API_KEY = process.env.ENGINE_API_KEY ?? "";

export async function engineFetch(path: string, init?: RequestInit): Promise<Response> {
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");
  if (ENGINE_API_KEY) headers.set("X-API-Key", ENGINE_API_KEY);
  return fetch(`${ENGINE_URL}${path}`, { ...init, headers, cache: "no-store" });
}

export function engineConfigured(): boolean {
  return Boolean(ENGINE_API_KEY);
}
