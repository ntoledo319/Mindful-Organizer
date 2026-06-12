import { app, BrowserWindow, ipcMain, shell, nativeTheme } from 'electron';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync } from 'node:fs';
import { getDb, closeDb } from './db';
import * as repo from './repo';
import * as wellness from './wellness';
import type { HearthApi } from '../src/shared/ipc';

const __dirname = dirname(fileURLToPath(import.meta.url));

process.env.DIST = join(__dirname, '../dist');
process.env.PUBLIC = app.isPackaged ? process.env.DIST : join(__dirname, '../public');

const DEV_SERVER = process.env.VITE_DEV_SERVER_URL;

let win: BrowserWindow | null = null;

function heroPath(): string {
  // Packaged: extraResources copies it next to the app. Dev: read from repo.
  const packaged = join(process.resourcesPath ?? '', 'hero-illustration.png');
  if (app.isPackaged && existsSync(packaged)) return packaged;
  return join(__dirname, '../resources/hero-illustration.png');
}

function createWindow(): void {
  win = new BrowserWindow({
    width: 1240,
    height: 820,
    minWidth: 940,
    minHeight: 640,
    backgroundColor: nativeTheme.shouldUseDarkColors ? '#1C201D' : '#F5F0E6',
    titleBarStyle: 'hiddenInset',
    show: false,
    webPreferences: {
      preload: join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  });

  win.once('ready-to-show', () => win?.show());

  // Open external links in the real browser, never in-app.
  win.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http')) void shell.openExternal(url);
    return { action: 'deny' };
  });

  if (DEV_SERVER) {
    void win.loadURL(DEV_SERVER);
  } else {
    void win.loadFile(join(process.env.DIST!, 'index.html'));
  }
}

// --- IPC: one handler per HearthApi method --------------------------------

function registerIpc(): void {
  const handlers: HearthApi = {
    listTasks: async (inc) => repo.listTasks(inc),
    createTask: async (i) => repo.createTask(i),
    updateTask: async (id, p) => repo.updateTask(id, p),
    toggleTask: async (id) => repo.toggleTask(id),
    deleteTask: async (id) => repo.deleteTask(id),

    listMoods: async (l) => repo.listMoods(l),
    createMood: async (i) => repo.createMood(i),
    listSleep: async (l) => repo.listSleep(l),
    createSleep: async (i) => repo.createSleep(i),

    listJournal: async (l) => repo.listJournal(l),
    createJournal: async (i) => repo.createJournal(i),
    deleteJournal: async (id) => repo.deleteJournal(id),

    listPractices: async (l) => repo.listPractices(l),
    logPractice: async (i) => repo.logPractice(i),

    getCrisisPlan: async () => repo.getCrisisPlan(),
    saveCrisisPlan: async (p) => repo.saveCrisisPlan(p),

    getSnapshot: async () => wellness.snapshot(),
    getBriefing: async () => wellness.dailyBriefing(),
    getTrends: async (d) => wellness.trends(d),

    getSettings: async () => repo.getSettings(),
    saveSettings: async (p) => repo.saveSettings(p),

    heroDataUrl: async () => {
      try {
        const buf = readFileSync(heroPath());
        return `data:image/png;base64,${buf.toString('base64')}`;
      } catch {
        return null;
      }
    },
  };

  for (const [channel, fn] of Object.entries(handlers)) {
    ipcMain.handle(channel, (_e, ...args: unknown[]) =>
      (fn as (...a: unknown[]) => unknown)(...args),
    );
  }
}

// Screenshot mode runs headless under xvfb where the GPU stack is unavailable;
// software rendering keeps capturePage from stalling on GPU init. Must be set
// before app is ready, so it lives outside whenReady.
if (process.env.HEARTH_SCREENSHOT === '1') {
  app.disableHardwareAcceleration();
  app.commandLine.appendSwitch('disable-gpu');
  app.commandLine.appendSwitch('disable-software-rasterizer');
  app.commandLine.appendSwitch('no-sandbox');
}

app.whenReady().then(async () => {
  getDb(); // open + migrate before the window can call in
  registerIpc();

  // Dev-only screenshot mode: seed demo data, capture the Store listing images,
  // then quit. Gated behind HEARTH_SCREENSHOT so it can't fire in a real launch.
  if (process.env.HEARTH_SCREENSHOT === '1') {
    const { runScreenshots } = await import('./screenshot');
    try {
      await runScreenshots();
    } catch (err) {
      console.error('[screenshot] failed:', err);
      app.exit(1);
      return;
    }
    app.quit();
    return;
  }

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  closeDb();
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', closeDb);
