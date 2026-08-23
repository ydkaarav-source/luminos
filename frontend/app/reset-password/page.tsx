"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { apiClient, ApiError } from "@/lib/api-client";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await apiClient.post("/auth/reset-password", { token, new_password: password });
      router.push("/login");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="w-full max-w-sm">
      <h1 className="font-display text-xl font-medium mb-1">Set a new password</h1>
      <p className="text-sm text-ink-muted mb-6">Choose a new password for your account.</p>

      {!token ? (
        <p className="text-sm text-danger">
          This reset link is missing its token. Request a new one from{" "}
          <Link href="/forgot-password" className="text-accent hover:text-accent-glow">
            here
          </Link>
          .
        </p>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label block mb-1.5">New password</label>
            <Input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="At least 8 characters"
            />
          </div>

          {error && <p className="text-sm text-danger">{error}</p>}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Resetting…" : "Reset password"}
          </Button>
        </form>
      )}

      <p className="text-sm text-ink-muted mt-6 text-center">
        <Link href="/login" className="text-accent hover:text-accent-glow">
          Back to log in
        </Link>
      </p>
    </Card>
  );
}

export default function ResetPasswordPage() {
  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <Suspense>
        <ResetPasswordForm />
      </Suspense>
    </main>
  );
}
