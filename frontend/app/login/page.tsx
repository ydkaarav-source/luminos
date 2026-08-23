"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { login, error, loading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    login(email, password);
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <Card className="w-full max-w-sm">
        <h1 className="font-display text-xl font-medium mb-1">Welcome back</h1>
        <p className="text-sm text-ink-muted mb-6">Log in to your LuminOS command center.</p>

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
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="label">Password</label>
              <Link href="/forgot-password" className="text-xs text-accent hover:text-accent-glow">
                Forgot password?
              </Link>
            </div>
            <Input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>

          {error && <p className="text-sm text-danger">{error}</p>}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading ? "Logging in…" : "Log in"}
          </Button>
        </form>

        <p className="text-sm text-ink-muted mt-6 text-center">
          New to LuminOS?{" "}
          <Link href="/signup" className="text-accent hover:text-accent-glow">
            Create an account
          </Link>
        </p>
      </Card>
    </main>
  );
}
