import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // All calls to /api/google-form will be forwarded to the Apps Script exec URL
      "/api/google-form": {
        target: "https://script.google.com/macros/s/AKfycbwfefEX9lZjehgjxSXnBRGLuFu5SchGchIv_r5AHv_83QJfDjZfKlMRFttuKHGK3rTR/exec",
        changeOrigin: true,
        secure: true,
        rewrite: (path) => path.replace(/^\/api\/google-form/, ""),
      },
    },
  },
})
