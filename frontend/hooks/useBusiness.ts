"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import type { Business } from "@/lib/types";

export function useBusiness() {
  const [business, setBusiness] = useState<Business | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get<Business>("/businesses/active")
      .then(setBusiness)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return { business, loading };
}
