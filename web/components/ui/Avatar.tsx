import { cn } from "@/lib/utils";

function initials(name: string): string {
  const parts = name.replace(/@.*/, "").split(/[.\s_-]+/).filter(Boolean);
  return (parts[0]?.[0] ?? "?").concat(parts[1]?.[0] ?? "").toUpperCase();
}

export function Avatar({ name, className }: { name: string; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700",
        className,
      )}
      title={name}
    >
      {initials(name)}
    </span>
  );
}
