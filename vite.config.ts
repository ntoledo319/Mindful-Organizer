import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import electron from 'vite-plugin-electron';
import renderer from 'vite-plugin-electron-renderer';
import { resolve } from 'node:path';

export default defineConfig(({ command }) => ({
  resolve: {
    alias: {
      '@shared': resolve(__dirname, 'src/shared'),
      '@renderer': resolve(__dirname, 'src/renderer'),
    },
  },
  plugins: [
    react(),
    electron([
      {
        entry: 'electron/main.ts',
        vite: {
          build: {
            outDir: 'dist-electron',
            // vite-plugin-electron forces emptyOutDir:false and builds each
            // entry sequentially in array order. Emptying on the FIRST entry
            // clears stale hashed chunks (dynamic-import output accumulates
            // across builds) while preload's output — built next — is
            // untouched. Builds only: dev watch rebuilds must not empty.
            emptyOutDir: command === 'build',
            rollupOptions: {
              external: ['better-sqlite3', 'electron'],
            },
          },
        },
      },
      {
        entry: 'electron/preload.ts',
        onstart(args) {
          args.reload();
        },
        vite: {
          build: {
            outDir: 'dist-electron',
            // Electron loads preload scripts via CommonJS require(); with
            // "type": "module" set, vite-plugin-electron would emit ESM and
            // Electron throws ERR_REQUIRE_ESM. Force a CommonJS .cjs build so
            // the preload loads under both packaged and screenshot runs.
            lib: {
              entry: 'electron/preload.ts',
              formats: ['cjs'],
              fileName: () => 'preload.cjs',
            },
          },
        },
      },
    ]),
    renderer(),
  ],
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
}));
