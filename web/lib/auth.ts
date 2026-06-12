// Dev-login stub (UI-1). A plain session cookie carries the principal so every page can be
// built and gated now; Google SSO replaces this in UI-6 (the cookie/JWT seam stays).
import { cookies } from "next/headers";

export type Role = "viewer" | "requester" | "reviewer" | "admin";

export interface Session {
  subject: string;
  tenant: string;
  roles: Role[];
}

const COOKIE = "tn_session";

export async function getSession(): Promise<Session | null> {
  const raw = (await cookies()).get(COOKIE)?.value;
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Session;
  } catch {
    return null;
  }
}

export async function setSession(session: Session): Promise<void> {
  (await cookies()).set(COOKIE, JSON.stringify(session), {
    httpOnly: true,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,
  });
}

export async function clearSession(): Promise<void> {
  (await cookies()).delete(COOKIE);
}

export function can(session: Session | null, role: Role): boolean {
  if (!session) return false;
  if (session.roles.includes("admin")) return true;
  return session.roles.includes(role);
}
