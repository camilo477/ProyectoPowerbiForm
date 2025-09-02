/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1E40AF", 
          light: "#3B82F6",  
          dark: "#1E3A8A",   
        },
        secondary: {
          DEFAULT: "#0D9488", 
          light: "#14B8A6",
          dark: "#0F766E",
        },
        neutral: {
          DEFAULT: "#374151", 
          light: "#6B7280",   
          dark: "#111827",    
        },
        background: {
          DEFAULT: "#F9FAFB", 
          card: "#FFFFFF",   
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"], 
      },
      boxShadow: {
        soft: "0 4px 6px rgba(0, 0, 0, 0.05)", 
        medium: "0 6px 12px rgba(0, 0, 0, 0.1)", 
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.5rem",
      },
    },
  },
  plugins: [],
}
