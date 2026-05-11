/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#0b1220',
        slate: '#1f2a44',
        mist: '#f5f7fb',
        cyan: '#2bd4bd',
        amber: '#f59e0b',
        coral: '#fb7185',
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"DM Sans"', 'sans-serif'],
      },
      boxShadow: {
        glow: '0 10px 40px rgba(43, 212, 189, 0.25)',
        soft: '0 10px 30px rgba(15, 23, 42, 0.15)',
      },
      backgroundImage: {
        aura: 'radial-gradient(circle at top, rgba(43, 212, 189, 0.35), transparent 55%)',
        grid: 'linear-gradient(transparent 0 0), repeating-linear-gradient(90deg, rgba(148, 163, 184, 0.12) 0 1px, transparent 1px 120px), repeating-linear-gradient(180deg, rgba(148, 163, 184, 0.12) 0 1px, transparent 1px 120px)',
      },
    },
  },
  plugins: [],
}
