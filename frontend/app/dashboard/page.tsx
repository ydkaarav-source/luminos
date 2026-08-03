"use client";

import { useEffect, useState } from "react";

import { BusinessBuilderCard } from "@/components/dashboard/BusinessBuilderCard";
import { CEOBriefingCard } from "@/components/dashboard/CEOBriefingCard";
import { HealthScoreGauge } from "@/components/dashboard/HealthScoreGauge";
import { SolopreneurHubCard } from "@/components/dashboard/SolopreneurHubCard";
import { Card } from "@/components/ui/Card";
import { AppShell } from "@/components/layout/AppShell";
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

  return (
    <AppShell businessName={business?.name}>
      <div className="mb-8">
        <h1 className="font-display text-2xl font-medium">
          {greeting()}
          {business ? `, ${business.name}` : ""}.
        </h1>
        <p className="text-ink-muted mt-1">
          {business
            ? `Here's where ${business.name} stands today.`
            : "Setting up your command center…"}
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5">
        <Card className="lg:col-span-1 flex items-center gap-5">
          {score ? (
            <>
              <HealthScoreGauge score={score.overall_score} />
              <div>
                <p className="label mb-1">Business Health</p>
                <p className="text-sm text-ink-muted">
                  {score.overall_score >= 75
                    ? "Strong across the board."
                    : score.overall_score >= 50
                    ? "Solid, with room to grow."
                    : "A few areas need attention."}
                </p>
              </div>
            </>
          ) : (
            <div className="w-full text-center py-4">
              <p className="text-sm text-ink-faint mb-3">No health score yet.</p>
            </div>
          )}
        </Card>

        <div className="lg:col-span-2">
          <CEOBriefingCard briefing={briefing} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <SolopreneurHubCard tasks={tasks} />
        <BusinessBuilderCard />
      </div>
    </AppShell>
  );
}
