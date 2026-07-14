import { resolve } from 'node:path';
import { defineConfig } from 'vitest/config';

// Keep unit tests on the Node runtime. Importing the application Vite config
// also loads the Electron renderer plugin, which rewrites Node built-ins such
// as `node:crypto` into browser shims and makes security tests meaningless.
export default defineConfig({
  resolve: {
    alias: {
      '@shared': resolve(__dirname, 'src/shared'),
    },
  },
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts', 'electron/**/*.test.ts'],
  },
});
