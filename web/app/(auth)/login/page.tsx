import { Compass } from "lucide-react";
import { redirect } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { setSession, type Role } from "@/lib/auth";

export default function LoginPage() {
  async function devLogin(formData: FormData) {
    "use server";
    const subject = (formData.get("subject") as string)?.trim() || "dev@truenorth.local";
    const role = ((formData.get("role") as string) || "admin") as Role;
    await setSession({ subject, tenant: "default", roles: [role] });
    redirect("/dashboard");
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-app px-4">
      <div className="w-full max-w-sm">
        <div className="mb-6 flex items-center justify-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-white">
            <Compass className="h-5 w-5" />
          </span>
          <span className="text-lg font-semibold">TrueNorth</span>
        </div>
        <div className="rounded-2xl border border-line bg-surface p-6 shadow-card">
          <h1 className="text-base font-semibold">Sign in</h1>
          <p className="mt-1 text-sm text-muted">Dev login — Google SSO arrives next.</p>

          <button
            disabled
            className="mt-4 flex w-full items-center justify-center gap-2 rounded-lg border border-line bg-app px-4 py-2 text-sm text-muted"
          >
            Continue with Google (soon)
          </button>

          <div className="my-4 flex items-center gap-3 text-xs text-muted">
            <span className="h-px flex-1 bg-line" />
            or dev login
            <span className="h-px flex-1 bg-line" />
          </div>

          <form action={devLogin} className="space-y-3">
            <div>
              <label className="text-xs font-medium text-muted">Email</label>
              <input
                name="subject"
                defaultValue="dev@truenorth.local"
                className="mt-1 w-full rounded-lg border border-line bg-surface px-3 py-2 text-sm text-ink outline-none focus:border-brand-400"
              />
            </div>
            <div>
              <label className="text-xs font-medium text-muted">Role</label>
              <select
                name="role"
                defaultValue="admin"
                className="mt-1 w-full rounded-lg border border-line bg-surface px-3 py-2 text-sm text-ink outline-none focus:border-brand-400"
              >
                <option value="admin">admin</option>
                <option value="reviewer">reviewer</option>
                <option value="requester">requester</option>
                <option value="viewer">viewer</option>
              </select>
            </div>
            <Button type="submit" className="w-full">
              Sign in
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
