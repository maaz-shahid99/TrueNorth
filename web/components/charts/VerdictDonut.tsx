"use client";

import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";
import type { Verdict } from "@/lib/types";
import { verdictHex, verdictStyles } from "@/lib/verdict";

export function VerdictDonut({ data }: { data: { verdict: Verdict; count: number }[] }) {
  const total = data.reduce((a, d) => a + d.count, 0);
  const chartData = data.filter((d) => d.count > 0).map((d) => ({ name: d.verdict, value: d.count }));

  return (
    <div className="flex items-center gap-4">
      <div className="relative h-[140px] w-[140px] shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              innerRadius={45}
              outerRadius={65}
              paddingAngle={2}
              stroke="none"
            >
              {chartData.map((d) => (
                <Cell key={d.name} fill={verdictHex[d.name as Verdict]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-xl font-semibold text-ink">{total}</span>
          <span className="text-xs text-muted">decisions</span>
        </div>
      </div>
      <ul className="flex-1 space-y-1.5">
        {data.map((d) => (
          <li key={d.verdict} className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-muted">
              <span className="h-2 w-2 rounded-full" style={{ background: verdictHex[d.verdict] }} />
              {verdictStyles[d.verdict].label}
            </span>
            <span className="font-medium text-ink">{d.count}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
