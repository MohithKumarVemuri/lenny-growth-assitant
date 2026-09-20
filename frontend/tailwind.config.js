/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        obsidian: {
          900: '#070a0f',
          800: '#0b0f17',
          700: '#131b2a',
          600: '#1c2638',
          500: '#2a3850',
          400: '#415474'
        },
        brand: {
          amber: '#f59e0b',
          gold: '#fbbf24',
          emerald: '#10b981',
          indigo: '#6366f1',
          sky: '#38bdf8'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace']
      }
    },
  },
  plugins: [],
}
