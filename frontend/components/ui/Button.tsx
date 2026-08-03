import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export function Button({ variant = "primary", className = "", ...props }: ButtonProps) {
  const base = variant === "primary" ? "btn-primary" : "btn-secondary";
  return <button className={`${base} ${className}`} {...props} />;
}
