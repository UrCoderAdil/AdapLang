import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        rpg: {
          bg:      "#0f0e17",
          surface: "#1a1a2e",
          border:  "#2d2d44",
          gold:    "#f5a623",
          red:     "#e63946",
          green:   "#2dc653",
          blue:    "#457b9d",
          purple:  "#8338ec",
          text:    "#fffffe",
          muted:   "#a7a9be",
        },
      },
      fontFamily: {
        display: ["Georgia", "serif"],
        body:    ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "shake":      "shake 0.4s ease-in-out",
        "float":      "float 3s ease-in-out infinite",
        "pulse-gold": "pulseGold 1.5s ease-in-out infinite",
        "slide-up":   "slideUp 0.3s ease-out",
      },
      keyframes: {
        shake: {
          "0%, 100%": { transform: "translateX(0)" },
          "25%":      { transform: "translateX(-8px)" },
          "75%":      { transform: "translateX(8px)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%":      { transform: "translateY(-10px)" },
        },
        pulseGold: {
          "0%, 100%": { boxShadow: "0 0 0 0 rgba(245,166,35,0.4)" },
          "50%":      { boxShadow: "0 0 0 12px rgba(245,166,35,0)" },
        },
        slideUp: {
          from: { opacity: "0", transform: "translateY(16px)" },
          to:   { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
