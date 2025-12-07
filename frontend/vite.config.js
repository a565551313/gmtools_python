import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8009',
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, '') // Depending on backend, usually /api is kept or removed. 
        // In user-functions.html, calls are like /api/users/me. If backend expects /api/users/me, then no rewrite.
        // If backend is mounted at root, then rewrite. 
        // Python backends (FastAPI/Flask) often have /api prefix or not. 
        // I will assume no rewrite for now as it's safer if the backend is structured with /api routes.
      }
    }
  }
})
