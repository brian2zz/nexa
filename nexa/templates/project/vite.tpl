import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import fs from 'fs'

const appsDir = resolve(__dirname, 'apps')
const inputs = {}

// Dynamically find all app entry points
if (fs.existsSync(appsDir)) {
  const apps = fs.readdirSync(appsDir)
  apps.forEach(app => {
    const indexPath = resolve(appsDir, app, 'frontend', 'index.html')
    if (fs.existsSync(indexPath)) {
      inputs[app] = indexPath
    }
  })
}

export default defineConfig({
  plugins: [vue()],
  
  server: {
    port: 5173,
    host: '0.0.0.0',
    cors: true,
    strictPort: true,
    origin: 'http://localhost:5173',
    proxy: {
      '/api': {
        target: process.env.NEXA_BACKEND_URL || 'http://localhost:8000',
        changeOrigin: true
      },
      '/admin': {
        target: process.env.NEXA_BACKEND_URL || 'http://localhost:8000'
      },
      '/static': {
        target: process.env.NEXA_BACKEND_URL || 'http://localhost:8000'
      },
      '/media': {
        target: process.env.NEXA_BACKEND_URL || 'http://localhost:8000'
      }
    }
  },

  build: {
    manifest: true,
    outDir: 'dist',
    rollupOptions: {
      input: inputs
    }
  }
})
