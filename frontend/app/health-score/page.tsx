"use client";

import { useState } from "react";

import { HealthScoreGauge } from "@/components/dashboard/HealthScoreGauge";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { useHealthScore } from "@/hooks/useHealthScore";
import { apiClient } from "@/lib/api-client";
import type { HealthScore } from "@/lib/types";

const CATEGORY_LABELS: Record<string, string> = {
  revenue_score: "Revenue",
  operations_score: "Operations",
  marketing_score: "Marketing",
  customer_growth_score: "Customer growth",
  financial_management_score: "Financial management",
};

export default function HealthScorePage() {
  const { score: initialScore, loading } = useHealthScore();
  const [score, setScore] = useState<HealthScore | null>(null);
  const [recalculating, setRecalculating] = useState(false);
  const active = score ?? initialScore;

  async function recalculate() {
    setRecalculating(true);
    try {
      const result = await apiClient.post<HealthScore>("/health-score/recalculate");
      setScore(result);
    } finally {
      setRecalculating(false);
    }
  }

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="font-display text-2xl font-medium mb-1">Business Health Score</h1>
          <p className="text-ink-muted">A rule-based score, explained in plain language by AI.</p>
        </div>
        <Button onClick={recalculate} disabled={recalculating}>
          {recalculating ? "Recalculating…" : "Recalculate"}
        </Button>
      </div>

      {loading ? (
        <p className="text-sm text-ink-faint">Loading…</p>
      ) : !active ? (
        <Card>
          <p className="text-sm text-ink-muted">
            No score yet. Click "Recalculate" to generate your first Business Health Score.
          </p>
        </Card>
      ) : (
        <div className="space-y-5">
          <Card className="flex items-center gap-6">
            <HealthScoreGauge score={active.overall_score} />
            <div className="grid grid-cols-2 gap-4 flex-1">
              {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
                <div key={key}>
                  <p className="label mb-1">{label}</p>
                  <p className="text-lg font-display">{active[key as keyof HealthScore] as number}</p>
                </div>
              ))}
            </div>
          </Card>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            <Card>
              <CardHeader title="Strengths" />
              <ul className="text-sm text-ink-muted space-y-1.5 list-disc list-inside">
                {active.ai_explanation.strengths.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </Card>
            <Card>
              <CardHeader title="Weaknesses" />
              <ul className="text-sm text-ink-muted space-y-1.5 list-disc list-inside">
                {active.ai_explanation.weaknesses.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </Card>
            <Card>
              <CardHeader title="Recommendations" />
              <ul className="text-sm text-ink-muted space-y-1.5 list-disc list-inside">
                {active.ai_explanation.recommendations.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </Card>
          </div>
        </div>
      )}
    </AppShell>
  );
}
