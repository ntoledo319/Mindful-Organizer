import { useStore } from '../state/store';
import { CONDITIONS, type Condition, type Settings, type QuietMode } from '@shared/types';
import { dailySpoonsFor } from '@shared/spoons';
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
          on ? 'translate-x-5.5' : 'translate-x-0.5'
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
  if (!settings) return null;

  const toggleCondition = (c: Condition) => {
    const conditions = settings.conditions.includes(c)
      ? settings.conditions.filter((x) => x !== c)
      : [...settings.conditions, c];
    void saveSettings({ conditions, dailySpoons: dailySpoonsFor(conditions) });
  };

  return (
    <div>
      <PageHeader title="Settings" subtitle="Tune Hearth to you. Everything here stays on this machine." />

      <div className="space-y-6">
        <div className="surface-card p-6">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Name</span>
            <input
              className="field max-w-sm text-base"
              value={settings.displayName}
              placeholder="What should Hearth call you?"
              onChange={(e) => void saveSettings({ displayName: e.target.value })}
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

        {/* The acting layer — the part of Hearth that reaches past its own window.
            Free for everyone, always. Never gated. */}
        <div className="surface-card space-y-6 p-6">
          <div className="border-b border-base-border dark:border-night-border pb-4">
            <h3 className="text-lg font-medium text-text-primary dark:text-night-text">How Hearth shows up</h3>
            <p className="mt-1 text-sm text-text-muted dark:text-night-text/80">
              Beyond its own window, Hearth can lower the lights when your readings say you're drained, and hold the
              door while you focus. All of it runs on this machine.
            </p>
          </div>

          <SettingRow
            title="Live in the tray"
            desc="A quiet way back to Hearth, and the quick controls, from your menu bar."
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
          <h3 className="mb-2 text-base font-medium text-text-primary dark:text-night-text">What you're carrying</h3>
          <p className="mb-4 text-sm text-text-muted dark:text-night-text/80">
            Shapes the rhythm Hearth keeps and the signals it watches. Your daily energy budget adjusts with it.
          </p>
          <div className="flex flex-wrap gap-3">
            {CONDITIONS.map((c) => {
              const on = settings.conditions.includes(c.id);
              return (
                <button
                  key={c.id}
                  onClick={() => toggleCondition(c.id)}
                  aria-pressed={on}
                  className={`rounded-full border px-4 py-2 text-sm transition-colors focus-visible:ring-2 focus-visible:ring-brand focus:outline-none ${
                    on
                      ? 'border-brand bg-brand text-white dark:border-night-brand dark:bg-night-brand dark:text-night-bg'
                      : 'border-base-border text-text-muted hover:bg-black/5 dark:border-night-border dark:text-night-muted dark:hover:bg-white/5'
                  }`}
                >
                  {c.label}
                </button>
              );
            })}
          </div>
          <p className="mt-5 text-sm text-text-muted dark:text-night-muted">
            Daily energy budget: <span className="font-medium text-brand dark:text-night-brand">{settings.dailySpoons} spoons</span>
          </p>
        </div>

        <div className="surface-card p-6">
          <h3 className="mb-2 text-base font-medium text-text-primary dark:text-night-text">Privacy</h3>
          <p className="text-sm text-text-muted dark:text-night-text/80">
            Hearth keeps your records in local SQLite files on this device. There is no account, sync, analytics, or record upload.
            A session summary is saved only when you choose a PDF destination. The database is not application-level encrypted.
          </p>
        </div>

      </div>
    </div>
  );
}
