import type { HearthApi } from '@shared/ipc';
import type { PresenceUpdate } from '@shared/types';

interface PresenceBridge {
  subscribe(cb: (payload: PresenceUpdate) => void): () => void;
}

declare global {
  interface Window {
    hearth: HearthApi;
    hearthPresence?: PresenceBridge;
  }
}

// Thin accessor so screens import a typed `api` rather than reaching into window.
export const api: HearthApi = window.hearth;

// Subscribe to live presence/settings pushes from the main process. No-op in
// any context where the bridge isn't present (e.g. a plain browser preview).
export function onPresence(cb: (payload: PresenceUpdate) => void): () => void {
  return window.hearthPresence?.subscribe(cb) ?? (() => {});
}
