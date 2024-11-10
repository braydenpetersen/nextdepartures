import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    colors: {
      "black": "var(--black)",
      "white": "var(--white)",
      "yellow": "var(--yellow)",
      "dark-grey": "var(--dark-grey)",
      "light-grey": "var(--light-grey)",
    },
    fontFamily: {
      sans: ['Overpass', 'sans-serif'],
    },
  },
  plugins: [],
};
export default config;
