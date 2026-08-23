"use client";

import { useSearchParams } from "next/navigation";

import { AppShell } from "@/components/layout/AppShell";
import { AnalyticsTab } from "@/components/workspace/AnalyticsTab";
import { AssistantTab } from "@/components/workspace/AssistantTab";
import { BusinessBuilderTab } from "@/components/workspace/BusinessBuilderTab";
import { CEOBriefingTab } from "@/components/workspace/CEOBriefingTab";
import { DashboardTab } from "@/components/workspace/DashboardTab";
import { HealthScoreTab } from "@/components/workspace/HealthScoreTab";
import { RevenueTab } from "@/components/workspace/RevenueTab";
import { SolopreneurHubTab } from "@/components/workspace/SolopreneurHubTab";
import { WebsiteBriefTab } from "@/components/workspace/WebsiteBriefTab";
import { WorkspaceTabs } from "@/components/workspace/WorkspaceTabs";
import { useBusiness } from "@/hooks/useBusiness";

function TabContent({ tab }: { tab: string }) {
  switch (tab) {
    case "business-builder":
      return <BusinessBuilderTab />;
    case "website":
      return <WebsiteBriefTab />;
    case "ceo-briefing":
      return <CEOBriefingTab />;
    case "health-score":
      return <HealthScoreTab />;
    case "solopreneur-hub":
      return <SolopreneurHubTab />;
    case "analytics":
      return <AnalyticsTab />;
    case "revenue":
      return <RevenueTab />;
    case "assistant":
      return <AssistantTab />;
    default:
      return <DashboardTab />;
  }
}

export function WorkspaceContent() {
  const searchParams = useSearchParams();
  const tab = searchParams.get("tab") ?? "dashboard";
  // Only the dashboard tab ever passed businessName to AppShell before this
  // restructure (every other old page rendered <AppShell> with no prop) -
  // preserved here rather than showing it on every tab, which would be a
  // display change beyond the routing restructure.
  const { business } = useBusiness();

  return (
    <AppShell businessName={tab === "dashboard" ? business?.name : undefined}>
      <WorkspaceTabs />
      <TabContent tab={tab} />
    </AppShell>
  );
}
