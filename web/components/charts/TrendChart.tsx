"use client";

import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis } from "recharts";
import { BRAND_HEX } from "@/lib/verdict";

export function TrendChart({ data }: { data: { label: string; count: number }[] }) {
  return (
    <div className="h-[220px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="tnTrend" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={BRAND_HEX} stopOpacity={0.25} />
              <stop offset="100%" stopColor={BRAND_HEX} stopOpacity={0} />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="label"
            tickLine={false}
            axisLine={false}
            tick={{ fontSize: 12, fill: "#6B7280" }}
          />
          <Tooltip
            cursor={{ stroke: "#ECECEE" }}
            contentStyle={{ borderRadius: 12, border: "1px solid #ECECEE", fontSize: 12 }}
          />
          <Area
            type="monotone"
            dataKey="count"
            stroke={BRAND_HEX}
            strokeWidth={2}
            fill="url(#tnTrend)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
