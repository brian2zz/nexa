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
// Custom resolver plugin to support multi-app @/ aliases dynamically
const multiAppAliasResolver = () => {
  return {
    name: 'nexa-multi-app-alias',
    resolveId(source, importer) {
      if (source.startsWith('@/') && importer) {
        // Find the base src directory of the importing app
        const match = importer.match(/(.*\/apps\/[^/]+\/frontend\/src\/)/);
        if (match) {
          const targetPath = resolve(match[1], source.slice(2));
          if (fs.existsSync(targetPath)) {
            return targetPath;
          }
          // Coba tambahkan ekstensi standar jika tidak dituliskan
          const extensions = ['.js', '.vue', '.json'];
          for (const ext of extensions) {
            if (fs.existsSync(targetPath + ext)) {
              return targetPath + ext;
            }
          }
          return targetPath;
        }
      }
      return null;
    }
  }
}

export default defineConfig({
  plugins: [vue(), multiAppAliasResolver()],
  
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
