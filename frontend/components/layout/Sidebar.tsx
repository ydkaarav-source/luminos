"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Logo } from "@/components/ui/Logo";

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
    <aside className="relative z-10 hidden md:flex w-60 shrink-0 flex-col border-r border-night-border px-4 py-6">
      <div className="px-2 mb-8">
        <Logo className="text-lg" variant="dark" />
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
                  ? "bg-accent/15 text-accent-bright font-medium"
                  : "text-night-text-muted hover:text-night-text hover:bg-night-card"
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
