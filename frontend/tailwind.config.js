/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        display: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
        sans: ['"Inter"', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
        serif: ['"Newsreader"', 'Georgia', 'serif'],
      },
      colors: {
        canvas: 'var(--bg-canvas)',
        surface: 'var(--bg-surface)',
        'surface-elevated': 'var(--bg-surface-elevated)',
        'surface-secondary': 'var(--bg-surface-secondary)',
        primary: 'var(--text-primary)',
        secondary: 'var(--text-secondary)',
        subtle: 'var(--border-subtle)',
        'border-hover': 'var(--border-hover)',
        // Semantic investigation tokens
        'accent-violet': 'var(--accent-violet)',
        'accent-cyan': 'var(--accent-cyan)',
        'accent-coral': 'var(--accent-coral)',
        'accent-emerald': 'var(--accent-emerald)',
        'accent-amber': 'var(--accent-amber)',
        'accent-blue': 'var(--accent-blue)',
        'accent-red': 'var(--accent-red)',
      },
      boxShadow: {
        'soft': '0 1px 3px 0 rgba(0, 0, 0, 0.02), 0 1px 2px -1px rgba(0, 0, 0, 0.02)',
        'card': '0 4px 20px -2px rgba(0, 0, 0, 0.04), 0 2px 6px -1px rgba(0, 0, 0, 0.02)',
        'elevated': '0 10px 30px -4px rgba(0, 0, 0, 0.08), 0 4px 12px -2px rgba(0, 0, 0, 0.03)',
        'drawer': '0 20px 50px -12px rgba(0, 0, 0, 0.25)',
      },
      borderRadius: {
        'control': '7px',
        'card': '12px',
        'surface': '16px',
      },
      transitionTimingFunction: {
        'spring': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'out-expo': 'cubic-bezier(0.19, 1, 0.22, 1)',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        pulseSlow: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.4', transform: 'scale(0.95)' },
        },
      },
      animation: {
        'fade-up': 'fadeUp 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'slide-in-right': 'slideInRight 0.28s cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'pulse-slow': 'pulseSlow 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
