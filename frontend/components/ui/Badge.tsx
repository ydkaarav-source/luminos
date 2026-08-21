const VARIANTS = {
  low: "bg-panel-raised text-ink-muted",
  medium: "bg-accent-soft text-accent-glow",
  high: "bg-warning-soft text-warning",
  positive: "bg-positive-soft text-positive",
  demo: "bg-transparent border border-border text-ink-muted",
  fact: "bg-panel-raised text-ink-muted",
  decision: "bg-accent-soft text-accent-glow",
  preference: "bg-transparent border border-border text-ink-muted",
  completed_milestone: "bg-positive-soft text-positive",
  note: "bg-panel-raised text-ink-muted",
};

export function Badge({
  children,
  variant = "medium",
}: {
  children: React.ReactNode;
  variant?: keyof typeof VARIANTS;
}) {
  return (
    <span className={`inline-flex items-center rounded-pill px-2.5 py-1 text-xs font-medium ${VARIANTS[variant]}`}>
      {children}
    </span>
  );
}
