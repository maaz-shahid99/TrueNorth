import type { Config } from "tailwindcss";

// SnowUI / Plus UI-derived tokens (approximated from the supplied screenshots; centralized
// here so they're trivial to refine against the real kit later).
const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        app: "#F7F8FA",
        surface: "#FFFFFF",
        line: "#ECECEE",
        ink: "#1C1C1C",
        muted: "#6B7280",
        brand: {
          50: "#EEF0FF",
          100: "#E0E2FF",
          200: "#C7CBFF",
          300: "#A5ABFF",
          400: "#838BFF",
          500: "#6366F1",
          600: "#4F46E5",
          700: "#4338CA",
          800: "#3730A3",
          900: "#312E81",
        },
        // Verdict scale — each with a solid color and a soft background tint.
        verdict: {
          endorse: "#16A34A",
          "endorse-bg": "#E7F6EC",
          conditions: "#0EA5E9",
          "conditions-bg": "#E3F4FD",
          caution: "#D97706",
          "caution-bg": "#FDF1DD",
          oppose: "#DC2626",
          "oppose-bg": "#FCE9E9",
        },
        pastel: {
          blue: "#E8F0FE",
          lilac: "#ECEAFE",
          mint: "#E6F4EA",
          peach: "#FDECE8",
        },
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.25rem",
      },
      boxShadow: {
        card: "0 1px 2px rgba(16,24,40,.04), 0 1px 3px rgba(16,24,40,.06)",
      },
      fontFamily: {
        sans: [
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Inter",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};

export default config;
