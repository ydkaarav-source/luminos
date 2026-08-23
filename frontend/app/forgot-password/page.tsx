"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { apiClient, ApiError } from "@/lib/api-client";
import type { ForgotPasswordResponse } from "@/lib/types";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ForgotPasswordResponse | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.post<ForgotPasswordResponse>("/auth/forgot-password", { email });
      setResult(response);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <Card className="w-full max-w-sm">
        <h1 className="font-display text-xl font-medium mb-1">Reset your password</h1>
        <p className="text-sm text-ink-muted mb-6">
          Enter your email and we&apos;ll send you a link to reset your password.
        </p>

        {result ? (
          <div className="space-y-4">
            <p className="text-sm text-ink-muted">{result.message}</p>
            {result.reset_url && (
              <div className="rounded-lg border border-accent/30 bg-accent/10 p-3">
                <p className="text-xs text-ink-muted mb-1">
                  Local dev only - no email sending is configured yet:
                </p>
                <a href={result.reset_url} className="text-xs text-accent hover:text-accent-glow break-all">
                  {result.reset_url}
                </a>
              </div>
            )}
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="label block mb-1.5">Email</label>
              <Input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@business.com"
              />
            </div>

            {error && <p className="text-sm text-danger">{error}</p>}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Sending…" : "Send reset link"}
            </Button>
          </form>
        )}

        <p className="text-sm text-ink-muted mt-6 text-center">
          <Link href="/login" className="text-accent hover:text-accent-glow">
            Back to log in
          </Link>
        </p>
      </Card>
    </main>
  );
}
