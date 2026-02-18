import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import basicSsl from '@vitejs/plugin-basic-ssl'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), basicSsl()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-react':      ['react', 'react-dom', 'react-router-dom'],
          'vendor-charts':     ['recharts'],
          'vendor-datepicker': ['react-datepicker', 'date-fns'],
        },
      },
    },
  },
  server: {
    host: true,
    port: 5173,
    https: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
