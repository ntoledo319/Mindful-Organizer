import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/renderer/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Earthenware & Vellum
        base: {
          bg: '#F5F2ED',    // Unbleached Linen
          surface: '#FCFBF9', // Clean Vellum
          border: '#E6DFD7',  // Dry Clay
        },
        text: {
          primary: '#2C2725', // Charred Wood
          muted: '#5A524C',   // River Stone (Darkened for WCAG)
        },
        brand: {
          DEFAULT: '#C45536', // Fired Terracotta
        },
        semantic: {
          error: '#B53737',
          warning: '#C48421',
          success: '#3B7051',
        },
        // Dark Mode Embers
        night: {
          bg: '#191716',      // Cold Ash
          surface: '#24211F', // Smoldering Loam
          border: '#3C3633',  // Charcoal Seam
          text: '#EAE6E0',    // Pale Bone
          muted: '#9E968F',   // Pumice
          brand: '#E27352',   // Glowing Ember
          error: '#E36A6A',
          warning: '#E6B055',
          success: '#64A37D',
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
        hearth: '0 4px 12px -2px rgba(44, 39, 37, 0.08), 0 2px 4px -2px rgba(44, 39, 37, 0.04)',
        glow: '0 4px 20px -2px rgba(196, 85, 54, 0.15)',
        'night-hearth': '0 4px 12px -2px rgba(0, 0, 0, 0.4)',
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
