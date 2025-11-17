import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000, // We'll run on port 3000 to match docker-compose
    // This is for local development (npm run dev)
    // It proxies requests from http://localhost:3000/api/...
    // to your backend services running on ports 8000 & 8001.
    proxy: {
      '/api/text-to-sql': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/text-to-sql/, ''),
      },
      '/api/diagnostics': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/diagnostics/, ''),
      },
    },
  },
})

