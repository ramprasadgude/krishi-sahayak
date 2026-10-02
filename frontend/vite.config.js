import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// During local development, the frontend runs on :5173 and the backend on
// :8000. This proxy lets the frontend call "/api/..." without hardcoding a
// host, so the same code works locally and once deployed (where you set
// VITE_API_BASE_URL instead — see src/api.js).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
