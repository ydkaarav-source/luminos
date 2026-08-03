import type { Config } from "tailwindcss";

/**
 * LuminOS design tokens.
 *
 * Direction: Apple-level simplicity, Bloomberg-level density/intelligence,
 * Jarvis-level calm. Dark, near-black canvas so data and AI copy read as
 * the main event; one confident accent (indigo) for actions and focus,
 * a cool mint for positive/health signals, amber reserved for warnings.
 */
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#0B0D12",
        panel: "#12151C",
        "panel-raised": "#171B25",
        border: {
          DEFAULT: "#1F2430",
          subtle: "#181C26",
        },
        ink: {
          DEFAULT: "#E7E9EE",
          muted: "#9AA2B4",
          faint: "#5B6273",
        },
        accent: {
          DEFAULT: "#4C6FFF",
          soft: "#2A3568",
          glow: "#7C93FF",
        },
        positive: {
          DEFAULT: "#2FD9C4",
          soft: "#123B37",
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
      },
      borderRadius: {
        card: "16px",
        pill: "999px",
      },
      boxShadow: {
        card: "0 1px 0 0 rgba(255,255,255,0.03) inset, 0 8px 24px -12px rgba(0,0,0,0.6)",
        glow: "0 0 0 1px rgba(76,111,255,0.4), 0 0 24px 0 rgba(76,111,255,0.25)",
      },
      backgroundImage: {
        "grid-fade":
          "radial-gradient(circle at 50% 0%, rgba(76,111,255,0.08), transparent 60%)",
      },
    },
  },
  plugins: [],
};

export default config;
