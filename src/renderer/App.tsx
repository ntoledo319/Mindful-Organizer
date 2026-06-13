import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useStore } from './state/store';
import { useScreenshotDriver } from './lib/screenshot';
import { Onboarding } from './screens/Onboarding';
import { Dashboard } from './screens/Dashboard';
import { Tasks } from './screens/Tasks';
import { Reflect } from './screens/Reflect';
import { Practices } from './screens/Practices';
import { Trends } from './screens/Trends';
import { CrisisPlanScreen } from './screens/CrisisPlan';
import { SettingsScreen } from './screens/Settings';
import { Spinner } from './components/ui';
import {
  HearthMark,
  HomeIcon,
  TaskIcon,
  MoodIcon,
  LeafIcon,
  ChartIcon,
  ShieldIcon,
  GearIcon,
  MoonIcon,
} from './components/icons';

export type Route = 'dashboard' | 'tasks' | 'reflect' | 'practices' | 'trends' | 'crisis' | 'settings';

const NAV: { id: Route; label: string; icon: typeof HomeIcon }[] = [
  { id: 'dashboard', label: 'Today', icon: HomeIcon },
  { id: 'tasks', label: 'Tasks', icon: TaskIcon },
  { id: 'reflect', label: 'Reflect', icon: MoodIcon },
  { id: 'practices', label: 'Practices', icon: LeafIcon },
  { id: 'trends', label: 'Rhythm', icon: ChartIcon },
  { id: 'crisis', label: 'Crisis plan', icon: ShieldIcon },
];

export function App() {
  const { settings, loading, presence, setQuiet } = useStore();
  const [route, setRoute] = useState<Route>('dashboard');

  // No-op unless main launched us in screenshot mode; then it steers route/theme.
  useScreenshotDriver(setRoute, !loading && !!settings);

  if (loading || !settings) {
    return (
      <div className="h-full bg-cream dark:bg-night">
        <Spinner />
      </div>
    );
  }

  if (!settings.onboarded) {
    return <Onboarding />;
  }

  return (
    <div className="flex h-full bg-cream text-charcoal dark:bg-night dark:text-cream">
      <aside className="app-drag flex w-60 shrink-0 flex-col gap-1 border-r border-charcoal/5 px-4 pb-5 pt-12 dark:border-white/5">
        <div className="app-no-drag mb-6 flex items-center gap-2.5 px-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-sage text-cream shadow-hearth">
            <HearthMark width={20} height={20} />
          </span>
          <span className="font-display text-xl font-semibold tracking-tight">Hearth</span>
        </div>

        <nav className="app-no-drag flex flex-1 flex-col gap-1">
          {NAV.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setRoute(id)}
              className={`nav-item ${route === id ? 'active' : ''}`}
            >
              <Icon width={18} height={18} />
              {label}
            </button>
          ))}
        </nav>

        {presence && (
          <button
            onClick={() => void setQuiet(!presence.quietActive)}
            className={`nav-item app-no-drag ${presence.quietActive ? 'active' : ''}`}
            title="Lower the lights over everything"
          >
            <MoonIcon width={18} height={18} />
            {presence.quietActive ? 'Brighten' : 'Quiet'}
          </button>
        )}

        <button
          onClick={() => setRoute('settings')}
          className={`nav-item app-no-drag ${route === 'settings' ? 'active' : ''}`}
        >
          <GearIcon width={18} height={18} />
          Settings
        </button>
      </aside>

      <main className="relative flex-1 overflow-y-auto">
        <div className="app-drag absolute inset-x-0 top-0 h-12" />
        <div className="mx-auto max-w-4xl px-10 pb-16 pt-12">
          <AnimatePresence mode="wait">
            <motion.div
              key={route}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.22 }}
            >
              {route === 'dashboard' && <Dashboard onNavigate={setRoute} />}
              {route === 'tasks' && <Tasks />}
              {route === 'reflect' && <Reflect />}
              {route === 'practices' && <Practices />}
              {route === 'trends' && <Trends />}
              {route === 'crisis' && <CrisisPlanScreen />}
              {route === 'settings' && <SettingsScreen />}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
