"use client";

import { useSearchParams } from "next/navigation";

import { GoalsView } from "@/components/workspace/solopreneur-hub/GoalsView";
import { ProjectsView } from "@/components/workspace/solopreneur-hub/ProjectsView";
import { RevenueView } from "@/components/workspace/solopreneur-hub/RevenueView";
import { TasksView } from "@/components/workspace/solopreneur-hub/TasksView";

export function SolopreneurHubTab() {
  const searchParams = useSearchParams();
  const subtab = searchParams.get("subtab") ?? "tasks";

  if (subtab === "goals") return <GoalsView />;
  if (subtab === "projects") return <ProjectsView />;
  if (subtab === "revenue") return <RevenueView />;
  return <TasksView />;
}
