"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { apiClient, ApiError } from "@/lib/api-client";
import type { User } from "@/lib/types";

export function useAuth() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function signup(email: string, password: string, name: string) {
    setLoading(true);
    setError(null);
    try {
      const user = await apiClient.post<User>("/auth/signup", { email, password, name });
      router.push(user.onboarding_completed ? "/dashboard" : "/onboarding");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  async function login(email: string, password: string) {
    setLoading(true);
    setError(null);
    try {
      const user = await apiClient.post<User>("/auth/login", { email, password });
      router.push(user.onboarding_completed ? "/dashboard" : "/onboarding");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    await apiClient.post("/auth/logout");
    router.push("/login");
  }

  return { signup, login, logout, error, loading };
}
