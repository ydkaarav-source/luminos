"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

const TABS = [
  { value: "tasks", label: "Tasks" },
  { value: "goals", label: "Goals" },
  { value: "projects", label: "Projects" },
  { value: "revenue", label: "Revenue" },
];

export function SolopreneurHubTabs() {
  const searchParams = useSearchParams();
  const active = searchParams.get("subtab") ?? "tasks";

  return (
    <div className="flex gap-1 border-b border-night-border mb-6">
      {TABS.map((tab) => (
        <Link
          key={tab.value}
          href={`/workspace?tab=solopreneur-hub&subtab=${tab.value}`}
          className={`px-4 py-2.5 text-sm border-b-2 transition ${
            active === tab.value
              ? "border-accent-bright text-night-text font-medium"
              : "border-transparent text-night-text-muted hover:text-night-text"
          }`}
        >
          {tab.label}
        </Link>
      ))}
    </div>
  );
}
