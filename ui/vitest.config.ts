import { defineConfig } from 'vitest/config';
import path from 'path';

export default defineConfig({
  test: {
    environment: 'happy-dom',
    setupFiles: [path.resolve(__dirname, 'vitest.setup.ts')],
    pool: 'forks',
    include: ['tests/**/*.test.{ts,tsx}'],
  },
  esbuild: {
    jsx: 'automatic',
    jsxImportSource: 'react',
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname),
    },
  },
});