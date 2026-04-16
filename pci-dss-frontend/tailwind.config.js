/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'pci-dark': '#0f172a',
        'pci-card': '#1e293b',
        'pci-border': '#334155',
        'pci-blue': '#3b82f6',
        'pci-green': '#22c55e',
        'pci-red': '#ef4444',
        'pci-amber': '#f59e0b',
        'pci-purple': '#a855f7',
      }
    },
  },
  plugins: [],
}