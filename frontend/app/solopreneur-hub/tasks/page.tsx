"use client";

import { FormEvent, useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { useTasks } from "@/hooks/useTasks";
import { apiClient } from "@/lib/api-client";

export default function TasksPage() {
  const { tasks, loading, refresh, completeTask } = useTasks();
  const [title, setTitle] = useState("");
  const [creating, setCreating] = useState(false);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setCreating(true);
    try {
      await apiClient.post("/tasks", { title, priority: "medium" });
      setTitle("");
      await refresh();
    } finally {
      setCreating(false);
    }
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-medium mb-1">Solopreneur Hub — Tasks</h1>
      <p className="text-ink-muted mb-6">Everything you need to move today.</p>

      <Card className="mb-5">
        <form onSubmit={handleCreate} className="flex gap-2">
          <Input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Add a task…"
            className="flex-1"
          />
          <Button type="submit" disabled={creating || !title.trim()}>
            Add
          </Button>
        </form>
      </Card>

      <Card>
        <CardHeader title="Tasks" />
        {loading ? (
          <p className="text-sm text-ink-faint">Loading…</p>
        ) : tasks.length === 0 ? (
          <p className="text-sm text-ink-faint">No tasks yet - add your first one above.</p>
        ) : (
          <ul className="divide-y divide-border-subtle">
            {tasks.map((task) => (
              <li key={task.id} className="flex items-center justify-between py-3">
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    checked={task.status === "done"}
                    onChange={() => task.status !== "done" && completeTask(task.id)}
                    className="h-4 w-4 rounded accent-accent"
                  />
                  <span className={`text-sm ${task.status === "done" ? "line-through text-ink-faint" : "text-ink"}`}>
                    {task.title}
                  </span>
                  {task.source === "ai_generated" && <Badge variant="medium">AI</Badge>}
                </div>
                <Badge
                  variant={task.priority === "high" ? "high" : task.priority === "medium" ? "medium" : "low"}
                >
                  {task.priority}
                </Badge>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </AppShell>
  );
}
