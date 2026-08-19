export function Logo({
  className = "",
  variant = "light",
}: {
  className?: string;
  variant?: "light" | "dark";
}) {
  const inkClass = variant === "dark" ? "text-night-text" : "text-ink";
  const accentClass = variant === "dark" ? "text-accent-bright" : "text-accent";

  return (
    <span className={`font-serif font-medium tracking-tight ${className}`}>
      <span className={inkClass}>Lumin</span>
      <span className={accentClass}>OS</span>
    </span>
  );
}
