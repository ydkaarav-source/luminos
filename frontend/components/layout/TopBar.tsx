"use client";

import { useAuth } from "@/hooks/useAuth";

export function TopBar({ businessName }: { businessName?: string }) {
  const { logout } = useAuth();

  return (
    <header className="flex items-center justify-between px-6 md:px-8 py-4 border-b border-night-border">
      <div>
        {businessName && <p className="text-sm text-night-text-muted">{businessName}</p>}
      </div>
      <button onClick={() => logout()} className="text-sm text-night-text-muted hover:text-night-text transition">
        Log out
      </button>
    </header>
  );
}
