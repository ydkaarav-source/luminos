"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { Card, CardHeader } from "@/components/ui/Card";
import { apiClient } from "@/lib/api-client";
import type { CEOBriefing } from "@/lib/types";

export default function CEOBriefingPage() {
  const [today, setToday] = useState<CEOBriefing | null>(null);
  const [history, setHistory] = useState<CEOBriefing[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiClient.get<CEOBriefing>("/ceo-briefing/today"),
      apiClient.get<CEOBriefing[]>("/ceo-briefing/history"),
    ])
      .then(([t, h]) => {
        setToday(t);
        setHistory(h.filter((b) => b.id !== t.id));
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-medium mb-1">CEO Briefing</h1>
      <p className="text-night-text-muted mb-6">Your daily strategic read, generated each morning.</p>

      {loading ? (
        <p className="text-sm text-night-text-muted">Loading briefing…</p>
      ) : (
        <div className="space-y-4">
          {today && (
            <Card className="border-accent/30">
              <CardHeader
                title={today.finding}
                subtitle="Today"
                action={
                  <div className="flex items-center gap-2">
                    {today.is_demo && <Badge variant="demo">Demo</Badge>}
                    <Badge variant={today.confidence}>{today.confidence} confidence</Badge>
                  </div>
                }
              />
              {today.why.length > 0 && (
                <ul className="text-sm text-night-text-muted space-y-1.5 list-disc list-inside mb-4">
                  {today.why.map((w, i) => (
                    <li key={i}>{w}</li>
                  ))}
                </ul>
              )}
              <div className="rounded-lg border border-accent/30 bg-accent/15 p-4">
                <p className="label mb-1.5 text-accent-bright">Recommendation</p>
                <p className="text-sm text-night-text leading-relaxed">{today.recommendation}</p>
              </div>
            </Card>
          )}

          {history.length > 0 && (
            <div>
              <p className="label mb-3">Previous briefings</p>
              <div className="space-y-3">
                {history.map((b) => (
                  <Card key={b.id}>
                    <CardHeader
                      title={b.finding}
                      subtitle={new Date(b.generated_at).toLocaleDateString()}
                      action={<Badge variant={b.confidence}>{b.confidence}</Badge>}
                    />
                    {b.why.length > 0 && (
                      <ul className="text-sm text-night-text-muted space-y-1.5 list-disc list-inside mb-4">
                        {b.why.map((w, i) => (
                          <li key={i}>{w}</li>
                        ))}
                      </ul>
                    )}
                    <div className="rounded-lg border border-accent/30 bg-accent/15 p-4">
                      <p className="label mb-1.5 text-accent-bright">Recommendation</p>
                      <p className="text-sm text-night-text leading-relaxed">{b.recommendation}</p>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </AppShell>
  );
}
