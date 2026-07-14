// Main-process screenshot orchestrator. Runs only when HEARTH_SCREENSHOT=1
// (see main.ts) and produces the Microsoft Store listing screenshots at exactly
// 1920x1080. It seeds demo data, drives the renderer's route/theme through the
// __hearthShot bridge, and writes PNGs via webContents.capturePage. Dev-only —
// nothing here is reachable in a normal or packaged launch.
import { BrowserWindow, ipcMain, nativeTheme } from 'electron';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mkdirSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
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
  caption: string;
}

interface CapturedShot {
  file: string;
  route: Route | 'onboarding';
  theme: 'light' | 'dark';
  width: number;
  height: number;
  bytes: number;
  sha256: string;
  caption: string;
}

const SHOTS: Shot[] = [
  {
    file: '01-today.png',
    route: 'dashboard',
    theme: 'light',
    onboarded: true,
    caption: 'See the energy left today, a plain-language briefing, and open tasks whose recorded cost fits the remaining budget.',
  },
  {
    file: '02-tasks.png',
    route: 'tasks',
    theme: 'light',
    onboarded: true,
    caption: 'Give work a priority, expected duration, and energy demand; Hearth estimates a spoon cost for the plan.',
  },
  {
    file: '03-reflect.png',
    route: 'reflect',
    theme: 'light',
    onboarded: true,
    caption: 'Record mood, energy, anxiety, sleep, or a private journal entry in the local desktop app.',
  },
  {
    file: '04-rhythm.png',
    route: 'trends',
    theme: 'dark',
    onboarded: true,
    caption: 'Review your own mood, energy, and sleep across 7, 14, or 30 days, then request a local PDF summary.',
  },
  {
    file: '05-onboarding.png',
    theme: 'light',
    onboarded: false,
    caption: 'Start without an account and review local-data consent before Hearth stores the information you enter.',
  },
];

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

function withTimeout<T>(promise: Promise<T>, label: string, timeoutMs = 20_000): Promise<T> {
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(
      () => reject(new Error(`${label} exceeded ${timeoutMs / 1000} seconds.`)),
      timeoutMs,
    );
    promise.then(
      (value) => {
        clearTimeout(timeout);
        resolve(value);
      },
      (error: unknown) => {
        clearTimeout(timeout);
        reject(error);
      },
    );
  });
}

// Resolve on the next 'screenshot:ready' from the renderer. A missing signal is
// a failed proof, not permission to capture a potentially blank Store image.
function waitForReady(timeoutMs = 20_000): Promise<void> {
  return new Promise((resolve, reject) => {
    const done = () => {
      clearTimeout(t);
      ipcMain.removeListener('screenshot:ready', done);
      resolve();
    };
    const t = setTimeout(() => {
      ipcMain.removeListener('screenshot:ready', done);
      reject(new Error(`Renderer did not signal screenshot readiness within ${timeoutMs / 1000} seconds.`));
    }, timeoutMs);
    ipcMain.once('screenshot:ready', done);
  });
}

function loadApp(win: BrowserWindow): Promise<void> {
  const devServer = process.env.VITE_DEV_SERVER_URL;
  if (devServer) return win.loadURL(devServer);
  return win.loadFile(join(process.env.DIST!, 'index.html'));
}

export async function runScreenshots(): Promise<void> {
  const outDir = process.env.HEARTH_SHOT_DIR || join(__dirname, '../screenshots');
  mkdirSync(outDir, { recursive: true });
  const manifest: {
    generatedAt: string;
    buildRef: string | null;
    containsFictionalDemoData: true;
    images: CapturedShot[];
  } = {
    generatedAt: new Date().toISOString(),
    buildRef: process.env.HEARTH_SHOT_BUILD_REF || null,
    containsFictionalDemoData: true,
    images: [],
  };

  seedDemoData();

  const win = new BrowserWindow({
    width: WIDTH,
    height: HEIGHT,
    // Windows hosted runners can stop painting a permanently hidden surface.
    // Showing the frameless content window keeps capturePage deterministic; it
    // never changes the captured content rectangle.
    show: process.platform === 'win32',
    useContentSize: true, // 1920x1080 of actual web content, no chrome inset
    backgroundColor: nativeTheme.shouldUseDarkColors ? '#1C201D' : '#F5F0E6',
    webPreferences: {
      preload: join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
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

  try {
    for (const shot of SHOTS) {
      // The onboarding shot needs settings.onboarded=false; the rest need it true.
      repo.saveSettings({ onboarded: shot.onboarded });
      const settings = repo.getSettings();
      if (shot.onboarded && !settings.privacyConsentAt) {
        throw new Error('Screenshot seed did not clear the explicit privacy-consent gate.');
      }

      const ready = waitForReady();
      await Promise.all([
        withTimeout(loadApp(win), `Loading ${shot.file}`),
        ready, // app shell mounted (and read the current settings)
      ]);

      // Every shot waits for the renderer's settled signal. The onboarding shot
      // carries no route but still loads the hero illustration — a multi-megabyte
      // PNG that must finish decoding before the frame is clean — so it cannot
      // rely on a fixed delay (the decode races the capture and the gradient
      // fallback gets captured instead). The renderer signals only once the route
      // has painted and any hero image has decoded.
      const settled = waitForReady();
      win.webContents.send('screenshot:goto', { route: shot.route, theme: shot.theme });
      await settled;

      await delay(500); // a final beat for fonts/images
      // Capture an exact 1920x1080 rect — the xvfb backing buffer is one px short
      // of the requested content size, so pin the rect rather than trust the size.
      const image = await withTimeout(
        win.webContents.capturePage({ x: 0, y: 0, width: WIDTH, height: HEIGHT }),
        `Capturing ${shot.file}`,
      );
      const dest = join(outDir, shot.file);
      const size = image.getSize();
      if (size.width !== WIDTH || size.height !== HEIGHT) {
        throw new Error('Screenshot capture did not produce the required 1920x1080 frame.');
      }
      const png = image.toPNG();
      writeFileSync(dest, png);
      manifest.images.push({
        file: shot.file,
        route: shot.route ?? 'onboarding',
        theme: shot.theme,
        width: size.width,
        height: size.height,
        bytes: png.byteLength,
        sha256: createHash('sha256').update(png).digest('hex'),
        caption: shot.caption,
      });
      // eslint-disable-next-line no-console
      console.log(`[screenshot] wrote ${dest} (${image.getSize().width}x${image.getSize().height})`);
    }

    writeFileSync(join(outDir, 'manifest.json'), JSON.stringify(manifest, null, 2));
  } finally {
    if (!win.isDestroyed()) win.destroy();
  }
}
