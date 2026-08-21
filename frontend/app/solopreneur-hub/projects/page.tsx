"use client";

import { FormEvent, useEffect, useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { apiClient } from "@/lib/api-client";

interface Project {
  id: string;
  name: string;
  description: string | null;
  status: "active" | "archived" | "completed";
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(true);

  function refresh() {
    setLoading(true);
    return apiClient.get<Project[]>("/projects").then(setProjects).finally(() => setLoading(false));
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    await apiClient.post("/projects", { name });
    setName("");
    refresh();
  }

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-medium mb-1">Solopreneur Hub — Projects</h1>
      <p className="text-night-text-muted mb-6">Group related tasks under a project.</p>

      <Card className="mb-5">
        <form onSubmit={handleCreate} className="flex gap-2">
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Add a project…" className="flex-1" />
          <Button type="submit" disabled={!name.trim()}>
            Add
          </Button>
        </form>
      </Card>

      <Card>
        <CardHeader title="Projects" />
        {loading ? (
          <p className="text-sm text-night-text-muted">Loading…</p>
        ) : projects.length === 0 ? (
          <p className="text-sm text-night-text-muted">No projects yet.</p>
        ) : (
          <ul className="divide-y divide-night-border">
            {projects.map((p) => (
              <li key={p.id} className="flex items-center justify-between py-3">
                <span className="text-sm text-night-text">{p.name}</span>
                <Badge variant={p.status === "completed" ? "positive" : "medium"}>{p.status}</Badge>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </AppShell>
  );
}
