import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Simple dev proxy to Flask if you want same-origin URLs:
// (Uncomment and use /api not absolute URL. I’ll keep fetch using absolute http://127.0.0.1:5000 to avoid confusion.)
export default defineConfig({
  plugins: [react()],
})
