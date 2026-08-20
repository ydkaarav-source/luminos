"use client";

import { useState } from "react";

import { HealthScoreGauge } from "@/components/dashboard/HealthScoreGauge";
import { AppShell } from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { useHealthScore } from "@/hooks/useHealthScore";
import { apiClient } from "@/lib/api-client";
import type { HealthScore, HealthScoreRole } from "@/lib/types";

const CATEGORY_LABELS: Record<string, string> = {
  revenue_score: "Revenue",
  operations_score: "Operations",
  marketing_score: "Marketing",
  customer_growth_score: "Customer growth",
  financial_management_score: "Financial management",
};

// CEO listed first - it's the synthesized top-level view, the other four
// are each scoped to one narrow slice of the business.
const ROLES: { key: HealthScoreRole; label: string; description: string }[] = [
  { key: "ceo", label: "CEO", description: "The synthesized, top-level read across the whole business." },
  { key: "cfo", label: "CFO", description: "Revenue and financial management." },
  { key: "cmo", label: "CMO", description: "Marketing performance." },
  { key: "coo", label: "COO", description: "Operations and task execution." },
  { key: "cro", label: "CRO", description: "Customer growth." },
];

export default function HealthScorePage() {
  const { score: initialScore, loading } = useHealthScore();
  const [score, setScore] = useState<HealthScore | null>(null);
  const [recalculating, setRecalculating] = useState(false);
  const [activeRole, setActiveRole] = useState<HealthScoreRole>("ceo");
  const active = score ?? initialScore;
  const activeExplanation = active?.ai_explanation[activeRole];
  const activeRoleMeta = ROLES.find((r) => r.key === activeRole);

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
          <div className="flex items-center gap-2 mb-1">
            <h1 className="font-display text-2xl font-medium">Business Health Score</h1>
            {active?.is_demo && <Badge variant="demo">Demo</Badge>}
          </div>
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

          <div className="flex gap-1 border-b border-border-subtle">
            {ROLES.map((role) => (
              <button
                key={role.key}
                onClick={() => setActiveRole(role.key)}
                className={`px-4 py-2.5 text-sm border-b-2 transition ${
                  activeRole === role.key
                    ? "border-accent text-ink font-medium"
                    : "border-transparent text-ink-muted hover:text-ink"
                }`}
              >
                {role.label}
              </button>
            ))}
          </div>

          {activeExplanation && (
            <div className="space-y-3">
              {activeRoleMeta && <p className="text-sm text-ink-faint">{activeRoleMeta.description}</p>}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                <Card>
                  <CardHeader title="Strengths" />
                  <ul className="text-sm text-ink-muted space-y-1.5 list-disc list-inside">
                    {activeExplanation.strengths.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </Card>
                <Card>
                  <CardHeader title="Weaknesses" />
                  <ul className="text-sm text-ink-muted space-y-1.5 list-disc list-inside">
                    {activeExplanation.weaknesses.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </Card>
                <Card>
                  <CardHeader title="Recommendations" />
                  <ul className="text-sm text-ink-muted space-y-1.5 list-disc list-inside">
                    {activeExplanation.recommendations.map((s, i) => (
                      <li key={i}>{s}</li>
                    ))}
                  </ul>
                </Card>
              </div>
            </div>
          )}
        </div>
      )}
    </AppShell>
  );
}
