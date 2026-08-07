"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/business-builder", label: "Business Builder" },
  { href: "/ceo-briefing", label: "CEO Briefing" },
  { href: "/health-score", label: "Health Score" },
  { href: "/solopreneur-hub/tasks", label: "Solopreneur Hub" },
  { href: "/analytics/business", label: "Analytics" },
  { href: "/assistant", label: "AI Assistant" },
  { href: "/settings", label: "Settings" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex w-60 shrink-0 flex-col border-r border-border-subtle px-4 py-6">
      <div className="px-2 mb-8">
        <span className="font-display text-lg font-medium tracking-tight">LuminOS</span>
      </div>
      <nav className="flex flex-col gap-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`rounded-lg px-3 py-2 text-sm transition ${
                active
                  ? "bg-accent-soft text-accent-glow font-medium"
                  : "text-ink-muted hover:text-ink hover:bg-panel-raised"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
