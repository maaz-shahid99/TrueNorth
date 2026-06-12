"use client";

import { Bell, LogOut, Search } from "lucide-react";
import { Avatar } from "@/components/ui/Avatar";
import type { Session } from "@/lib/auth";

export function Topbar({ session }: { session: Session }) {
  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-line bg-surface px-6">
      <div className="flex items-center gap-2 text-sm text-muted">
        <span className="font-medium text-ink">{session.tenant}</span>
        <span>/</span>
        <span>Workspace</span>
      </div>
      <div className="flex items-center gap-3">
        <div className="hidden items-center gap-2 rounded-lg border border-line bg-app px-3 py-2 text-sm text-muted md:flex">
          <Search className="h-4 w-4" />
          <input
            placeholder="Search decisions…"
            className="w-48 bg-transparent text-ink outline-none placeholder:text-muted"
          />
        </div>
        <button className="rounded-lg p-2 text-muted hover:bg-app hover:text-ink" aria-label="Notifications">
          <Bell className="h-5 w-5" />
        </button>
        <div className="flex items-center gap-2">
          <Avatar name={session.subject} />
          <div className="hidden leading-tight md:block">
            <p className="text-sm font-medium text-ink">{session.subject}</p>
            <p className="text-xs text-muted">{session.roles.join(", ")}</p>
          </div>
        </div>
        <form action="/api/auth/logout" method="post">
          <button className="rounded-lg p-2 text-muted hover:bg-app hover:text-ink" aria-label="Sign out">
            <LogOut className="h-5 w-5" />
          </button>
        </form>
      </div>
    </header>
  );
}
