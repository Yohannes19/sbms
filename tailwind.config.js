// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html", // Point to your templates directory
  ],
  theme: {
    extend: {
      colors: {
        'luna-darkest': '#011C40',
        'luna-dark': '#023859',
        'luna-mid': '#26658C',
        'luna-light': '#54ACBF',
        'luna-accent': '#A7EBF2',
      },
      fontFamily: {
        sans: ['Inter', 'Open Sans', 'sans-serif'],
        // You can add custom fonts later if you like
      }
    },
  },
  plugins: [],
}