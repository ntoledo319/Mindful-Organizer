import { useEffect, useRef, useState } from 'react';
import { useStore } from '../state/store';
import { type Settings, type QuietMode, type AppInfo } from '@shared/types';
import { MAX_DAILY_SPOONS, MIN_DAILY_SPOONS } from '@shared/spoons';
import { api } from '../lib/api';
import { PageHeader, Scale } from '../components/ui';
import { SunIcon, MoonIcon } from '../components/icons';

const THEMES: { id: Settings['theme']; label: string }[] = [
  { id: 'light', label: 'Light' },
  { id: 'dark', label: 'Dark' },
  { id: 'system', label: 'Match system' },
];

const QUIET_MODES: { id: QuietMode; label: string }[] = [
  { id: 'off', label: 'Off' },
  { id: 'auto', label: 'Automatic' },
  { id: 'on', label: 'Always on' },
];

function Toggle({ on, onChange, label }: { on: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <button
      role="switch"
      aria-checked={on}
      aria-label={label}
      onClick={() => onChange(!on)}
      className={`relative h-6 w-11 shrink-0 rounded-full transition-colors focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 focus:outline-none ${
        on ? 'bg-brand dark:bg-night-brand' : 'bg-base-border dark:bg-night-border'
      }`}
    >
      <span
        className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow-sm transition-transform ${
          on ? 'translate-x-5' : 'translate-x-0.5'
        }`}
      />
    </button>
  );
}

function SettingRow({
  title,
  desc,
  on,
  onChange,
}: {
  title: string;
  desc: string;
  on: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <div className="flex items-start justify-between gap-6">
      <div>
        <p className="text-base font-medium text-text-primary dark:text-night-text">{title}</p>
        <p className="mt-1 text-sm text-text-muted dark:text-night-muted">{desc}</p>
      </div>
      <div className="pt-1">
        <Toggle on={on} onChange={onChange} label={title} />
      </div>
    </div>
  );
}

export function SettingsScreen() {
  const { settings, presence, saveSettings, setQuiet } = useStore();
  const [exportState, setExportState] = useState<'idle' | 'saving' | 'saved' | 'cancelled' | 'error'>('idle');
  const [eraseArmed, setEraseArmed] = useState(false);
  const [eraseText, setEraseText] = useState('');
  const [eraseState, setEraseState] = useState<'idle' | 'deleting' | 'error'>('idle');

  // The name field persists to a local draft first: saving on every keystroke
  // meant a full database serialize + encrypt + two atomic writes per character.
  const serverName = settings?.displayName ?? '';
  const [nameDraft, setNameDraft] = useState(serverName);
  const nameSaveTimer = useRef<number | null>(null);
  const pendingName = useRef<string | null>(null);

  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'error'>('idle');

  // Keep the draft in step with external changes (presence pushes, other saves).
  useEffect(() => {
    setNameDraft(serverName);
  }, [serverName]);

  // Flush a pending debounced save when the screen unmounts.
  useEffect(() => {
    return () => {
      if (nameSaveTimer.current !== null) window.clearTimeout(nameSaveTimer.current);
      if (pendingName.current !== null) void saveSettings({ displayName: pendingName.current });
    };
  }, [saveSettings]);

  useEffect(() => {
    let cancelled = false;
    void api
      .getAppInfo()
      .then((info) => {
        if (!cancelled) setAppInfo(info);
      })
      .catch(() => {
        // The About card shows an "unavailable" note instead of crashing.
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (!settings) return null;

  const changeName = (value: string) => {
    setNameDraft(value);
    pendingName.current = value;
    if (nameSaveTimer.current !== null) window.clearTimeout(nameSaveTimer.current);
    nameSaveTimer.current = window.setTimeout(() => {
      nameSaveTimer.current = null;
      pendingName.current = null;
      void saveSettings({ displayName: value });
    }, 500);
  };

  const flushNameSave = () => {
    if (nameSaveTimer.current !== null) {
      window.clearTimeout(nameSaveTimer.current);
      nameSaveTimer.current = null;
    }
    if (pendingName.current !== null) {
      const value = pendingName.current;
      pendingName.current = null;
      void saveSettings({ displayName: value });
    }
  };

  const copyDiagnostics = async () => {
    if (!appInfo) return;
    try {
      await navigator.clipboard.writeText(`Paulatim ${appInfo.version} · ${appInfo.os} · ${appInfo.arch}`);
      setCopyState('copied');
    } catch {
      setCopyState('error');
    }
  };

  const exportAllData = async () => {
    setExportState('saving');
    try {
      const result = await api.exportAllData();
      setExportState(result.status === 'saved' ? 'saved' : 'cancelled');
    } catch {
      setExportState('error');
    }
  };

  const eraseAllData = async () => {
    if (eraseText !== 'ERASE') return;
    setEraseState('deleting');
    try {
      await api.deleteAllData();
      window.location.reload();
    } catch {
      setEraseState('error');
    }
  };

  return (
    <div>
      <PageHeader title="Settings" subtitle="Tune Paulatim to you. Everything here stays on this machine." />

      <div className="space-y-6">
        <div className="surface-card p-6">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Name</span>
            <input
              className="field max-w-sm text-base"
              value={nameDraft}
              placeholder="What should Paulatim call you?"
              onChange={(e) => changeName(e.target.value)}
              onBlur={flushNameSave}
            />
          </label>
        </div>

        <div className="surface-card p-6">
          <h3 className="mb-4 text-base font-medium text-text-primary dark:text-night-text">Appearance</h3>
          <div className="flex gap-3">
            {THEMES.map((t) => (
              <button
                key={t.id}
                onClick={() => void saveSettings({ theme: t.id })}
                className={settings.theme === t.id ? 'btn-primary' : 'btn-ghost'}
              >
                {t.id === 'light' && <SunIcon width={16} height={16} />}
                {t.id === 'dark' && <MoonIcon width={16} height={16} />}
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* The acting layer — the part of Paulatim that reaches past its own window.
            Free for everyone, always. Never gated. */}
        <div className="surface-card space-y-6 p-6">
          <div className="border-b border-base-border dark:border-night-border pb-4">
            <h3 className="text-lg font-medium text-text-primary dark:text-night-text">How Paulatim shows up</h3>
            <p className="mt-1 text-sm text-text-muted dark:text-night-text/80">
              Beyond its own window, Paulatim can lower the lights when your readings say you're drained, and hold the
              door while you focus. All of it runs on this machine.
            </p>
          </div>

          <SettingRow
            title="Live in the tray"
            desc="A quiet way back to Paulatim, and the quick controls, from your menu bar."
            on={settings.presence}
            onChange={(v) => void saveSettings({ presence: v })}
          />

          <div className="space-y-4 border-t border-base-border pt-6 dark:border-night-border">
            <div className="flex items-start justify-between gap-6">
              <div>
                <p className="text-base font-medium text-text-primary dark:text-night-text">Dim when you're drained</p>
                <p className="mt-1 text-sm text-text-muted dark:text-night-text/80">
                  A warm wash lowers over the screen so a tired hour stops shouting at you.
                </p>
              </div>
              {presence && (
                <button
                  onClick={() => void setQuiet(!presence.quietActive)}
                  className={presence.quietActive ? 'btn-primary shrink-0' : 'btn-ghost shrink-0'}
                >
                  {presence.quietActive ? 'Brighten now' : 'Dim now'}
                </button>
              )}
            </div>
            <div className="flex gap-3 pt-2">
              {QUIET_MODES.map((m) => (
                <button
                  key={m.id}
                  onClick={() => void saveSettings({ quietMode: m.id })}
                  className={settings.quietMode === m.id ? 'btn-primary' : 'btn-ghost'}
                >
                  {m.label}
                </button>
              ))}
            </div>
            {settings.quietMode !== 'off' && (
              <div className="max-w-sm pt-4">
                <Scale
                  label="How deep the dim goes"
                  value={Math.round(settings.quietDim * 10)}
                  min={1}
                  max={8}
                  onChange={(v) => void saveSettings({ quietDim: v / 10 })}
                />
              </div>
            )}
          </div>

          <div className="space-y-6 border-t border-base-border pt-6 dark:border-night-border">
            <SettingRow
              title="Hold the door on focus blocks"
              desc="A calm full-screen hold while a focus block runs. End it anytime — the link, Esc, or the tray."
              on={settings.focusGuard}
              onChange={(v) => void saveSettings({ focusGuard: v })}
            />
            <SettingRow
              title="Gentle nudges"
              desc="A soft note when a focus block finishes, or when a hard moment shows in your own signals. Never a diagnosis."
              on={settings.nudges}
              onChange={(v) => void saveSettings({ nudges: v })}
            />
          </div>
        </div>

        <div className="surface-card p-6">
          <h3 className="mb-2 text-base font-medium text-text-primary dark:text-night-text">Daily energy budget</h3>
          <p className="mb-4 text-sm text-text-muted dark:text-night-text/80">
            Set the amount you want to plan against today. Paulatim does not infer this number from a diagnosis or a check-in.
          </p>
          <div className="max-w-sm">
            <Scale
              label="Daily energy budget"
              value={settings.dailySpoons}
              min={MIN_DAILY_SPOONS}
              max={MAX_DAILY_SPOONS}
              onChange={(value) => void saveSettings({ dailySpoons: value })}
            />
            <p className="mt-2 text-xs leading-relaxed text-text-muted dark:text-night-muted">
              You choose this number directly. Check-ins never lower it behind your back.
            </p>
          </div>
        </div>

        <div className="surface-card space-y-5 p-6">
          <div>
            <h3 className="mb-2 text-base font-medium text-text-primary dark:text-night-text">Privacy and your data</h3>
            <p className="text-sm leading-relaxed text-text-muted dark:text-night-text/80">
              Paulatim stores an AES-256-GCM encrypted database on this device. Its random key is protected by your
              operating-system sign-in. There is no account, sync, analytics, telemetry, or record upload. Consent
              was recorded {new Date(settings.privacyConsentAt ?? '').toLocaleString()}.
            </p>
          </div>

          <div className="border-t border-base-border pt-5 dark:border-night-border">
            <h4 className="text-sm font-medium text-text-primary dark:text-night-text">Take a copy</h4>
            <p className="mt-1 text-sm leading-relaxed text-text-muted dark:text-night-muted">
              Export all records and settings as readable JSON. The exported file is intentionally unencrypted so
              you can use it elsewhere; protect it like any sensitive document.
            </p>
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <button className="btn-ghost" onClick={() => void exportAllData()} disabled={exportState === 'saving'}>
                {exportState === 'saving' ? 'Choosing a location…' : 'Export all data'}
              </button>
              {exportState === 'saved' && <span className="text-sm text-semantic-success">Export saved.</span>}
              {exportState === 'cancelled' && <span className="text-sm text-text-muted dark:text-night-muted">Export cancelled.</span>}
              {exportState === 'error' && <span className="text-sm text-semantic-error">Export failed. Your database was not changed.</span>}
            </div>
          </div>

          <div className="border-t border-semantic-error/25 pt-5">
            <h4 className="text-sm font-medium text-semantic-error">Withdraw consent and erase everything</h4>
            <p className="mt-1 text-sm leading-relaxed text-text-muted dark:text-night-muted">
              This destroys every Paulatim record, encrypted rollback snapshot, and the key that decrypts them, then
              returns to a fresh empty store. It cannot erase PDFs or JSON files you previously exported.
            </p>
            {!eraseArmed ? (
              <button className="btn-ghost mt-3" onClick={() => setEraseArmed(true)}>
                Erase all Paulatim data…
              </button>
            ) : (
              <div className="mt-4 rounded-soft border border-semantic-error/30 bg-semantic-error/5 p-4">
                <label className="block text-sm text-text-primary dark:text-night-text">
                  Type <span className="font-semibold">ERASE</span> to confirm permanent deletion.
                  <input
                    className="field mt-2 max-w-xs"
                    value={eraseText}
                    onChange={(event) => setEraseText(event.target.value)}
                    autoComplete="off"
                    spellCheck={false}
                  />
                </label>
                <div className="mt-3 flex flex-wrap gap-2">
                  <button
                    className="btn-primary bg-semantic-error hover:bg-semantic-error/90"
                    onClick={() => void eraseAllData()}
                    disabled={eraseText !== 'ERASE' || eraseState === 'deleting'}
                  >
                    {eraseState === 'deleting' ? 'Erasing…' : 'Permanently erase data'}
                  </button>
                  <button
                    className="btn-ghost"
                    onClick={() => {
                      setEraseArmed(false);
                      setEraseText('');
                      setEraseState('idle');
                    }}
                    disabled={eraseState === 'deleting'}
                  >
                    Cancel
                  </button>
                </div>
                {eraseState === 'error' && (
                  <p className="mt-3 text-sm text-semantic-error">
                    Paulatim could not verify complete cleanup. Close and reopen Paulatim; it will resume the requested deletion before opening storage.
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="surface-card p-6">
          <h3 className="mb-2 text-base font-medium text-text-primary dark:text-night-text">About Paulatim</h3>
          <p className="text-sm leading-relaxed text-text-muted dark:text-night-muted">
            {appInfo
              ? `Version ${appInfo.version} · ${appInfo.os} · ${appInfo.arch}`
              : 'Version information is unavailable right now.'}
          </p>
          {appInfo && (
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <button className="btn-ghost" onClick={() => void copyDiagnostics()}>
                Copy diagnostics
              </button>
              {copyState === 'copied' && (
                <span className="text-sm text-semantic-success">Copied — paste it into the bug report form.</span>
              )}
              {copyState === 'error' && (
                <span className="text-sm text-semantic-error">Copy failed. You can copy the version line above by hand.</span>
              )}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
