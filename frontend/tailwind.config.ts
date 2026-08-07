import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#1D2333",
        panel: "#242B3D",
        "panel-raised": "#2C3447",
        border: {
          DEFAULT: "#343D54",
          subtle: "#2A3145",
        },
        ink: {
          DEFAULT: "#EDF0F5",
          muted: "#9AA3BC",
          faint: "#6B7590",
        },
        accent: {
          DEFAULT: "#3E6FD4",
          soft: "#28345C",
          glow: "#7BA8D9",
        },
        positive: {
          DEFAULT: "#52B98A",
          soft: "#1C3A2E",
        },
        warning: {
          DEFAULT: "#F5A623",
          soft: "#3A2C10",
        },
        danger: {
          DEFAULT: "#FF5C7A",
          soft: "#3A1420",
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
        glow: "0 0 0 1px rgba(62,111,212,0.4), 0 0 24px 0 rgba(62,111,212,0.25)",
      },
      backgroundImage: {
        "grid-fade":
          "radial-gradient(circle at 50% 0%, rgba(62,111,212,0.08), transparent 60%)",
      },
    },
  },
  plugins: [],
};

export default config;