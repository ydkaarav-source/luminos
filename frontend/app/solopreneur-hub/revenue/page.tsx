"use client";

import { FormEvent, useEffect, useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { apiClient } from "@/lib/api-client";

interface RevenueEntry {
  id: string;
  amount: number;
  currency: string;
  source: string | null;
  entry_date: string;
}

export default function RevenuePage() {
  const [entries, setEntries] = useState<RevenueEntry[]>([]);
  const [amount, setAmount] = useState("");
  const [source, setSource] = useState("");
  const [loading, setLoading] = useState(true);

  function refresh() {
    setLoading(true);
    return apiClient.get<RevenueEntry[]>("/revenue").then(setEntries).finally(() => setLoading(false));
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    if (!amount) return;
    await apiClient.post("/revenue", {
      amount: Number(amount),
      source,
      entry_date: new Date().toISOString().slice(0, 10),
    });
    setAmount("");
    setSource("");
    refresh();
  }

  const total = entries.reduce((sum, e) => sum + Number(e.amount), 0);

  return (
    <AppShell>
      <h1 className="font-display text-2xl font-medium mb-1">Solopreneur Hub — Revenue</h1>
      <p className="text-ink-muted mb-6">Log revenue to keep your Health Score current.</p>

      <Card className="mb-5">
        <form onSubmit={handleCreate} className="flex gap-2">
          <Input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="Amount"
            className="w-32"
          />
          <Input
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="Source (e.g. client retainer)"
            className="flex-1"
          />
          <Button type="submit" disabled={!amount}>
            Log
          </Button>
        </form>
      </Card>

      <Card>
        <CardHeader title="Revenue entries" subtitle={`Total logged: $${total.toFixed(2)}`} />
        {loading ? (
          <p className="text-sm text-ink-faint">Loading…</p>
        ) : entries.length === 0 ? (
          <p className="text-sm text-ink-faint">No revenue logged yet.</p>
        ) : (
          <ul className="divide-y divide-border-subtle">
            {entries.map((e) => (
              <li key={e.id} className="flex items-center justify-between py-3 text-sm">
                <span className="text-ink-muted">{e.source ?? "Untitled"}</span>
                <span className="text-ink font-medium">
                  ${Number(e.amount).toFixed(2)} · {new Date(e.entry_date).toLocaleDateString()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </AppShell>
  );
}
