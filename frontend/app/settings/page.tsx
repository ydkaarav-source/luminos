"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { MemoryTab } from "@/components/settings/MemoryTab";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { apiClient, ApiError } from "@/lib/api-client";
import type { Business, User } from "@/lib/types";

const TABS = [
  { id: "account", label: "Account" },
  { id: "memory", label: "Memory" },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function SettingsPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [business, setBusiness] = useState<Business | null>(null);
  const [name, setName] = useState("");
  const [saving, setSaving] = useState(false);
  const [tab, setTab] = useState<TabId>("account");

  const [deletePassword, setDeletePassword] = useState("");
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

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

  async function deleteAccount() {
    if (
      !window.confirm(
        "This permanently deletes your account, your business, and all its data. This cannot be undone. Continue?"
      )
    ) {
      return;
    }
    setDeleting(true);
    setDeleteError(null);
    try {
      await apiClient.delete("/businesses/active/delete-account", { password: deletePassword });
      router.push("/");
    } catch (err) {
      setDeleteError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setDeleting(false);
    }
  }

  return (
    <AppShell businessName={business?.name}>
      <h1 className="font-display text-2xl font-medium mb-6">Settings</h1>

      <div className="flex gap-1 border-b border-night-border mb-6">
        {TABS.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2.5 text-sm border-b-2 transition ${
              tab === t.id
                ? "border-accent-bright text-night-text font-medium"
                : "border-transparent text-night-text-muted hover:text-night-text"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "account" ? (
        <div className="space-y-5 max-w-lg">
          <Card>
            <CardHeader title="Account" />
            <div className="space-y-1 text-sm">
              <p className="text-night-text-muted">Name: <span className="text-night-text">{user?.name}</span></p>
              <p className="text-night-text-muted">Email: <span className="text-night-text">{user?.email}</span></p>
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

          <Card className="border-danger/40 bg-danger/5">
            <CardHeader
              title="Delete account"
              subtitle="Permanently deletes your account, your business, and all associated data - tasks, revenue, memory, connected Stripe accounts, everything. This cannot be undone."
            />
            <div className="space-y-3">
              <div>
                <label className="label block mb-1.5">Confirm your password</label>
                <Input
                  type="password"
                  value={deletePassword}
                  onChange={(e) => setDeletePassword(e.target.value)}
                  placeholder="Current password"
                />
              </div>
              {deleteError && <p className="text-sm text-danger">{deleteError}</p>}
              <Button
                variant="secondary"
                className="border-danger text-danger hover:bg-danger/10"
                onClick={deleteAccount}
                disabled={deleting || !deletePassword}
              >
                {deleting ? "Deleting…" : "Delete my account"}
              </Button>
            </div>
          </Card>
        </div>
      ) : (
        <div className="max-w-lg">
          <MemoryTab />
        </div>
      )}
    </AppShell>
  );
}
