/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Mission-control "ink" surface ramp (deep navy → black).
        ink: {
          950: '#05080F',
          900: '#080F1C',
          850: '#0B1422',
          800: '#0F1B2D',
          700: '#16273C',
          600: '#1E3A52',
          500: '#2B567A',
        },
        // Brand teal — the command accent.
        accent: {
          DEFAULT: '#2DD4BF',
          glow: '#5EEAD4',
          dim: '#0E7C86',
          deep: '#0B5F66',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      boxShadow: {
        glow: '0 0 24px -4px rgba(45,212,191,0.55)',
        'glow-sm': '0 0 12px -2px rgba(45,212,191,0.45)',
        'glow-amber': '0 0 22px -4px rgba(245,158,11,0.55)',
        'glow-danger': '0 0 22px -4px rgba(244,63,94,0.55)',
        'glow-sky': '0 0 22px -4px rgba(56,189,248,0.5)',
        panel: '0 18px 40px -24px rgba(0,0,0,0.9), inset 0 1px 0 0 rgba(148,163,184,0.06)',
      },
      backgroundImage: {
        grid:
          'linear-gradient(rgba(45,212,191,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(45,212,191,0.05) 1px, transparent 1px)',
        'radial-command':
          'radial-gradient(1200px 600px at 78% -8%, rgba(14,124,134,0.22), transparent 60%), radial-gradient(900px 500px at 8% 110%, rgba(56,189,248,0.12), transparent 55%)',
        'accent-sheen':
          'linear-gradient(135deg, rgba(94,234,212,0.18), rgba(14,124,134,0.04))',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 0 0 rgba(45,212,191,0.55)' },
          '50%': { opacity: '0.65', boxShadow: '0 0 0 6px rgba(45,212,191,0)' },
        },
        'fan-in': {
          '0%': { opacity: '0', transform: 'translateY(-10px) scale(0.85)' },
          '100%': { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-300% 0' },
          '100%': { backgroundPosition: '300% 0' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '50%': { opacity: '0.7' },
          '100%': { transform: 'translateY(2400%)', opacity: '0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-4px)' },
        },
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'fan-in': 'fan-in 0.5s cubic-bezier(0.22,1,0.36,1) both',
        shimmer: 'shimmer 2.4s linear infinite',
        scan: 'scan 7s linear infinite',
        float: 'float 5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
