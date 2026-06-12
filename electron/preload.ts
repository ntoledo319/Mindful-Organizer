import { contextBridge, ipcRenderer } from 'electron';
import { IPC_CHANNELS } from '../src/shared/ipc';
import type { HearthApi } from '../src/shared/ipc';

// Build the renderer-facing API from the shared channel list so the bridge can
// never drift from the contract. Each method just forwards to ipcRenderer.invoke.
const api = {} as Record<string, (...args: unknown[]) => Promise<unknown>>;
for (const channel of IPC_CHANNELS) {
  api[channel] = (...args: unknown[]) => ipcRenderer.invoke(channel, ...args);
}

contextBridge.exposeInMainWorld('hearth', api as unknown as HearthApi);

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
