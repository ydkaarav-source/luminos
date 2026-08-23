"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card, CardHeader } from "@/components/ui/Card";
import { apiClient, ApiError } from "@/lib/api-client";
import type { WebsiteBrief, WebsiteScrapeResult } from "@/lib/types";

export function WebsiteBriefTab() {
  const [brief, setBrief] = useState<WebsiteBrief | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [siteUrl, setSiteUrl] = useState("");
  const [checkingSite, setCheckingSite] = useState(false);
  const [scrapeError, setScrapeError] = useState<string | null>(null);
  const [scrapePreview, setScrapePreview] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<WebsiteBrief>("/website-brief/latest")
      .then((result) => {
        setBrief(result);
        if (result.site_url) setSiteUrl(result.site_url);
      })
      .catch((err) => {
        if (!(err instanceof ApiError && err.status === 404)) {
          setError(err instanceof ApiError ? err.message : "Something went wrong loading your website brief.");
        }
      })
      .finally(() => setLoading(false));
  }, []);

  async function generate() {
    setGenerating(true);
    setError(null);
    try {
      const result = await apiClient.post<WebsiteBrief>("/website-brief/generate", {});
      setBrief(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong generating your website brief.");
    } finally {
      setGenerating(false);
    }
  }

  async function checkSite() {
    if (!siteUrl.trim()) return;
    setCheckingSite(true);
    setScrapeError(null);
    setScrapePreview(null);
    try {
      const result = await apiClient.post<WebsiteScrapeResult>("/website-brief/scrape-site", {
        url: siteUrl,
      });
      setBrief(result.brief);
      setScrapePreview(result.content_preview);
    } catch (err) {
      // Show the backend's own honest reason (unreachable, blocked,
      // timed out, not HTML, ...) verbatim - never swap it for a
      // generic message, since the specific reason is useful to a founder.
      setScrapeError(err instanceof ApiError ? err.message : "Something went wrong checking your site.");
    } finally {
      setCheckingSite(false);
    }
  }

  return (
    <>
      <h1 className="font-display text-2xl font-medium mb-1">Website</h1>
      <p className="text-night-text-muted mb-6">
        A recommended page structure and messaging direction for your site - analysis and
        suggestions to hand to a developer or website builder, not a guarantee of results.
      </p>

      {loading ? (
        <p className="text-sm text-night-text-muted">Loading website brief…</p>
      ) : (
        <>
          {!brief && (
            <Card className="mb-6">
              <p className="text-sm text-night-text-muted mb-4">
                No website brief yet. Generate one from your business profile and plan.
              </p>
              <div className="flex justify-end">
                <Button onClick={generate} disabled={generating}>
                  {generating ? "Generating brief…" : "Generate website brief"}
                </Button>
              </div>
            </Card>
          )}

          {error && <p className="text-sm text-danger mb-4">{error}</p>}

          {brief && (
            <div className="space-y-5">
              <Card>
                <CardHeader
                  title={brief.title}
                  subtitle="Website brief"
                  action={
                    <Button onClick={generate} disabled={generating}>
                      {generating ? "Regenerating…" : "Regenerate"}
                    </Button>
                  }
                />
              </Card>

              <Card>
                <CardHeader title="Suggested pages" />
                <div className="space-y-4">
                  {brief.target_pages.map((page, i) => (
                    <div key={i} className="border-l-2 border-accent/40 pl-4">
                      <p className="text-sm font-medium text-night-text">{page.name}</p>
                      <p className="text-sm text-night-text-muted mt-1">{page.purpose}</p>
                    </div>
                  ))}
                </div>
              </Card>

              <Card>
                <CardHeader title="Copy direction" />
                <p className="text-sm text-night-text-muted leading-relaxed">{brief.copy_direction}</p>
              </Card>

              <Card>
                <CardHeader title="Design direction" />
                <p className="text-sm text-night-text-muted leading-relaxed">{brief.design_direction}</p>
              </Card>

              <Card>
                <CardHeader
                  title="Check my site"
                  subtitle="Once your site is live, LuminOS can read its real content so CEO Briefing, Health Score, and the Assistant reflect it - not just what's in your Business Brain."
                />
                <div className="flex flex-col sm:flex-row gap-3">
                  <input
                    value={siteUrl}
                    onChange={(e) => setSiteUrl(e.target.value)}
                    placeholder="https://yourbusiness.com"
                    className="input-field flex-1"
                  />
                  <Button onClick={checkSite} disabled={checkingSite || !siteUrl.trim()}>
                    {checkingSite ? "Checking site…" : "Check my site"}
                  </Button>
                </div>

                {scrapeError && (
                  <div className="rounded-lg border border-danger/30 bg-danger/10 p-4 mt-4">
                    <p className="label mb-1.5 text-danger">Couldn't access this site</p>
                    <p className="text-sm text-night-text leading-relaxed">{scrapeError}</p>
                  </div>
                )}

                {scrapePreview && !scrapeError && (
                  <div className="rounded-lg border border-accent/30 bg-accent/15 p-4 mt-4">
                    <p className="label mb-1.5 text-accent-bright">Found and understood</p>
                    <p className="text-sm text-night-text leading-relaxed">{scrapePreview}</p>
                  </div>
                )}
              </Card>
            </div>
          )}
        </>
      )}
    </>
  );
}
