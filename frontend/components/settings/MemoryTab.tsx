"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { apiClient } from "@/lib/api-client";
import type { MemoryRecord } from "@/lib/types";

function formatLabel(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1).replace(/_/g, " ");
}

export function MemoryTab() {
  const [records, setRecords] = useState<MemoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editContent, setEditContent] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    apiClient
      .get<MemoryRecord[]>("/memory")
      .then(setRecords)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  function startEdit(record: MemoryRecord) {
    setEditingId(record.id);
    setEditContent(record.content);
  }

  function cancelEdit() {
    setEditingId(null);
    setEditContent("");
  }

  async function saveEdit(id: string) {
    setSaving(true);
    try {
      const updated = await apiClient.patch<MemoryRecord>(`/memory/${id}`, {
        content: editContent,
      });
      setRecords((prev) => prev.map((r) => (r.id === id ? updated : r)));
      cancelEdit();
    } finally {
      setSaving(false);
    }
  }

  async function deleteRecord(id: string) {
    if (!window.confirm("Delete this memory? The AI will no longer use it as context.")) return;
    await apiClient.delete(`/memory/${id}`);
    setRecords((prev) => prev.filter((r) => r.id !== id));
  }

  return (
    <Card>
      <CardHeader
        title="Memory"
        subtitle="What LuminOS remembers about your business - used by the Assistant, CEO Briefing, Business Builder, and Health Score."
      />
      {loading ? (
        <p className="text-sm text-ink-faint">Loading…</p>
      ) : records.length === 0 ? (
        <p className="text-sm text-ink-faint">
          No memory yet - as you use the Assistant, Business Builder, and onboarding, LuminOS
          will remember key facts, decisions, and preferences here.
        </p>
      ) : (
        <ul className="divide-y divide-border-subtle">
          {records.map((record) => (
            <li key={record.id} className="py-3">
              <div className="flex items-center gap-2 mb-2">
                <Badge variant={record.memory_type}>{formatLabel(record.memory_type)}</Badge>
                <span className="text-xs text-ink-faint">{formatLabel(record.source)}</span>
              </div>
              {editingId === record.id ? (
                <div className="space-y-2">
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="input-field w-full min-h-[80px]"
                  />
                  <div className="flex gap-2">
                    <Button onClick={() => saveEdit(record.id)} disabled={saving || !editContent.trim()}>
                      {saving ? "Saving…" : "Save"}
                    </Button>
                    <Button variant="secondary" onClick={cancelEdit} disabled={saving}>
                      Cancel
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm text-ink flex-1">{record.content}</p>
                  <div className="flex gap-2 shrink-0">
                    <button
                      onClick={() => startEdit(record)}
                      className="text-xs text-accent hover:text-accent-glow"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => deleteRecord(record.id)}
                      className="text-xs text-ink-faint hover:text-warning"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
