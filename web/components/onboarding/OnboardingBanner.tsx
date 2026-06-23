"use client";

import { X } from "lucide-react";
import Link from "next/link";
import * as React from "react";

const KEY = "tn_onboarding_dismissed";

// A dismissible welcome banner for new users (persisted in localStorage). AD-1/AD-2.
export function OnboardingBanner() {
  // Start hidden to avoid an SSR/first-paint flash; reveal after reading localStorage.
  const [dismissed, setDismissed] = React.useState(true);
  React.useEffect(() => {
    setDismissed(localStorage.getItem(KEY) === "1");
  }, []);
  if (dismissed) return null;

  function dismiss() {
    localStorage.setItem(KEY, "1");
    setDismissed(true);
  }

  return (
    <div className="flex items-start justify-between gap-4 rounded-2xl border border-brand-200 bg-brand-50 p-4">
      <div>
        <p className="text-sm font-semibold text-brand-700">Welcome to TrueNorth</p>
        <p className="mt-1 text-sm text-ink">
          New here? See how a decision is judged and run your first one in a couple of minutes.
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <Link
            href="/get-started"
            className="rounded-lg bg-brand-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-brand-700"
          >
            Get started
          </Link>
          <Link
            href="/decisions/new"
            className="rounded-lg border border-line bg-surface px-3 py-1.5 text-sm font-medium text-ink hover:bg-app"
          >
            New decision
          </Link>
        </div>
      </div>
      <button onClick={dismiss} aria-label="Dismiss" className="text-muted hover:text-ink">
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}
