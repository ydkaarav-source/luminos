"use client";

import { useEffect, useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { apiClient } from "@/lib/api-client";
import type { Business, User } from "@/lib/types";

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null);
  const [business, setBusiness] = useState<Business | null>(null);
  const [name, setName] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    apiClient.get<User>("/auth/me").then(setUser);
    apiClient.get<Business>("/businesses/active").then((b) => {
      setBusiness(b);
      setName(b.name);
    });
  }, []);

  async function save() {
    setSaving(true);
    try {
      const updated = await apiClient.patch<Business>("/businesses/active", { name });
      setBusiness(updated);
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell businessName={business?.name}>
      <h1 className="font-display text-2xl font-medium mb-6">Settings</h1>

      <div className="space-y-5 max-w-lg">
        <Card>
          <CardHeader title="Account" />
          <div className="space-y-1 text-sm">
            <p className="text-ink-muted">Name: <span className="text-ink">{user?.name}</span></p>
            <p className="text-ink-muted">Email: <span className="text-ink">{user?.email}</span></p>
          </div>
        </Card>

        <Card>
          <CardHeader title="Business" subtitle="Update your business name" />
          <div className="flex gap-2">
            <Input value={name} onChange={(e) => setName(e.target.value)} />
            <Button onClick={save} disabled={saving}>
              {saving ? "Saving…" : "Save"}
            </Button>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
