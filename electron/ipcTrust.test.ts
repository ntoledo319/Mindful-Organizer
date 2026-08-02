import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
import type { IpcMainInvokeEvent } from 'electron';
import { afterEach, describe, expect, it } from 'vitest';
import { isTrustedIpcSender } from './ipcTrust';

// The trust check reads the environment exactly the way main.ts sets it up at
// launch, so each test stages VITE_DEV_SERVER_URL / DIST and the hook restores
// whatever the runner had.
const savedDevServer = process.env.VITE_DEV_SERVER_URL;
const savedDist = process.env.DIST;

afterEach(() => {
  if (savedDevServer === undefined) delete process.env.VITE_DEV_SERVER_URL;
  else process.env.VITE_DEV_SERVER_URL = savedDevServer;
  if (savedDist === undefined) delete process.env.DIST;
  else process.env.DIST = savedDist;
});

function fakeEvent(url: string, subframe = false): IpcMainInvokeEvent {
  const mainFrame = { url };
  return {
    senderFrame: subframe ? { url } : mainFrame,
    sender: { mainFrame },
  } as unknown as IpcMainInvokeEvent;
}

describe('isTrustedIpcSender', () => {
  it('trusts only the Vite dev-server origin in development', () => {
    process.env.VITE_DEV_SERVER_URL = 'http://localhost:5173';
    expect(isTrustedIpcSender(fakeEvent('http://localhost:5173/'))).toBe(true);
    expect(isTrustedIpcSender(fakeEvent('http://localhost:5173/tasks'))).toBe(true);
    expect(isTrustedIpcSender(fakeEvent('http://localhost:5174/'))).toBe(false);
    expect(isTrustedIpcSender(fakeEvent('http://evil.example/'))).toBe(false);
  });

  it('trusts only the packaged index.html over file: in production', () => {
    delete process.env.VITE_DEV_SERVER_URL;
    process.env.DIST = join('hearth-test', 'dist');
    const expected = pathToFileURL(join(process.env.DIST, 'index.html')).href;
    expect(isTrustedIpcSender(fakeEvent(expected))).toBe(true);
    expect(
      isTrustedIpcSender(fakeEvent(pathToFileURL(join(process.env.DIST, 'other.html')).href)),
    ).toBe(false);
    expect(isTrustedIpcSender(fakeEvent('https://example.com/index.html'))).toBe(false);
  });

  it('rejects subframes even when the URL itself would be trusted', () => {
    process.env.VITE_DEV_SERVER_URL = 'http://localhost:5173';
    expect(isTrustedIpcSender(fakeEvent('http://localhost:5173/', true))).toBe(false);
  });

  it('rejects missing frames and malformed URLs', () => {
    expect(
      isTrustedIpcSender({
        senderFrame: null,
        sender: { mainFrame: null },
      } as unknown as IpcMainInvokeEvent),
    ).toBe(false);
    process.env.VITE_DEV_SERVER_URL = 'http://localhost:5173';
    expect(isTrustedIpcSender(fakeEvent('not a url'))).toBe(false);
  });
});
