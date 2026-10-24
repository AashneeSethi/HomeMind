import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const BACKEND_URL = process.env.VITE_BACKEND_URL || 'http://127.0.0.1:8081'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/health': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/state': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/events': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/watches': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/alerts': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/simulate': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/chat': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/mode': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
      '/commands': {
        target: BACKEND_URL,
        changeOrigin: true,
      },
    }
  }
})
