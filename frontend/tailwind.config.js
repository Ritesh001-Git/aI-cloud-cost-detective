/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        panel: "#101827",
        ink: "#070b13",
        signal: "#39e6d0",
        violet: "#9b87f5",
      },
      boxShadow: {
        glow: "0 0 30px rgba(57, 230, 208, 0.12)",
      },
    },
  },
  plugins: [],
};
