import type { HearthApi } from '@shared/ipc';

declare global {
  interface Window {
    hearth: HearthApi;
  }
}

// Thin accessor so screens import a typed `api` rather than reaching into window.
export const api: HearthApi = window.hearth;
