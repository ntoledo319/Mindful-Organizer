import {
  app,
  BrowserWindow,
  ipcMain,
  shell,
  nativeTheme,
  globalShortcut,
  type IpcMainInvokeEvent,
} from 'electron';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { readFileSync, existsSync } from 'node:fs';
import { getDb, closeDb } from './db';
import * as repo from './repo';
import * as wellness from './wellness';
import * as presence from './presence';
import * as sessionSummary from './sessionSummary';
import type { HearthApi } from '../src/shared/ipc';

const __dirname = dirname(fileURLToPath(import.meta.url));

process.env.DIST = join(__dirname, '../dist');
process.env.PUBLIC = app.isPackaged ? process.env.DIST : join(__dirname, '../public');

const DEV_SERVER = process.env.VITE_DEV_SERVER_URL;

let win: BrowserWindow | null = null;
let quitting = false;

function openExternal(url: string): void {
  try {
    const protocol = new URL(url).protocol;
    if (['https:', 'http:', 'mailto:', 'tel:', 'sms:'].includes(protocol)) {
      void shell.openExternal(url);
    }
  } catch {
    // Ignore malformed or unsupported links instead of navigating the app away.
  }
}

function isTrustedIpcSender(event: IpcMainInvokeEvent): boolean {
  const frame = event.senderFrame;
  if (!frame || frame !== event.sender.mainFrame) return false;

  try {
    const senderUrl = new URL(frame.url);
    if (DEV_SERVER) {
      return senderUrl.origin === new URL(DEV_SERVER).origin;
    }

    const expected = pathToFileURL(join(process.env.DIST!, 'index.html'));
    return senderUrl.protocol === 'file:' && senderUrl.pathname === expected.pathname;
  } catch {
    return false;
  }
}

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
      sandbox: true,
    },
  });

  win.once('ready-to-show', () => win?.show());

  // Open external links in the real browser, never in-app.
  win.webContents.setWindowOpenHandler(({ url }) => {
    openExternal(url);
    return { action: 'deny' };
  });

  // Keep every external scheme out of the renderer while allowing explicit
  // crisis-call/text links to reach the operating system.
  win.webContents.on('will-navigate', (event, url) => {
    event.preventDefault();
    openExternal(url);
  });

  // With tray presence enabled, closing the window tucks Hearth away instead
  // of silently killing the acting layer. The tray's Quit action still exits.
  win.on('close', (event) => {
    if (!quitting && repo.getSettings().presence) {
      event.preventDefault();
      win?.hide();
    }
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
    replaceTaskWithSubtasks: async (id, subtasks) => repo.replaceTaskWithSubtasks(id, subtasks),
    updateTask: async (id, p) => repo.updateTask(id, p),
    toggleTask: async (id) => repo.toggleTask(id),
    deleteTask: async (id) => repo.deleteTask(id),

    listMoods: async (l) => repo.listMoods(l),
    createMood: async (i) => {
      const m = repo.createMood(i);
      presence.onReadingLogged(); // a fresh reading may ease the lights down
      return m;
    },
    listSleep: async (l) => repo.listSleep(l),
    createSleep: async (i) => {
      const s = repo.createSleep(i);
      presence.onReadingLogged();
      return s;
    },

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
    exportSessionSummary: async (d) => sessionSummary.exportSessionSummary(d, win),

    getSettings: async () => repo.getSettings(),
    saveSettings: async (p) => {
      const next = repo.saveSettings(p);
      presence.applySettings(next); // presence/quiet/focus/nudge toggles apply live
      return next;
    },

    getPresence: async () => presence.state(),
    setQuietActive: async (active) => presence.setQuietActive(active),
    startFocus: async (input) => presence.startFocus(input.seconds, input.intention ?? null),
    endFocus: async () => presence.endFocus(),

    listErpSessions: async (l) => repo.listErpSessions(l),
    createErpSession: async (i) => repo.createErpSession(i),
    
    listDiaryCards: async (l) => repo.listDiaryCards(l),
    createDiaryCard: async (i) => repo.createDiaryCard(i),
    
    listMedications: async () => repo.listMedications(),
    createMedication: async (i) => repo.createMedication(i),
    updateMedication: async (id, p) => repo.updateMedication(id, p),
    deleteMedication: async (id) => repo.deleteMedication(id),
    
    getGamification: async () => repo.getGamification(),

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
    ipcMain.handle(channel, (event, ...args: unknown[]) => {
      if (!isTrustedIpcSender(event)) {
        throw new Error('Rejected IPC request from an untrusted renderer.');
      }
      return (fn as (...a: unknown[]) => unknown)(...args);
    });
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
  presence.init(() => win); // the acting layer: tray, the dim, the focus hold

  app.on('activate', () => {
    if (win && !win.isDestroyed()) {
      win.show();
      win.focus();
    } else {
      createWindow();
    }
  });
  
  // Register global hotkey to toggle window visibility
  globalShortcut.register('CommandOrControl+Shift+H', () => {
    if (win) {
      if (win.isVisible()) {
        if (win.isFocused()) {
          win.hide();
        } else {
          win.show();
          win.focus();
        }
      } else {
        win.show();
        win.focus();
      }
    }
  });
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
  quitting = true;
  presence.dispose();
  closeDb();
});
