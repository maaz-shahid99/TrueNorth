import { MessageSquare } from "lucide-react";

export function MinorityReport({ text }: { text: string }) {
  return (
    <div className="rounded-2xl border border-brand-200 bg-brand-50 p-5">
      <div className="flex items-center gap-2 text-brand-700">
        <MessageSquare className="h-4 w-4" />
        <h3 className="text-sm font-semibold">Minority report</h3>
      </div>
      <p className="mt-2 text-sm leading-relaxed text-ink">{text}</p>
    </div>
  );
}
