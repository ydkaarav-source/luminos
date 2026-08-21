"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/analytics/business", label: "Business" },
  { href: "/analytics/portfolio", label: "Portfolio" },
];

export function AnalyticsTabs() {
  const pathname = usePathname();

  return (
    <div className="flex gap-1 border-b border-night-border mb-6">
      {TABS.map((tab) => {
        const active = pathname.startsWith(tab.href);
        return (
          <Link
            key={tab.href}
            href={tab.href}
            className={`px-4 py-2.5 text-sm border-b-2 transition ${
              active
                ? "border-accent-bright text-night-text font-medium"
                : "border-transparent text-night-text-muted hover:text-night-text"
            }`}
          >
            {tab.label}
          </Link>
        );
      })}
    </div>
  );
}