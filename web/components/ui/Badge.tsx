import * as React from "react";
import { cn } from "@/lib/utils";
import type { ReviewState, StakesTier, Verdict } from "@/lib/types";
import { reviewStyles, stakesLabel, verdictStyles } from "@/lib/verdict";

export function Badge({
  className,
  children,
}: {
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium",
        className,
      )}
    >
      {children}
    </span>
  );
}

export function VerdictPill({ verdict }: { verdict: Verdict }) {
  const s = verdictStyles[verdict];
  return (
    <Badge className={cn(s.bg, s.text)}>
      <span className={cn("h-1.5 w-1.5 rounded-full", s.dot)} />
      {s.label}
    </Badge>
  );
}

export function ReviewPill({ state }: { state: ReviewState }) {
  const s = reviewStyles[state];
  return <Badge className={cn(s.bg, s.text)}>{s.label}</Badge>;
}

export function StakesPill({ stakes }: { stakes: StakesTier }) {
  return (
    <Badge className="border border-line bg-app text-muted">{stakesLabel[stakes]}</Badge>
  );
}
