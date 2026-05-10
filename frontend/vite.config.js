import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: 'http://119.28.14.122:8000',
        changeOrigin: true,
      },
      '/report': {
        target: 'ws://119.28.14.122:50000',
        ws: true,
        changeOrigin: true,
      }
    }
  }
})
