"use client";

import { FormEvent, useEffect, useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { apiClient } from "@/lib/api-client";

interface Goal {
  id: string;
  title: string;
  description: string | null;
  status: "not_started" | "in_progress" | "completed" | "abandoned";
}

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(true);

  function refresh() {
    setLoading(true);
    return apiClient.get<Goal[]>("/goals").then(setGoals).finally(() => setLoading(false));
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    await apiClient.post("/goals", { title });
    setTitle("");
    refresh();
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-medium mb-1">Solopreneur Hub — Goals</h1>
      <p className="text-night-text-muted mb-6">The outcomes you're steering toward.</p>

      <Card className="mb-5">
        <form onSubmit={handleCreate} className="flex gap-2">
          <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Add a goal…" className="flex-1" />
          <Button type="submit" disabled={!title.trim()}>
            Add
          </Button>
        </form>
      </Card>

      <Card>
        <CardHeader title="Goals" />
        {loading ? (
          <p className="text-sm text-night-text-muted">Loading…</p>
        ) : goals.length === 0 ? (
          <p className="text-sm text-night-text-muted">No goals yet.</p>
        ) : (
          <ul className="divide-y divide-night-border">
            {goals.map((g) => (
              <li key={g.id} className="flex items-center justify-between py-3">
                <span className="text-sm text-night-text">{g.title}</span>
                <Badge variant={g.status === "completed" ? "positive" : "medium"}>
                  {g.status.replace("_", " ")}
                </Badge>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </AppShell>
  );
}
