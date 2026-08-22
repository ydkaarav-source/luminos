"use client";

import { useSearchParams } from "next/navigation";

import { BusinessView } from "@/components/workspace/analytics/BusinessView";
import { PortfolioView } from "@/components/workspace/analytics/PortfolioView";

export function AnalyticsTab() {
  const searchParams = useSearchParams();
  const subtab = searchParams.get("subtab") ?? "business";

  if (subtab === "portfolio") return <PortfolioView />;
  return <BusinessView />;
}
