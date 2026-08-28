import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import type { IpcMainInvokeEvent } from 'electron';

// Every ipcMain.handle routes through this check: only the main frame of
// Paulatim's own window may call in. Under the Vite dev server that means the
// dev origin; otherwise it means exactly the packaged index.html over file:.
// Subframes, other origins, and malformed URLs are refused.
export function isTrustedIpcSender(event: IpcMainInvokeEvent): boolean {
  const frame = event.senderFrame;
  if (!frame || frame !== event.sender.mainFrame) return false;

  try {
    const senderUrl = new URL(frame.url);
    const devServer = process.env.VITE_DEV_SERVER_URL;
    if (devServer) {
      return senderUrl.origin === new URL(devServer).origin;
    }

    const expected = pathToFileURL(join(process.env.DIST!, 'index.html'));
    return senderUrl.protocol === 'file:' && senderUrl.pathname === expected.pathname;
  } catch {
    return false;
  }
}
