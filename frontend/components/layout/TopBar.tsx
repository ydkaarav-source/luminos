"use client";

import { useAuth } from "@/hooks/useAuth";

export function TopBar({ businessName }: { businessName?: string }) {
  const { logout } = useAuth();

  return (
    <header className="flex items-center justify-between px-6 md:px-8 py-4 border-b border-border-subtle">
      <div>
        {businessName && <p className="text-sm text-ink-muted">{businessName}</p>}
      </div>
      <button onClick={() => logout()} className="text-sm text-ink-muted hover:text-ink transition">
        Log out
      </button>
    </header>
  );
}
