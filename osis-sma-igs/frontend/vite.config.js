import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../backend/static/js",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        home: path.resolve(__dirname, "src/home.jsx")
      },
      output: {
        entryFileNames: "[name].js",
      },
    },
  },
});
