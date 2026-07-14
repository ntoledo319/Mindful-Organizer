import {
  app,
  BrowserWindow,
  Tray,
  Menu,
  Notification,
  nativeImage,
  screen,
  type NativeImage,
} from 'electron';
import { deflateSync } from 'node:zlib';
import * as repo from './repo';
import * as wellness from './wellness';
import type { Settings, PresenceState, PresenceUpdate, QuietMode } from '../src/shared/types';

// The acting layer. Everything above the data layer is a tracker; this is the
// part of Hearth that reaches past its own window and changes the room you work
// in — it dims the screen when your own readings say you're drained, and it
// holds a calm hold over everything else during a focus block. It owns no data;
// it reads the same local SQLite the rest of the app does and acts on it.
//
// Hard rule for a mental-health tool: every hold has an obvious, immediate way
// out (a visible link, the Escape key, and the tray). It never traps you.

const NIGHT = '#1c201d';

let getMainWindow: (() => BrowserWindow | null) | null = null;
let settings: Settings | null = null;

let tray: Tray | null = null;
let dimWin: BrowserWindow | null = null;
let focusWin: BrowserWindow | null = null;

let manualOverride: boolean | null = null; // momentary "dim now / brighten now"
let quietActive = false;

let focusTimer: ReturnType<typeof setTimeout> | null = null;
let focus: PresenceState['focus'] = null;

let autoTimer: ReturnType<typeof setInterval> | null = null;
let lastUrgentNudge = 0;

// --- public surface --------------------------------------------------------

export function init(mainWindow: () => BrowserWindow | null): void {
  getMainWindow = mainWindow;
  applySettings(repo.getSettings());
}

export function applySettings(next: Settings): void {
  const prevMode = settings?.quietMode;
  settings = next;

  // A migrated profile is encrypted before the renderer opens, then gated at
  // onboarding until the user explicitly consents. Do not let records from
  // that profile affect a dim window, tray action, notification, or timer
  // before consent is recorded.
  if (!next.privacyConsentAt) {
    manualOverride = null;
    if (autoTimer) clearInterval(autoTimer);
    autoTimer = null;
    showDim(false);
    destroyTray();
    return;
  }

  if (!autoTimer) {
    // Re-read the room every few minutes so a quiet evening eases in on its own.
    autoTimer = setInterval(() => evaluateQuiet(), 3 * 60 * 1000);
  }
  if (next.quietMode !== prevMode) manualOverride = null; // a mode change is a fresh intent
  if (next.presence) ensureTray();
  else destroyTray();
  evaluateQuiet();
  refreshTrayMenu();
}

// A new reading is a fresh signal — let auto take the wheel back from any
// momentary manual override, then re-evaluate the dim.
export function onReadingLogged(): void {
  manualOverride = null;
  evaluateQuiet();
  maybeNudgeUrgent();
}

export function state(): PresenceState {
  return {
    quietActive,
    quietMode: settings?.quietMode ?? 'auto',
    focus,
  };
}

export function setQuietActive(active: boolean): PresenceState {
  manualOverride = active;
  evaluateQuiet();
  return state();
}

export function startFocus(seconds: number, intention: string | null): PresenceState {
  endFocusInternal(false); // never stack two holds
  const safe = Math.max(60, Math.min(seconds, 4 * 60 * 60));
  const endsAt = new Date(Date.now() + safe * 1000).toISOString();
  focus = { endsAt, intention, seconds: safe };
  try {
    raiseFocusWindow();
  } catch (err) {
    console.error('[presence] focus window failed:', err);
  }
  focusTimer = setTimeout(() => endFocusInternal(true), safe * 1000);
  emit();
  return state();
}

export function endFocus(): PresenceState {
  endFocusInternal(false);
  return state();
}

export function dispose(): void {
  if (autoTimer) clearInterval(autoTimer);
  if (focusTimer) clearTimeout(focusTimer);
  autoTimer = focusTimer = null;
  closeWindow(dimWin);
  closeWindow(focusWin);
  dimWin = focusWin = null;
  destroyTray();
  settings = null;
  getMainWindow = null;
}

// --- quiet / dim -----------------------------------------------------------

function drainedNow(): boolean {
  const last = repo.listMoods(1)[0];
  if (!last) return false;
  const energyLow = last.energyLevel != null && last.energyLevel <= 3;
  const moodLow = last.moodScore <= 3;
  return energyLow || moodLow;
}

function evaluateQuiet(): void {
  if (!settings) return;
  // A focus hold owns the screen on its own; don't layer a second wash under it.
  if (focus) {
    showDim(false);
    return;
  }
  const base =
    settings.quietMode === 'on' ? true : settings.quietMode === 'off' ? false : drainedNow();
  const target = manualOverride !== null ? manualOverride : base;
  showDim(target);
}

function showDim(on: boolean): void {
  if (on === quietActive && (!on || dimWin)) {
    if (on && dimWin) dimWin.setOpacity(clampDim());
    return;
  }
  if (on) {
    try {
      ensureDimWindow();
      dimWin?.setOpacity(clampDim());
      dimWin?.showInactive();
      quietActive = true;
    } catch (err) {
      console.error('[presence] dim window failed:', err);
      quietActive = false;
    }
  } else {
    dimWin?.hide();
    quietActive = false;
  }
  emit();
  refreshTrayMenu();
}

function clampDim(): number {
  const d = settings?.quietDim ?? 0.4;
  return Math.max(0.1, Math.min(d, 0.85));
}

function ensureDimWindow(): void {
  if (dimWin && !dimWin.isDestroyed()) return;
  const b = screen.getPrimaryDisplay().bounds;
  dimWin = new BrowserWindow({
    x: b.x,
    y: b.y,
    width: b.width,
    height: b.height,
    frame: false,
    transparent: true,
    backgroundColor: '#00000000',
    resizable: false,
    movable: false,
    minimizable: false,
    maximizable: false,
    fullscreenable: false,
    skipTaskbar: true,
    focusable: false,
    hasShadow: false,
    show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false },
  });
  dimWin.setIgnoreMouseEvents(true, { forward: true }); // the dim never eats a click
  dimWin.setAlwaysOnTop(true, 'screen-saver');
  dimWin.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  // A warm vignette rather than a flat gray film — the lights lowering, not a screen off.
  const html = `<!doctype html><meta charset="utf-8"><style>
    html,body{margin:0;height:100%;overflow:hidden;background:transparent}
    .v{position:fixed;inset:0;background:radial-gradient(ellipse at 50% 42%,
       rgba(40,46,41,0.55) 0%, rgba(28,32,29,0.86) 55%, ${NIGHT} 100%)}
  </style><div class="v"></div>`;
  void dimWin.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(html));
  dimWin.on('closed', () => {
    dimWin = null;
  });
}

// --- focus hold ------------------------------------------------------------

function raiseFocusWindow(): void {
  const b = screen.getPrimaryDisplay().bounds;
  focusWin = new BrowserWindow({
    x: b.x,
    y: b.y,
    width: b.width,
    height: b.height,
    frame: false,
    transparent: true,
    backgroundColor: '#00000000',
    resizable: false,
    movable: false,
    fullscreenable: false,
    skipTaskbar: true,
    hasShadow: false,
    show: false,
    webPreferences: { contextIsolation: true, nodeIntegration: false },
  });
  focusWin.setAlwaysOnTop(true, 'screen-saver');
  focusWin.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });

  const intention = focus?.intention?.trim();
  const endsAt = focus?.endsAt ?? new Date().toISOString();
  const html = focusHtml(endsAt, intention || null);
  void focusWin.loadURL('data:text/html;charset=utf-8,' + encodeURIComponent(html));
  focusWin.once('ready-to-show', () => focusWin?.show());

  // Three ways out, always: the visible link, Escape, and the tray item.
  focusWin.webContents.on('will-navigate', (e) => {
    e.preventDefault();
    endFocusInternal(false);
  });
  focusWin.webContents.on('before-input-event', (_e, input) => {
    if (input.type === 'keyDown' && input.key === 'Escape') endFocusInternal(false);
  });
  focusWin.on('closed', () => {
    focusWin = null;
  });
}

function focusHtml(endsAt: string, intention: string | null): string {
  const line = intention
    ? `Holding the door for: <span class="i">${escapeHtml(intention)}</span>`
    : 'One thing, protected. Everything else can wait.';
  return `<!doctype html><meta charset="utf-8"><style>
    html,body{margin:0;height:100%;overflow:hidden;color:#f5f0e6;
      font-family:-apple-system,Segoe UI,Roboto,system-ui,sans-serif;
      background:radial-gradient(ellipse at 50% 38%, #2a302b 0%, #1c201d 70%, #14160f 100%)}
    .wrap{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;
      justify-content:center;gap:26px;text-align:center;-webkit-app-region:no-drag}
    .pulse{width:120px;height:120px;border-radius:50%;
      background:radial-gradient(circle at 50% 45%, rgba(159,179,140,0.9), rgba(159,179,140,0.15));
      animation:breathe 9s ease-in-out infinite}
    @keyframes breathe{0%,100%{transform:scale(0.82);opacity:.65}50%{transform:scale(1.12);opacity:1}}
    .time{font-size:64px;font-weight:600;font-variant-numeric:tabular-nums;letter-spacing:1px}
    .line{font-size:16px;color:rgba(245,240,230,0.72);max-width:30rem;line-height:1.5}
    .i{color:#bfd0a8;font-weight:600}
    .exit{margin-top:10px;font-size:13px;color:rgba(245,240,230,0.5);text-decoration:none;
      border-bottom:1px solid rgba(245,240,230,0.25);padding-bottom:2px}
    .exit:hover{color:rgba(245,240,230,0.85)}
    .hint{font-size:11px;color:rgba(245,240,230,0.32);margin-top:2px}
  </style>
  <div class="wrap">
    <div class="pulse"></div>
    <div class="time" id="t">--:--</div>
    <div class="line">${line}</div>
    <a class="exit" href="hearth:end">End the block early</a>
    <div class="hint">or press Esc</div>
  </div>
  <script>
    var target = new Date(${JSON.stringify(endsAt)}).getTime();
    function tick(){
      var ms = Math.max(0, target - Date.now());
      var s = Math.round(ms/1000);
      var mm = String(Math.floor(s/60)).padStart(2,'0');
      var ss = String(s%60).padStart(2,'0');
      document.getElementById('t').textContent = mm+':'+ss;
    }
    tick(); setInterval(tick, 1000);
  </script>`;
}

function endFocusInternal(completed: boolean): void {
  if (focusTimer) clearTimeout(focusTimer);
  focusTimer = null;
  const was = focus;
  focus = null;
  closeWindow(focusWin);
  focusWin = null;
  if (was) {
    const elapsed = Math.max(
      0,
      Math.round((Date.now() - (new Date(was.endsAt).getTime() - was.seconds * 1000)) / 1000),
    );
    try {
      repo.logPractice({
        kind: 'focus',
        technique: `${Math.round(was.seconds / 60)}-minute focus block`,
        durationSeconds: Math.min(elapsed, was.seconds),
      });
    } catch (err) {
      console.error('[presence] could not log focus block:', err);
    }
    if (completed) nudge('Focus block complete', 'Well held. Come back when you want to.');
  }
  evaluateQuiet(); // the dim may take back over now that the hold is gone
  emit();
  refreshTrayMenu();
}

// --- nudges ----------------------------------------------------------------

function nudge(title: string, body: string): void {
  if (!settings?.nudges) return;
  try {
    if (!Notification.isSupported()) return;
    new Notification({ title, body, silent: false }).show();
  } catch (err) {
    console.error('[presence] notification failed:', err);
  }
}

// Conservative on purpose: only the most urgent signal, at most once an hour,
// and it only opens the app — it never diagnoses.
function maybeNudgeUrgent(): void {
  if (!settings?.nudges) return;
  const now = Date.now();
  if (now - lastUrgentNudge < 60 * 60 * 1000) return;
  let urgent = false;
  try {
    urgent = wellness.detectCrisisSignals().some((s) => s.severity === 'urgent');
  } catch {
    urgent = false;
  }
  if (!urgent) return;
  lastUrgentNudge = now;
  try {
    if (!Notification.isSupported()) return;
    const n = new Notification({
      title: 'Hearth is here',
      body: 'A hard moment, maybe. Your crisis plan is one click away.',
      silent: true,
    });
    n.on('click', () => {
      const w = getMainWindow?.();
      if (w) {
        if (w.isMinimized()) w.restore();
        w.show();
        w.focus();
      }
    });
    n.show();
  } catch (err) {
    console.error('[presence] urgent nudge failed:', err);
  }
}

// --- tray ------------------------------------------------------------------

function ensureTray(): void {
  if (tray) return;
  try {
    tray = new Tray(trayImage());
    tray.setToolTip('Hearth');
    refreshTrayMenu();
    tray.on('click', () => showMainWindow());
  } catch (err) {
    console.error('[presence] tray failed:', err);
    tray = null;
  }
}

function destroyTray(): void {
  if (tray) {
    tray.destroy();
    tray = null;
  }
}

function refreshTrayMenu(): void {
  if (!tray || !settings) return;
  const mode = settings.quietMode;
  const setMode = (m: QuietMode) => persistFromTray({ quietMode: m });

  const menu = Menu.buildFromTemplate([
    { label: 'Open Hearth', click: () => showMainWindow() },
    { type: 'separator' },
    {
      label: 'Quiet — dim when drained',
      submenu: [
        { label: 'Off', type: 'radio', checked: mode === 'off', click: () => setMode('off') },
        { label: 'Automatic', type: 'radio', checked: mode === 'auto', click: () => setMode('auto') },
        { label: 'Always on', type: 'radio', checked: mode === 'on', click: () => setMode('on') },
      ],
    },
    {
      label: quietActive ? 'Brighten now' : 'Dim now',
      click: () => setQuietActive(!quietActive),
    },
    { type: 'separator' },
    focus
      ? { label: 'End focus block', click: () => endFocusInternal(false) }
      : {
          label: 'Hold a focus block',
          submenu: [15, 25, 50].map((m) => ({
            label: `${m} minutes`,
            click: () => startFocus(m * 60, null),
          })),
        },
    { type: 'separator' },
    { label: 'Quit Hearth', click: () => app.quit() },
  ]);
  tray.setContextMenu(menu);
}

function persistFromTray(patch: Partial<Settings>): void {
  try {
    const next = repo.saveSettings(patch);
    applySettings(next);
    emit(); // push the new settings down to the open window too
  } catch (err) {
    console.error('[presence] tray persist failed:', err);
  }
}

function showMainWindow(): void {
  const w = getMainWindow?.();
  if (w) {
    if (w.isMinimized()) w.restore();
    w.show();
    w.focus();
  }
}

// --- plumbing --------------------------------------------------------------

function emit(): void {
  const w = getMainWindow?.();
  if (!w || w.isDestroyed() || !settings) return;
  const payload: PresenceUpdate = { state: state(), settings };
  w.webContents.send('presence:update', payload);
}

function closeWindow(w: BrowserWindow | null): void {
  if (w && !w.isDestroyed()) w.close();
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// --- tray icon: a warm ember dot, encoded as a PNG at runtime so there is no
// binary asset to ship or lose. RGBA → minimal PNG via zlib. ----------------

function trayImage(): NativeImage {
  const size = 18;
  const px = Buffer.alloc(size * size * 4);
  const cx = size / 2 - 0.5;
  const cy = size / 2 - 0.5;
  const r = size / 2 - 1;
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const d = Math.hypot(x - cx, y - cy);
      const i = (y * size + x) * 4;
      // soft edge so it reads as a dot, not a square
      const a = d > r ? 0 : d > r - 1.5 ? Math.round(255 * (r - d) / 1.5) : 255;
      const t = Math.max(0, Math.min(1, d / r)); // center→edge
      px[i] = Math.round(214 - 40 * t); // warm ember → sage
      px[i + 1] = Math.round(150 + 30 * t);
      px[i + 2] = Math.round(96 + 44 * t);
      px[i + 3] = a;
    }
  }
  const png = encodePng(size, size, px);
  const img = nativeImage.createFromBuffer(png);
  return img.isEmpty() ? nativeImage.createEmpty() : img;
}

function encodePng(width: number, height: number, rgba: Buffer): Buffer {
  const sig = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // color type RGBA
  const stride = width * 4;
  const raw = Buffer.alloc((stride + 1) * height);
  for (let y = 0; y < height; y++) {
    raw[y * (stride + 1)] = 0; // no filter
    rgba.copy(raw, y * (stride + 1) + 1, y * stride, (y + 1) * stride);
  }
  const idat = deflateSync(raw);
  return Buffer.concat([sig, chunk('IHDR', ihdr), chunk('IDAT', idat), chunk('IEND', Buffer.alloc(0))]);
}

function chunk(type: string, data: Buffer): Buffer {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const t = Buffer.from(type, 'ascii');
  const body = Buffer.concat([t, data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(body) >>> 0, 0);
  return Buffer.concat([len, body, crc]);
}

const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(buf: Buffer): number {
  let c = 0xffffffff;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
