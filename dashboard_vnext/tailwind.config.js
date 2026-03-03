/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0E1117',
        card: '#1E1E1E',
        dry: '#FF4B4B',
        warn: '#F5A623',
        normal: '#00C851'
      }
    }
  },
  plugins: []
};
