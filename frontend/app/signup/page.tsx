"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/hooks/useAuth";

export default function SignupPage() {
  const { signup, error, loading } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    signup(email, password, name);
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <Card className="w-full max-w-sm">
        <h1 className="font-display text-xl font-medium mb-1">Create your account</h1>
        <p className="text-sm text-ink-muted mb-6">
          Start building your business with an AI CEO assistant.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label block mb-1.5">Name</label>
            <Input required value={name} onChange={(e) => setName(e.target.value)} placeholder="Alex Rivera" />
          </div>
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
            <label className="label block mb-1.5">Password</label>
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
            {loading ? "Creating account…" : "Create account"}
          </Button>
        </form>

        <p className="text-sm text-ink-muted mt-6 text-center">
          Already have an account?{" "}
          <Link href="/login" className="text-accent hover:text-accent-glow">
            Log in
          </Link>
        </p>
      </Card>
    </main>
  );
}
