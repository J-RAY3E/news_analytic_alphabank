import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#ef3124",
        "primary-press": "#c4271c",
        "surface-dark": "#121212",
        "surface-dark-raised": "#212124",
        "surface-dark-button": "#2c2c2e",
        "hairline-on-dark": "#3a3a3d",
        "on-dark-mute": "#a0a3ab",
        ink: "#121212",
        "ink-secondary": "#2c2c2e",
        "ink-mute": "#6d7078",
        "on-primary": "#ffffff",
        canvas: "#ffffff",
        "canvas-soft": "#f3f4f5",
        "canvas-track": "#edeef0",
        "canvas-grey": "#e8ecee",
        hairline: "#e3e5e8",
        "hairline-input": "#c9cdd2",
        cyan: "#01d2f1",
        "cyan-soft": "#6ae9ed",
        blue: "#266fff",
        "blue-deep": "#0a3fb5",
        "blue-bg": "#e3edff",
        lilac: "#dfbfff",
        "lilac-soft": "#f1e4ff",
        "lilac-deep": "#9b5de5",
        success: "#108c3d",
        "success-bg": "#e3f5e8",
        "risk-bg": "#ffe5e2",
        danger: "#c4271c",
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      borderRadius: {
        xs: "4px",
        sm: "6px",
        md: "8px",
        lg: "12px",
        xl: "16px",
        pill: "9999px",
      },
      boxShadow: {
        "level-1": "0 1px 3px rgba(18, 18, 18, 0.08)",
        "level-2": "0 8px 24px rgba(18, 18, 18, 0.10), 0 2px 6px rgba(18, 18, 18, 0.05)",
      },
    },
  },
  plugins: [],
};
export default config;
