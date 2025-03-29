import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  server: {
    historyApiFallback: true,
  },
  resolve: {
    alias: {
      '@common': path.resolve(__dirname, 'src/common'),
    },
  },
});
