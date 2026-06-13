import { contextBridge, ipcRenderer, type IpcRendererEvent } from 'electron';
import { IPC_CHANNELS } from '../src/shared/ipc';
import type { HearthApi } from '../src/shared/ipc';
import type { PresenceUpdate } from '../src/shared/types';

// Build the renderer-facing API from the shared channel list so the bridge can
// never drift from the contract. Each method just forwards to ipcRenderer.invoke.
const api = {} as Record<string, (...args: unknown[]) => Promise<unknown>>;
for (const channel of IPC_CHANNELS) {
  api[channel] = (...args: unknown[]) => ipcRenderer.invoke(channel, ...args);
}

contextBridge.exposeInMainWorld('hearth', api as unknown as HearthApi);

// One-way bridge for the acting layer: main pushes live presence/settings state
// (the dim went up, the focus hold ended, the tray changed a setting) so the UI
// can mirror it without polling. Returns an unsubscribe.
contextBridge.exposeInMainWorld('hearthPresence', {
  subscribe(cb: (payload: PresenceUpdate) => void): () => void {
    const handler = (_e: IpcRendererEvent, payload: PresenceUpdate) => cb(payload);
    ipcRenderer.on('presence:update', handler);
    return () => ipcRenderer.removeListener('presence:update', handler);
  },
});

// Screenshot driver bridge — exposed only when main launched us in screenshot
// mode (process arg --hearth-screenshot). Lets the capture orchestrator steer
// the renderer's route/theme. Inert in every normal launch.
if (process.argv.includes('--hearth-screenshot')) {
  contextBridge.exposeInMainWorld('__hearthShot', {
    onGoto: (cb: (spec: { route?: string; theme?: 'light' | 'dark' }) => void) =>
      ipcRenderer.on('screenshot:goto', (_e, spec) => cb(spec)),
    ready: () => ipcRenderer.send('screenshot:ready'),
  });
}
