// Main-process screenshot orchestrator. Runs only when HEARTH_SCREENSHOT=1
// (see main.ts) and produces the Microsoft Store listing screenshots at exactly
// 1920x1080. It seeds demo data, drives the renderer's route/theme through the
// __hearthShot bridge, and writes PNGs via webContents.capturePage. Dev-only —
// nothing here is reachable in a normal or packaged launch.
import { BrowserWindow, ipcMain, nativeTheme } from 'electron';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mkdirSync, writeFileSync } from 'node:fs';
import * as repo from './repo';
import { seedDemoData } from './devSeed';

const __dirname = dirname(fileURLToPath(import.meta.url));

const WIDTH = 1920;
const HEIGHT = 1080;

type Route = 'dashboard' | 'tasks' | 'reflect' | 'trends';

interface Shot {
  file: string;
  route?: Route;
  theme: 'light' | 'dark';
  onboarded: boolean;
}

const SHOTS: Shot[] = [
  { file: '01-today.png', route: 'dashboard', theme: 'light', onboarded: true },
  { file: '02-tasks.png', route: 'tasks', theme: 'light', onboarded: true },
  { file: '03-reflect.png', route: 'reflect', theme: 'light', onboarded: true },
  { file: '04-rhythm.png', route: 'trends', theme: 'dark', onboarded: true },
  { file: '05-onboarding.png', theme: 'light', onboarded: false },
];

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

// Resolve on the next 'screenshot:ready' from the renderer, or after a timeout
// so a renderer that never signals can't wedge the whole run.
function waitForReady(timeoutMs = 8000): Promise<void> {
  return new Promise((resolve) => {
    const done = () => {
      clearTimeout(t);
      ipcMain.removeListener('screenshot:ready', done);
      resolve();
    };
    const t = setTimeout(() => {
      console.warn('[screenshot] waitForReady timed out; proceeding anyway');
      done();
    }, timeoutMs);
    ipcMain.once('screenshot:ready', done);
  });
}

function loadApp(win: BrowserWindow): void {
  const devServer = process.env.VITE_DEV_SERVER_URL;
  if (devServer) void win.loadURL(devServer);
  else void win.loadFile(join(process.env.DIST!, 'index.html'));
}

export async function runScreenshots(): Promise<void> {
  const outDir = process.env.HEARTH_SHOT_DIR || join(__dirname, '../screenshots');
  mkdirSync(outDir, { recursive: true });

  seedDemoData();

  const win = new BrowserWindow({
    width: WIDTH,
    height: HEIGHT,
    show: false,
    useContentSize: true, // 1920x1080 of actual web content, no chrome inset
    backgroundColor: nativeTheme.shouldUseDarkColors ? '#1C201D' : '#F5F0E6',
    webPreferences: {
      preload: join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
      // The window is never shown (show:false); without this, Chromium throttles
      // timers/rAF on the hidden window and the route paint can lag the capture.
      backgroundThrottling: false,
      additionalArguments: ['--hearth-screenshot'],
    },
  });

  // Surface a crashed/blank renderer instead of silently capturing a blank frame.
  win.webContents.on('did-fail-load', (_e, code, desc, url) =>
    console.error('[screenshot] did-fail-load', code, desc, url),
  );
  win.webContents.on('render-process-gone', (_e, details) =>
    console.error('[screenshot] render-process-gone', details.reason),
  );

  for (const shot of SHOTS) {
    // The onboarding shot needs settings.onboarded=false; the rest need it true.
    repo.saveSettings({ onboarded: shot.onboarded });

    const ready = waitForReady();
    loadApp(win);
    await ready; // app shell mounted (and read the current settings)

    if (shot.route) {
      const settled = waitForReady();
      win.webContents.send('screenshot:goto', { route: shot.route, theme: shot.theme });
      await settled;
    } else {
      // Onboarding: no route, but still honor the theme for completeness.
      win.webContents.send('screenshot:goto', { theme: shot.theme });
      await delay(900);
    }

    await delay(500); // a final beat for fonts/images
    // Capture an exact 1920x1080 rect — the xvfb backing buffer is one px short
    // of the requested content size, so pin the rect rather than trust the size.
    const image = await win.webContents.capturePage({ x: 0, y: 0, width: WIDTH, height: HEIGHT });
    const dest = join(outDir, shot.file);
    writeFileSync(dest, image.toPNG());
    // eslint-disable-next-line no-console
    console.log(`[screenshot] wrote ${dest} (${image.getSize().width}x${image.getSize().height})`);
  }

  win.destroy();
}
