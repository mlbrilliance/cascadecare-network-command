/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Charcoal "ink" surface ramp (warm-neutral graphite, Phoenix-style).
        ink: {
          950: '#0C0E12',
          900: '#111317',
          850: '#15181E',
          800: '#1B1F27',
          700: '#242935',
          600: '#333A48',
          500: '#4A5365',
        },
        // Single command accent — the "crisis energy" orange.
        accent: {
          DEFAULT: '#F26B1D',
          glow: '#FF8A3D',
          dim: '#B8501A',
          deep: '#7A3411',
        },
        // Neutral UI grey — the dominant text/icon tone.
        slateUI: '#8A929E',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      boxShadow: {
        // Glow is reserved — only the hero bolt + active cables + primary CTA.
        glow: '0 0 26px -4px rgba(242,107,29,0.6)',
        'glow-sm': '0 0 14px -3px rgba(242,107,29,0.5)',
        panel: '0 20px 44px -28px rgba(0,0,0,0.95), inset 0 1px 0 0 rgba(255,255,255,0.04)',
      },
      backgroundImage: {
        // Faint dot texture (Phoenix uses dots, not a grid).
        dots: 'radial-gradient(rgba(255,255,255,0.045) 1px, transparent 1px)',
        'radial-command':
          'radial-gradient(1100px 560px at 82% -10%, rgba(242,107,29,0.14), transparent 60%), radial-gradient(820px 460px at 4% 108%, rgba(242,107,29,0.06), transparent 58%)',
        'accent-sheen':
          'linear-gradient(135deg, rgba(255,138,61,0.16), rgba(242,107,29,0.02))',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '1', boxShadow: '0 0 0 0 rgba(242,107,29,0.55)' },
          '50%': { opacity: '0.7', boxShadow: '0 0 0 6px rgba(242,107,29,0)' },
        },
        // Energy travelling along an SVG cable (paired with stroke-dasharray).
        'flow-dash': {
          to: { strokeDashoffset: '-32' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-300% 0' },
          '100%': { backgroundPosition: '300% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-3px)' },
        },
      },
      animation: {
        'pulse-glow': 'pulse-glow 2.2s ease-in-out infinite',
        'flow-dash': 'flow-dash 1s linear infinite',
        shimmer: 'shimmer 2.4s linear infinite',
        float: 'float 5s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
