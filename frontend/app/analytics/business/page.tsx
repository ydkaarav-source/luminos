"use client";

import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { AnalyticsTabs } from "@/components/analytics/AnalyticsTabs";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardHeader } from "@/components/ui/Card";
import { apiClient } from "@/lib/api-client";
import type { BusinessAnalytics } from "@/lib/types";

const CHART_COLORS = {
  accent: "#3E6FD4",
  positive: "#52B98A",
  grid: "#343D54",
  text: "#9AA3BC",
};

function formatDate(iso: unknown) {
  if (!iso) return "";
  const d = new Date(iso as string | number);
  if (isNaN(d.getTime())) return String(iso);
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export default function BusinessAnalyticsPage() {
  const [data, setData] = useState<BusinessAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get<BusinessAnalytics>("/analytics/business")
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-medium mb-1">Analytics</h1>
      <p className="text-ink-muted mb-2">A closer look at how your business is trending.</p>
      <AnalyticsTabs />

      {loading ? (
        <p className="text-sm text-ink-faint">Loading…</p>
      ) : !data ? (
        <p className="text-sm text-ink-faint">No analytics data yet.</p>
      ) : (
        <div className="space-y-5">
          <Card>
            <CardHeader title="Revenue over time" subtitle="Logged revenue, by day" />
            {data.revenue_over_time.length === 0 ? (
              <p className="text-sm text-ink-faint">No revenue logged yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={240}>
                <AreaChart data={data.revenue_over_time}>
                  <defs>
                    <linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={CHART_COLORS.accent} stopOpacity={0.35} />
                      <stop offset="100%" stopColor={CHART_COLORS.accent} stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
                  <XAxis
                    dataKey="period"
                    tickFormatter={formatDate}
                    stroke={CHART_COLORS.text}
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis stroke={CHART_COLORS.text} fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip
                    labelFormatter={formatDate}
                    contentStyle={{ background: "#242B3D", border: "1px solid #343D54", borderRadius: 8 }}
                    labelStyle={{ color: "#EDF0F5" }}
                  />
                  <Area
                    type="monotone"
                    dataKey="amount"
                    stroke={CHART_COLORS.accent}
                    strokeWidth={2}
                    fill="url(#revenueFill)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </Card>

          <Card>
            <CardHeader title="Task completion" subtitle="Tasks created vs. completed, by day" />
            {data.task_completion_over_time.length === 0 ? (
              <p className="text-sm text-ink-faint">No task activity yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={data.task_completion_over_time}>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
                  <XAxis
                    dataKey="period"
                    tickFormatter={formatDate}
                    stroke={CHART_COLORS.text}
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis stroke={CHART_COLORS.text} fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                  <Tooltip
                    labelFormatter={formatDate}
                    contentStyle={{ background: "#242B3D", border: "1px solid #343D54", borderRadius: 8 }}
                    labelStyle={{ color: "#EDF0F5" }}
                  />
                  <Bar dataKey="created" fill={CHART_COLORS.grid} radius={[3, 3, 0, 0]} />
                  <Bar dataKey="completed" fill={CHART_COLORS.positive} radius={[3, 3, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Card>

          <Card>
            <CardHeader title="Health Score history" subtitle="Overall score over time" />
            {data.health_score_history.length === 0 ? (
              <p className="text-sm text-ink-faint">No health scores calculated yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={data.health_score_history}>
                  <CartesianGrid strokeDasharray="3 3" stroke={CHART_COLORS.grid} vertical={false} />
                  <XAxis
                    dataKey="calculated_at"
                    tickFormatter={formatDate}
                    stroke={CHART_COLORS.text}
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    domain={[0, 100]}
                    stroke={CHART_COLORS.text}
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip
                    labelFormatter={formatDate}
                    contentStyle={{ background: "#242B3D", border: "1px solid #343D54", borderRadius: 8 }}
                    labelStyle={{ color: "#EDF0F5" }}
                  />
                  <Line
                    type="monotone"
                    dataKey="overall_score"
                    stroke={CHART_COLORS.positive}
                    strokeWidth={2}
                    dot={{ fill: CHART_COLORS.positive, r: 3 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </Card>
        </div>
      )}
    </AppShell>
  );
}