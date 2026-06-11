import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/renderer/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cream: {
          DEFAULT: '#F5F0E6',
          deep: '#EDE6D6',
        },
        sage: {
          DEFAULT: '#3E5C50',
          light: '#5A7C6E',
          dim: '#6E8C7E',
        },
        eucalyptus: '#A6BFA6',
        lavender: {
          DEFAULT: '#C9C3E3',
          deep: '#A79FD0',
        },
        charcoal: {
          DEFAULT: '#2C2C2A',
          soft: '#4A4A46',
          mute: '#7A7A72',
        },
        ember: '#C97B5A',
        // dark mode hearth tones
        night: {
          DEFAULT: '#1C201D',
          card: '#252A26',
          edge: '#333A34',
        },
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        glass: '1.5rem',
      },
      boxShadow: {
        hearth: '0 10px 40px -12px rgba(62, 92, 80, 0.22)',
        glow: '0 0 0 1px rgba(255,255,255,0.4), 0 18px 50px -20px rgba(62,92,80,0.35)',
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
