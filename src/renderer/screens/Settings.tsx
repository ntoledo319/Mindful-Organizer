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

function Toggle({ on, onChange }: { on: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      role="switch"
      aria-checked={on}
      onClick={() => onChange(!on)}
      className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${
        on ? 'bg-sage' : 'bg-charcoal/15 dark:bg-white/15'
      }`}
    >
      <span
        className={`absolute top-0.5 h-5 w-5 rounded-full bg-cream shadow-sm transition-all ${
          on ? 'left-[1.375rem]' : 'left-0.5'
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
    <div className="flex items-start justify-between gap-4">
      <div>
        <p className="text-sm font-medium text-charcoal-soft dark:text-cream/80">{title}</p>
        <p className="mt-0.5 text-xs text-charcoal-mute dark:text-cream/50">{desc}</p>
      </div>
      <Toggle on={on} onChange={onChange} />
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

      <div className="space-y-4">
        <div className="glass-card p-5">
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-charcoal-soft dark:text-cream/70">Name</span>
            <input
              className="field max-w-xs"
              value={settings.displayName}
              placeholder="What should Hearth call you?"
              onChange={(e) => void saveSettings({ displayName: e.target.value })}
            />
          </label>
        </div>

        <div className="glass-card p-5">
          <h3 className="mb-3 text-sm font-medium text-charcoal-soft dark:text-cream/70">Appearance</h3>
          <div className="flex gap-2">
            {THEMES.map((t) => (
              <button
                key={t.id}
                onClick={() => void saveSettings({ theme: t.id })}
                className={settings.theme === t.id ? 'btn-primary' : 'btn-ghost'}
              >
                {t.id === 'light' && <SunIcon width={15} height={15} />}
                {t.id === 'dark' && <MoonIcon width={15} height={15} />}
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* The acting layer — the part of Hearth that reaches past its own window. */}
        <div className="glass-card space-y-5 p-5">
          <div>
            <h3 className="text-sm font-medium text-charcoal-soft dark:text-cream/70">How Hearth shows up</h3>
            <p className="mt-0.5 text-xs text-charcoal-mute dark:text-cream/50">
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

          <div className="space-y-3 border-t border-charcoal/5 pt-4 dark:border-white/5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-charcoal-soft dark:text-cream/80">Dim when you're drained</p>
                <p className="mt-0.5 text-xs text-charcoal-mute dark:text-cream/50">
                  A warm wash lowers over the screen so a tired hour stops shouting at you.
                </p>
              </div>
              {presence && (
                <button
                  onClick={() => void setQuiet(!presence.quietActive)}
                  className={presence.quietActive ? 'btn-primary' : 'btn-ghost'}
                >
                  {presence.quietActive ? 'Brighten now' : 'Dim now'}
                </button>
              )}
            </div>
            <div className="flex gap-2">
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
              <div className="max-w-xs pt-1">
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

          <div className="space-y-4 border-t border-charcoal/5 pt-4 dark:border-white/5">
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

        <div className="glass-card p-5">
          <h3 className="mb-1 text-sm font-medium text-charcoal-soft dark:text-cream/70">What you're carrying</h3>
          <p className="mb-3 text-xs text-charcoal-mute dark:text-cream/50">
            Shapes the rhythm Hearth keeps and the signals it watches. Your daily energy budget adjusts with it.
          </p>
          <div className="flex flex-wrap gap-2">
            {CONDITIONS.map((c) => {
              const on = settings.conditions.includes(c.id);
              return (
                <button
                  key={c.id}
                  onClick={() => toggleCondition(c.id)}
                  className={`rounded-full border px-4 py-1.5 text-sm transition ${
                    on
                      ? 'border-sage bg-sage text-cream'
                      : 'border-charcoal/10 text-charcoal-soft hover:bg-white/60 dark:border-white/10 dark:text-cream/70 dark:hover:bg-white/5'
                  }`}
                >
                  {c.label}
                </button>
              );
            })}
          </div>
          <p className="mt-3 text-xs text-charcoal-mute dark:text-cream/50">
            Daily energy budget: <span className="font-medium text-sage dark:text-eucalyptus">{settings.dailySpoons} spoons</span>
          </p>
        </div>

        <div className="glass-card p-5">
          <h3 className="mb-1 text-sm font-medium text-charcoal-soft dark:text-cream/70">Privacy</h3>
          <p className="text-sm text-charcoal-mute dark:text-cream/55">
            Hearth keeps a single local database on this device. No account, no sync, no analytics, no network calls.
            Your data is yours.
          </p>
        </div>
      </div>
    </div>
  );
}
