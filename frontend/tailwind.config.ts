import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#EEF5EF",
        panel: "#FFFFFF",
        "panel-raised": "#DFEEE2",
        border: {
          DEFAULT: "#C8DFCC",
          subtle: "#D8E8DB",
        },
        ink: {
          DEFAULT: "#0B1810",
          muted: "#3E5745",
          faint: "#6B8570",
        },
        accent: {
          DEFAULT: "#16A34A",
          soft: "#DCF3E3",
          glow: "#22C55E",
          bright: "#4ADE80",
        },
        night: {
          DEFAULT: "#0A0F0C",
          card: "#101B13",
          border: "#1E2E22",
          text: "#FAFAFA",
          "text-muted": "#A8BFA9",
        },
        positive: {
          DEFAULT: "#15803D",
          soft: "#D7EEDD",
        },
        warning: {
          DEFAULT: "#B45309",
          soft: "#FCEACB",
        },
        danger: {
          DEFAULT: "#E11D48",
          soft: "#FDE2E7",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        display: ["var(--font-space-grotesk)", "system-ui", "sans-serif"],
        serif: ["var(--font-fraunces)", "Georgia", "serif"],
      },
      borderRadius: {
        card: "16px",
        pill: "999px",
      },
      boxShadow: {
        card: "0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 24px -12px rgba(0,0,0,0.6)",
        glow: "0 0 0 1px rgba(34,197,94,0.4), 0 0 24px 0 rgba(34,197,94,0.35)",
      },
      backgroundImage: {
        "grid-fade":
          "radial-gradient(circle at 50% 0%, rgba(22,163,74,0.07), transparent 60%)",
      },
    },
  },
  plugins: [],
};

export default config;