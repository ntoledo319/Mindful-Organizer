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
