"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api-client";
import type { HealthScore } from "@/lib/types";

export function useHealthScore() {
  const [score, setScore] = useState<HealthScore | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get<HealthScore | null>("/health-score/latest")
      .then(setScore)
      .finally(() => setLoading(false));
  }, []);

  return { score, loading };
}
