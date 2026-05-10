import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    hmr: false,  // 禁用热更新，避免 WebSocket 连接问题
    proxy: {
      '/api': {
        target: 'http://119.28.14.122:8000',
        changeOrigin: true,
      }
    }
  }
})
