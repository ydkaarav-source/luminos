"use client";

import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { apiClient, ApiError } from "@/lib/api-client";
import type { RevenueEntry, StripeConnectUrl, StripeStatus, StripeSyncResult } from "@/lib/types";

export function RevenueTab() {
  const searchParams = useSearchParams();

  const [status, setStatus] = useState<StripeStatus | null>(null);
  const [entries, setEntries] = useState<RevenueEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<StripeSyncResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Set when a sync fails while status still says "connected" - the
  // stored connection may be broken (token revoked externally, etc).
  // Re-running Connect Stripe re-authorizes and overwrites the stored
  // connection for this business, so it doubles as "Reconnect."
  const [syncFailed, setSyncFailed] = useState(false);

  const [amount, setAmount] = useState("");
  const [source, setSource] = useState("");

  function refresh() {
    return Promise.all([
      apiClient.get<StripeStatus>("/stripe/status"),
      apiClient.get<RevenueEntry[]>("/revenue"),
    ]).then(([s, e]) => {
      setStatus(s);
      setEntries(e);
    });
  }

  useEffect(() => {
    // Land back here after the OAuth redirect completes - show the
    // backend's own honest failure message verbatim, never a generic one.
    if (searchParams.get("stripe") === "error") {
      setError(searchParams.get("message") ?? "Stripe connection failed.");
    }
    setLoading(true);
    refresh()
      .catch((err) => setError(err instanceof ApiError ? err.message : "Something went wrong loading revenue."))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function connectStripe() {
    setConnecting(true);
    setError(null);
    try {
      const result = await apiClient.get<StripeConnectUrl>("/stripe/connect");
      window.location.href = result.url;
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong starting Stripe Connect.");
      setConnecting(false);
    }
  }

  async function syncNow() {
    setSyncing(true);
    setError(null);
    setSyncResult(null);
    setSyncFailed(false);
    try {
      const result = await apiClient.post<StripeSyncResult>("/stripe/sync", {});
      setSyncResult(result);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong syncing from Stripe.");
      setSyncFailed(true);
    } finally {
      setSyncing(false);
    }
  }

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
    <>
      <h1 className="font-display text-2xl font-medium mb-1">Revenue</h1>
      <p className="text-night-text-muted mb-6">
        Connect Stripe to pull in real transactions automatically, or log revenue manually.
      </p>

      <Card className="mb-5">
        <CardHeader
          title="Stripe"
          subtitle={
            status?.connected && status.connected_at
              ? `Connected ${new Date(status.connected_at).toLocaleDateString()}`
              : "Not connected"
          }
          action={
            status?.connected ? (
              <Button onClick={syncNow} disabled={syncing}>
                {syncing ? "Syncing…" : "Sync now"}
              </Button>
            ) : (
              <Button onClick={connectStripe} disabled={connecting || loading}>
                {connecting ? "Redirecting…" : "Connect Stripe"}
              </Button>
            )
          }
        />
        {!loading && !status?.connected && (
          <div className="mt-3">
            <p className="text-sm text-night-text-muted">
              Don&apos;t have Stripe yet? You don&apos;t need to sign up first - clicking Connect
              Stripe above lets you create a free account on the spot, right through Stripe&apos;s
              own sign-up flow.
            </p>
            <p className="text-sm text-night-text-muted mt-2">
              Prefer to create your account separately first? Visit{" "}
              <a
                href="https://dashboard.stripe.com/register"
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent-bright underline"
              >
                dashboard.stripe.com/register
              </a>{" "}
              (opens in a new tab), then come back and click Connect Stripe.
            </p>
          </div>
        )}
        {syncResult && (
          <p className="text-sm text-night-text-muted">
            Synced {syncResult.synced_count} new transaction{syncResult.synced_count === 1 ? "" : "s"} (
            {syncResult.total_fetched} checked).
          </p>
        )}
        {error && <p className="text-sm text-danger mt-3">{error}</p>}
        {syncFailed && (
          <div className="mt-3">
            <p className="text-sm text-night-text-muted mb-2">
              If Stripe access was revoked or expired, reconnecting will fix this.
            </p>
            <Button onClick={connectStripe} disabled={connecting}>
              {connecting ? "Redirecting…" : "Reconnect Stripe"}
            </Button>
          </div>
        )}
      </Card>

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
          <p className="text-sm text-night-text-muted">Loading…</p>
        ) : entries.length === 0 ? (
          <p className="text-sm text-night-text-muted">No revenue logged yet.</p>
        ) : (
          <ul className="divide-y divide-night-border">
            {entries.map((e) => (
              <li key={e.id} className="flex items-center justify-between py-3 text-sm">
                <span className="flex items-center gap-2">
                  <span className="text-night-text-muted">{e.source ?? "Untitled"}</span>
                  <Badge variant={e.origin}>{e.origin === "stripe" ? "Stripe" : "Manual"}</Badge>
                </span>
                <span className="text-night-text font-medium">
                  ${Number(e.amount).toFixed(2)} · {new Date(e.entry_date).toLocaleDateString()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </>
  );
}
