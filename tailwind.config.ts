import type { Config } from 'tailwindcss';
import { THEME_COLORS } from './src/shared/theme';

export default {
  content: ['./index.html', './src/renderer/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Earthenware & Vellum
        base: {
          bg: THEME_COLORS.base.bg,    // Unbleached Linen
          surface: THEME_COLORS.base.surface, // Clean Vellum
          border: THEME_COLORS.base.border,  // Dry Clay
        },
        text: {
          primary: THEME_COLORS.text.primary, // Charred Wood
          muted: THEME_COLORS.text.muted,   // River Stone (AAA on the base canvas)
        },
        brand: {
          DEFAULT: THEME_COLORS.brand, // Fired Terracotta (AA with white and on the base canvas)
        },
        semantic: {
          error: THEME_COLORS.semantic.error,
          warning: THEME_COLORS.semantic.warning,
          success: THEME_COLORS.semantic.success,
        },
        // Dark Mode Embers
        night: {
          bg: THEME_COLORS.night.bg,      // Cold Ash
          surface: THEME_COLORS.night.surface, // Smoldering Loam
          border: THEME_COLORS.night.border,  // Charcoal Seam
          text: THEME_COLORS.night.text,    // Pale Bone
          muted: THEME_COLORS.night.muted,   // Pumice (AAA on the night surface)
          brand: THEME_COLORS.night.brand,   // Glowing Ember
          error: THEME_COLORS.night.error,
          warning: THEME_COLORS.night.warning,
          success: THEME_COLORS.night.success,
        },
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        body: ['"Atkinson Hyperlegible"', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        soft: '0.5rem',
      },
      boxShadow: {
        // Physical shadow for earthenware
        paulatim: '0 4px 12px -2px rgba(44, 39, 37, 0.08), 0 2px 4px -2px rgba(44, 39, 37, 0.04)',
        glow: '0 4px 20px -2px rgba(196, 85, 54, 0.15)',
        'night-paulatim': '0 4px 12px -2px rgba(0, 0, 0, 0.4)',
      },
      keyframes: {
        breathe: {
          '0%, 100%': { transform: 'scale(0.82)', opacity: '0.65' },
          '50%': { transform: 'scale(1.12)', opacity: '1' },
        },
        rise: {
          '0%': { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        breathe: 'breathe 8s ease-in-out infinite',
        rise: 'rise 0.5s ease-out both',
      },
    },
  },
  plugins: [],
} satisfies Config;
