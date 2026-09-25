/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        clinical: {
          50: '#F0F9FF',
          100: '#E0F2FE',
          200: '#BAE6FD',
          300: '#7DD3FC',
          400: '#38BDF8',
          500: '#0EA5E9',
          600: '#0284C7',
          700: '#0369A1',
          800: '#075985',
          900: '#0C4A6E',
          950: '#082F49',
        },
        navy: {
          800: '#1E293B',
          900: '#0F172A',
          950: '#0B132B',
        },
        surface: {
          DEFAULT: '#FFFFFF',
          muted: '#F8FAFC',
          subtle: '#F1F5F9',
          border: '#E2E8F0',
        },
        redflag: {
          bg: '#FEF2F2',
          border: '#F87171',
          text: '#991B1B',
          accent: '#DC2626',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      animation: {
        'wave-pulse': 'wavePulse 1.5s ease-in-out infinite',
        'scan-beam': 'scanBeam 2.5s ease-in-out infinite',
        'subtle-pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        wavePulse: {
          '0%, 100%': { transform: 'scaleY(0.4)', opacity: '0.6' },
          '50%': { transform: 'scaleY(1.0)', opacity: '1.0' },
        },
        scanBeam: {
          '0%': { top: '0%' },
          '50%': { top: '95%' },
          '100%': { top: '0%' },
        }
      }
    },
  },
  plugins: [],
}
