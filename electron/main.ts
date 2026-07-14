import {
  app,
  BrowserWindow,
  ipcMain,
  shell,
  nativeTheme,
  globalShortcut,
  dialog,
  type IpcMainInvokeEvent,
} from 'electron';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { readFileSync, existsSync, mkdirSync } from 'node:fs';
import { getDb, closeDb } from './db';
import * as repo from './repo';
import * as wellness from './wellness';
import * as presence from './presence';
import * as sessionSummary from './sessionSummary';
import * as dataLifecycle from './dataLifecycle';
import type { HearthApi } from '../src/shared/ipc';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Local screenshot/smoke harnesses set this to a contained workspace path.
// It must be applied before the first app.getPath('userData')/getDb call.
if (process.env.HEARTH_DATA_DIR) {
  const containedDataDir = resolve(process.env.HEARTH_DATA_DIR);
  mkdirSync(containedDataDir, { recursive: true });
  app.setPath('userData', containedDataDir);
}

process.env.DIST = join(__dirname, '../dist');
process.env.PUBLIC = app.isPackaged ? process.env.DIST : join(__dirname, '../public');

const DEV_SERVER = process.env.VITE_DEV_SERVER_URL;
const SCREENSHOT_MODE = process.env.HEARTH_SCREENSHOT === '1';
const SMOKE_MODE = process.env.HEARTH_SMOKE === '1';
const RELEASE_VALIDATION_MODE = process.env.HEARTH_RELEASE_VALIDATION === '1';

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

  win.once('ready-to-show', () => {
    if (!SMOKE_MODE) win?.show();
  });

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

  if (SMOKE_MODE) {
    const smokeTimeout = setTimeout(() => {
      console.error('[smoke] renderer did not become ready within 30 seconds');
      app.exit(1);
    }, 30_000);

    win.webContents.once('did-fail-load', (_event, code, description, url) => {
      clearTimeout(smokeTimeout);
      console.error(`[smoke] load failed (${code}) ${description}: ${url}`);
      app.exit(1);
    });
    win.webContents.once('render-process-gone', (_event, details) => {
      clearTimeout(smokeTimeout);
      console.error(`[smoke] renderer exited: ${details.reason}`);
      app.exit(1);
    });
    win.webContents.once('did-finish-load', () => {
      void win?.webContents
        .executeJavaScript(`
          new Promise((resolve) => {
            const deadline = Date.now() + 15000;
            const inspect = () => {
              const root = document.querySelector('#root');
              const hasBridge = typeof window.hearth?.getSettings === 'function';
              const hasHearthContent = (root?.textContent || '').includes('Hearth');
              const hasInteraction = Boolean(root?.querySelector('button, input, textarea'));
              if (hasBridge && hasHearthContent && hasInteraction) {
                resolve({ ok: true });
                return;
              }
              if (Date.now() >= deadline) {
                resolve({ ok: false, hasBridge, hasHearthContent, hasInteraction });
                return;
              }
              setTimeout(inspect, 100);
            };
            inspect();
          })
        `)
        .then((result: { ok?: boolean }) => {
          clearTimeout(smokeTimeout);
          if (!result?.ok) {
            console.error(`[smoke] renderer readiness check failed: ${JSON.stringify(result)}`);
            app.exit(1);
            return;
          }
          console.log('[smoke] secure storage, preload bridge, and first-run renderer loaded');
          app.exit(0);
        })
        .catch((error: unknown) => {
          clearTimeout(smokeTimeout);
          console.error('[smoke] renderer inspection failed', error);
          app.exit(1);
        });
    });
  }

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
    exportAllData: async () => dataLifecycle.exportAllData(win),
    deleteAllData: async () => {
      dataLifecycle.deleteAllData();
      presence.applySettings(repo.getSettings());
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

// Screenshot mode runs on CI hosts where hardware acceleration may be
// unavailable. Disabling hardware acceleration lets Chromium fall back to its
// software renderer; do not disable that fallback or weaken the sandbox.
// This must be set before app readiness, so it lives outside whenReady.
if (SCREENSHOT_MODE) {
  app.disableHardwareAcceleration();
  app.commandLine.appendSwitch('disable-gpu');
}

app.whenReady().then(async () => {
  if (RELEASE_VALIDATION_MODE) {
    try {
      const { runExactCandidateValidation } = await import('./releaseValidation');
      await runExactCandidateValidation();
      console.log('[release-validation] packaged Windows data lifecycle passed');
      app.exit(0);
    } catch (error) {
      console.error('[release-validation] failed', error);
      app.exit(1);
    }
    return;
  }

  try {
    getDb(); // open + migrate before the window can call in
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    dialog.showErrorBox('Hearth could not open secure storage', message);
    app.exit(1);
    return;
  }
  registerIpc();

  // Dev-only screenshot mode: seed demo data, capture the Store listing images,
  // then quit. Gated behind HEARTH_SCREENSHOT so it can't fire in a real launch.
  if (SCREENSHOT_MODE) {
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
  if (SMOKE_MODE) return;
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
