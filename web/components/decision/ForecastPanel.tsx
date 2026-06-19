import { SectionCard } from "@/components/ui/Card";
import { formatPercent } from "@/lib/format";
import type { ScenarioForecast } from "@/lib/types";

// What-if scenario projection for a high-stakes decision (SF-1/SF-2).
export function ForecastPanel({ forecast }: { forecast: ScenarioForecast }) {
  return (
    <SectionCard title="Scenario forecast">
      {forecast.summary && <p className="text-sm text-ink">{forecast.summary}</p>}
      <div className="mt-3 space-y-3">
        {forecast.scenarios.map((s, i) => (
          <div key={i} className="rounded-xl border border-line p-3">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-medium text-ink">{s.name}</p>
              <span className="rounded-full bg-app px-2 py-0.5 text-xs font-medium text-muted">
                ~{formatPercent(s.probability)}
              </span>
            </div>
            <p className="mt-1 text-sm text-muted">{s.projection}</p>
            {s.drivers.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {s.drivers.map((d, j) => (
                  <span key={j} className="rounded-full bg-app px-2 py-0.5 text-xs text-muted">
                    {d}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </SectionCard>
  );
}
