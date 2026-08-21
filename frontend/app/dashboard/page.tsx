"use client";

import { useEffect, useState } from "react";

import { BusinessBuilderCard } from "@/components/dashboard/BusinessBuilderCard";
import { CEOBriefingCard } from "@/components/dashboard/CEOBriefingCard";
import { HealthScoreGauge } from "@/components/dashboard/HealthScoreGauge";
import { SolopreneurHubCard } from "@/components/dashboard/SolopreneurHubCard";
import { AppShell } from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader } from "@/components/ui/Card";
import { useBusiness } from "@/hooks/useBusiness";
import { useHealthScore } from "@/hooks/useHealthScore";
import { useTasks } from "@/hooks/useTasks";
import { apiClient } from "@/lib/api-client";
import type { CEOBriefing } from "@/lib/types";

function greeting(): string {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

export default function DashboardPage() {
  const { business } = useBusiness();
  const { score } = useHealthScore();
  const { tasks } = useTasks();
  const [briefing, setBriefing] = useState<CEOBriefing | null>(null);

  useEffect(() => {
    apiClient.get<CEOBriefing>("/ceo-briefing/today").then(setBriefing).catch(() => {});
  }, []);

  const tasksDone = tasks.filter((t) => t.status === "done").length;
  const completionRate = tasks.length > 0 ? Math.round((tasksDone / tasks.length) * 100) : null;

  return (
    <AppShell businessName={business?.name}>
      <div className="mb-8">
        <h1 className="font-display text-2xl font-medium">
          {greeting()}
          {business ? `, ${business.name}` : ""}.
        </h1>
        <p className="text-night-text-muted mt-1">
          {business
            ? `Here's where ${business.name} stands today.`
            : "Setting up your command center…"}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-5">
        <Card>
          {score ? (
            <>
              <div className="flex items-center gap-5">
                <HealthScoreGauge score={score.overall_score} />
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <p className="label">Business Health</p>
                    {score.is_demo && <Badge variant="demo">Demo</Badge>}
                  </div>
                  <p className="text-sm text-night-text-muted">
                    {score.overall_score >= 75
                      ? "Strong across the board."
                      : score.overall_score >= 50
                      ? "Solid, with room to grow."
                      : "A few areas need attention."}
                  </p>
                </div>
              </div>
              <div className="mt-5 pt-5 border-t border-night-border grid grid-cols-3 gap-3 text-center">
                <div>
                  <p className="text-lg font-medium text-accent-bright">{score.revenue_score}</p>
                  <p className="text-xs text-night-text-muted mt-0.5">Revenue score</p>
                </div>
                <div>
                  <p className="text-lg font-medium text-accent-bright">
                    {tasksDone}/{tasks.length}
                  </p>
                  <p className="text-xs text-night-text-muted mt-0.5">Tasks done</p>
                </div>
                <div>
                  <p className="text-lg font-medium text-accent-bright">
                    {completionRate === null ? "—" : `${completionRate}%`}
                  </p>
                  <p className="text-xs text-night-text-muted mt-0.5">Completion rate</p>
                </div>
              </div>
            </>
          ) : (
            <div className="w-full text-center py-4">
              <p className="text-sm text-night-text-muted mb-3">No health score yet.</p>
            </div>
          )}
        </Card>

        <CEOBriefingCard briefing={briefing} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <SolopreneurHubCard tasks={tasks} />

        <Card>
          <CardHeader title="This week" />
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-night-text-muted">Revenue score</span>
              <span className="text-sm font-medium text-night-text">
                {score ? `${score.revenue_score} / 100` : "—"}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-night-text-muted">Tasks completed</span>
              <span className="text-sm font-medium text-night-text">{tasksDone}</span>
            </div>
          </div>
        </Card>

        <BusinessBuilderCard />
      </div>
    </AppShell>
  );
}
