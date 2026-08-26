"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { apiClient, ApiError } from "@/lib/api-client";
import type { CEOBriefing, GoogleCalendarConnectUrl, GoogleCalendarStatus, UpcomingEvent } from "@/lib/types";

function formatEventTime(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso; // all-day events carry a bare date, not a time
  return d.toLocaleTimeString(undefined, { hour: "numeric", minute: "2-digit" });
}

function CalendarConnection() {
  const searchParams = useSearchParams();

  const [status, setStatus] = useState<GoogleCalendarStatus | null>(null);
  const [events, setEvents] = useState<UpcomingEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [disconnecting, setDisconnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function refresh() {
    return apiClient.get<GoogleCalendarStatus>("/google-calendar/status").then((s) => {
      setStatus(s);
      if (s.connected) {
        return apiClient
          .get<UpcomingEvent[]>("/google-calendar/upcoming-events")
          .then(setEvents)
          .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load upcoming events."));
      }
      setEvents([]);
    });
  }

  useEffect(() => {
    // Land back here after the OAuth redirect completes - show the
    // backend's own honest failure message verbatim, never a generic one.
    if (searchParams.get("calendar") === "error") {
      setError(searchParams.get("message") ?? "Google Calendar connection failed.");
    }
    setLoading(true);
    refresh().finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function connect() {
    setConnecting(true);
    setError(null);
    try {
      const result = await apiClient.get<GoogleCalendarConnectUrl>("/google-calendar/connect");
      window.location.href = result.url;
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong starting Google Calendar Connect.");
      setConnecting(false);
    }
  }

  async function disconnect() {
    setDisconnecting(true);
    setError(null);
    try {
      await apiClient.delete("/google-calendar/disconnect");
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong disconnecting Google Calendar.");
    } finally {
      setDisconnecting(false);
    }
  }

  return (
    <Card className="mb-4">
      <CardHeader
        title="Google Calendar"
        subtitle={
          status?.connected
            ? `Connected as ${status.google_email}`
            : "Connect so CEO Briefing can reference your real schedule - read-only, never modified."
        }
        action={
          status?.connected ? (
            <Button variant="secondary" onClick={disconnect} disabled={disconnecting}>
              {disconnecting ? "Disconnecting…" : "Disconnect"}
            </Button>
          ) : (
            <Button onClick={connect} disabled={connecting || loading}>
              {connecting ? "Redirecting…" : "Connect Google Calendar"}
            </Button>
          )
        }
      />
      {error && <p className="text-sm text-danger mt-2">{error}</p>}
      {status?.connected && !loading && (
        <div className="mt-3">
          {events.length === 0 ? (
            <p className="text-sm text-night-text-muted">Nothing scheduled in the next 7 days.</p>
          ) : (
            <ul className="text-sm text-night-text-muted space-y-1">
              {events.map((e, i) => (
                <li key={i}>
                  <span className="text-night-text">{e.title}</span>
                  {e.start && ` — ${formatEventTime(e.start)}`}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </Card>
  );
}

export function CEOBriefingTab() {
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
    <>
      <h1 className="font-display text-2xl font-medium mb-1">CEO Briefing</h1>
      <p className="text-night-text-muted mb-6">Your daily strategic read, generated each morning.</p>

      <CalendarConnection />

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
    </>
  );
}
