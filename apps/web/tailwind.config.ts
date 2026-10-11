import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#090A0D', // Deep matte luxury obsidian
        surface: '#121318',    // Refined charcoal obsidian
        'surface-elevated': '#191A22', // Elevated warm dark slate
        'surface-border': '#272834',   // Muted obsidian borders
        'surface-borderHover': '#423A2B', // Amber-tinted border hover
        primary: {
          50: '#FFFDF5',
          100: '#FEF9C3',
          200: '#FEF08A',
          300: '#FDE047',
          400: '#FBBF24', // Luminous Gold
          500: '#F59E0B', // Rich Warm Amber
          600: '#D97706', // Burnished Amber
          700: '#B45309', // Deep Bronze
          800: '#92400E',
          900: '#78350F',
          950: '#451A03',
        },
        accent: {
          gold: '#F6C453',
          amber: '#F59E0B',
          bronze: '#CA8A04',
          emerald: '#10B981',
          rose: '#F43F5E',
          cyan: '#38BDF8',
          violet: '#A855F7',
        }
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'hero-glow': 'radial-gradient(circle at 50% 0%, rgba(245, 158, 11, 0.16) 0%, transparent 70%)',
        'glass-gradient': 'linear-gradient(135deg, rgba(255, 248, 230, 0.04) 0%, rgba(245, 158, 11, 0.01) 100%)',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.65)',
        'glow-primary': '0 0 25px -4px rgba(245, 158, 11, 0.45)',
        'glow-amber': '0 0 30px -5px rgba(251, 191, 36, 0.5)',
        'glow-emerald': '0 0 25px -5px rgba(16, 185, 129, 0.4)',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '1' },
        },
      },
      animation: {
        'pulse-glow': 'pulseGlow 3s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};

export default config;
