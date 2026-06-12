import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { Card } from "./Card";
import { cn } from "@/lib/utils";

type Tint = "blue" | "lilac" | "mint" | "peach" | "plain";

const tints: Record<Tint, string> = {
  blue: "bg-pastel-blue",
  lilac: "bg-pastel-lilac",
  mint: "bg-pastel-mint",
  peach: "bg-pastel-peach",
  plain: "bg-surface",
};

export function StatCard({
  label,
  value,
  delta,
  tint = "plain",
}: {
  label: string;
  value: string;
  delta?: { value: string; direction: "up" | "down" };
  tint?: Tint;
}) {
  return (
    <Card className={cn("p-5", tints[tint])}>
      <p className="text-sm text-muted">{label}</p>
      <div className="mt-3 flex items-end justify-between">
        <span className="text-3xl font-semibold tracking-tight text-ink">{value}</span>
        {delta && (
          <span
            className={cn(
              "inline-flex items-center gap-0.5 text-xs font-medium",
              delta.direction === "up" ? "text-verdict-endorse" : "text-verdict-oppose",
            )}
          >
            {delta.value}
            {delta.direction === "up" ? (
              <ArrowUpRight className="h-3.5 w-3.5" />
            ) : (
              <ArrowDownRight className="h-3.5 w-3.5" />
            )}
          </span>
        )}
      </div>
    </Card>
  );
}
