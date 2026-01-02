import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },

  build: {
    // Use 'dist' for Docker builds, otherwise output to backend staticfiles
    outDir: process.env.DOCKER_BUILD === 'true'
      ? 'dist'
      : path.resolve(__dirname, '../backend/staticfiles/frontend'),
    emptyOutDir: true,
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui': ['@mantine/core', '@mantine/hooks', '@mantine/notifications'],
          'state': ['zustand', '@tanstack/react-query'],
        },
      },
    },
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
