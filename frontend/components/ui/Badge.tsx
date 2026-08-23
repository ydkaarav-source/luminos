const VARIANTS = {
  low: "bg-night-border text-night-text-muted",
  medium: "bg-accent/15 text-accent-bright",
  high: "bg-warning/15 text-warning",
  positive: "bg-positive/15 text-positive",
  demo: "bg-transparent border border-night-border text-night-text-muted",
  fact: "bg-night-border text-night-text-muted",
  decision: "bg-accent/15 text-accent-bright",
  preference: "bg-transparent border border-night-border text-night-text-muted",
  completed_milestone: "bg-positive/15 text-positive",
  note: "bg-night-border text-night-text-muted",
  manual: "bg-night-border text-night-text-muted",
  stripe: "bg-positive/15 text-positive",
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
