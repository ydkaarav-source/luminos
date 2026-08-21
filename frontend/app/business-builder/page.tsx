"use client";

import { useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { apiClient, ApiError } from "@/lib/api-client";
import type { BusinessPlan } from "@/lib/types";

export default function BusinessBuilderPage() {
  const [idea, setIdea] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [plan, setPlan] = useState<BusinessPlan | null>(null);

  async function generate() {
    if (!idea.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.post<BusinessPlan>("/business-builder/generate", {
        idea_description: idea,
      });
      setPlan(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong generating your plan.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-medium mb-1">Business Builder</h1>
      <p className="text-night-text-muted mb-6">
        Describe your idea. LuminOS will map the customer, the model, and a 90-day roadmap -
        analysis and recommendations, not guarantees.
      </p>

      <Card className="mb-6">
        <textarea
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          rows={3}
          placeholder="e.g. I want to start an AI marketing agency for local service businesses."
          className="input-field resize-none"
        />
        <div className="flex justify-end mt-4">
          <Button onClick={generate} disabled={loading || !idea.trim()}>
            {loading ? "Generating plan…" : "Generate business plan"}
          </Button>
        </div>
        {error && <p className="text-sm text-danger mt-3">{error}</p>}
      </Card>

      {plan && (
        <div className="space-y-5">
          <Card>
            <CardHeader title={plan.title} subtitle="Business overview" />
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              {Object.entries(plan.overview).map(([key, value]) => (
                <div key={key}>
                  <dt className="label mb-1">{key.replace(/_/g, " ")}</dt>
                  <dd className="text-night-text-muted">{value}</dd>
                </div>
              ))}
            </dl>
          </Card>

          <Card>
            <CardHeader title="Launch roadmap" subtitle="First 90 days" />
            <div className="space-y-4">
              {plan.roadmap.map((month) => (
                <div key={month.month} className="border-l-2 border-accent/40 pl-4">
                  <p className="text-sm font-medium text-night-text">
                    Month {month.month}: {month.focus}
                  </p>
                  <ul className="text-sm text-night-text-muted list-disc list-inside mt-1 space-y-0.5">
                    {month.milestones.map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </Card>

          <Card>
            <CardHeader title="Action plan" />
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 text-sm">
              <div>
                <p className="label mb-2">Daily tasks</p>
                <ul className="text-night-text-muted space-y-1 list-disc list-inside">
                  {plan.action_plan.daily_tasks.map((t, i) => (
                    <li key={i}>{t}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="label mb-2">Weekly goals</p>
                <ul className="text-night-text-muted space-y-1 list-disc list-inside">
                  {plan.action_plan.weekly_goals.map((t, i) => (
                    <li key={i}>{t}</li>
                  ))}
                </ul>
              </div>
              <div>
                <p className="label mb-2">Milestones</p>
                <ul className="text-night-text-muted space-y-1 list-disc list-inside">
                  {plan.action_plan.milestones.map((t, i) => (
                    <li key={i}>{t}</li>
                  ))}
                </ul>
              </div>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  );
}
