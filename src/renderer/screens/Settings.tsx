import { useStore } from '../state/store';
import { CONDITIONS, type Condition, type Settings } from '@shared/types';
import { dailySpoonsFor } from '@shared/spoons';
import { PageHeader } from '../components/ui';
import { SunIcon, MoonIcon } from '../components/icons';

const THEMES: { id: Settings['theme']; label: string }[] = [
  { id: 'light', label: 'Light' },
  { id: 'dark', label: 'Dark' },
  { id: 'system', label: 'Match system' },
];

export function SettingsScreen() {
  const { settings, saveSettings } = useStore();
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
