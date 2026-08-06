import { defineConfig } from "vite";
import uni from "@dcloudio/vite-plugin-uni";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [uni()],
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      // H5 开发时把 /api 代理到本地后端，避免跨域
      "/api": {
        target: "http://localhost:8080",
        changeOrigin: true,
      },
    },
  },
});
