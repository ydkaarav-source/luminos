"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

const TABS = [
  { value: "dashboard", label: "Dashboard" },
  { value: "business-builder", label: "Business Builder" },
  { value: "ceo-briefing", label: "CEO Briefing" },
  { value: "health-score", label: "Health Score" },
  { value: "solopreneur-hub", label: "Solopreneur Hub" },
  { value: "analytics", label: "Analytics" },
  { value: "assistant", label: "AI Assistant" },
];

export function WorkspaceTabs() {
  const searchParams = useSearchParams();
  const active = searchParams.get("tab") ?? "dashboard";

  return (
    <div className="flex flex-wrap gap-1 border-b border-night-border mb-6">
      {TABS.map((tab) => (
        <Link
          key={tab.value}
          href={`/workspace?tab=${tab.value}`}
          className={`px-4 py-2.5 text-sm border-b-2 transition whitespace-nowrap ${
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
