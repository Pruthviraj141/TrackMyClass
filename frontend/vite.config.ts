import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import tsconfigPaths from 'vite-tsconfig-paths'

// done 

export default defineConfig({
  plugins: [react(), tailwindcss(), tsconfigPaths()],
  server: {
    allowedHosts: ['trackmyclass.work.gd', 'www.trackmyclass.work.gd'],
    host: '0.0.0.0',
    port: 5173
  }
})
