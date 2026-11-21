// Vite config: React + Tailwind v4 plugins, "@" aliased to src/, and /api proxied to FastAPI on :8000.
// The proxy keeps the browser on one origin, which the backend's samesite=strict cookie needs.
import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
});
