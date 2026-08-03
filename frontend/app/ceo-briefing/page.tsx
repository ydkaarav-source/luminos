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
      <p className="text-ink-muted mb-6">Your daily strategic read, generated each morning.</p>

      {loading ? (
        <p className="text-sm text-ink-faint">Loading briefing…</p>
      ) : (
        <div className="space-y-4">
          {today && (
            <Card className="border-accent/30">
              <CardHeader
                title={today.title}
                subtitle="Today"
                action={<Badge variant={today.priority}>{today.priority} priority</Badge>}
              />
              <p className="text-sm text-ink-muted leading-relaxed">{today.body}</p>
            </Card>
          )}

          {history.length > 0 && (
            <div>
              <p className="label mb-3">Previous briefings</p>
              <div className="space-y-3">
                {history.map((b) => (
                  <Card key={b.id}>
                    <CardHeader
                      title={b.title}
                      subtitle={new Date(b.generated_at).toLocaleDateString()}
                      action={<Badge variant={b.priority}>{b.priority}</Badge>}
                    />
                    <p className="text-sm text-ink-muted leading-relaxed">{b.body}</p>
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
