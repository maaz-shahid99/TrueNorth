"use client";

import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis } from "recharts";
import { BRAND_HEX } from "@/lib/verdict";

export function StakesBars({ data }: { data: { stakes: string; count: number }[] }) {
  return (
    <div className="h-[180px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <XAxis
            dataKey="stakes"
            tickLine={false}
            axisLine={false}
            tick={{ fontSize: 12, fill: "#6B7280" }}
          />
          <Tooltip
            cursor={{ fill: "#F7F8FA" }}
            contentStyle={{ borderRadius: 12, border: "1px solid #ECECEE", fontSize: 12 }}
          />
          <Bar dataKey="count" fill={BRAND_HEX} radius={[6, 6, 0, 0]} barSize={28} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
