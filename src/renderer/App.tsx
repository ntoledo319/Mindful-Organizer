import React, { Suspense, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useStore } from './state/store';
import { useScreenshotDriver } from './lib/screenshot';
import { pageVariants } from './lib/motion';
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

// Lazy load screens for performance
const Onboarding = React.lazy(() => import('./screens/Onboarding').then(m => ({ default: m.Onboarding })));
const Dashboard = React.lazy(() => import('./screens/Dashboard').then(m => ({ default: m.Dashboard })));
const Tasks = React.lazy(() => import('./screens/Tasks').then(m => ({ default: m.Tasks })));
const Reflect = React.lazy(() => import('./screens/Reflect').then(m => ({ default: m.Reflect })));
const Practices = React.lazy(() => import('./screens/Practices').then(m => ({ default: m.Practices })));
const Trends = React.lazy(() => import('./screens/Trends').then(m => ({ default: m.Trends })));
const CrisisPlanScreen = React.lazy(() => import('./screens/CrisisPlan').then(m => ({ default: m.CrisisPlanScreen })));
const SettingsScreen = React.lazy(() => import('./screens/Settings').then(m => ({ default: m.SettingsScreen })));
const ErpTracker = React.lazy(() => import('./screens/Erp').then(m => ({ default: m.ErpTracker })));
const DiaryCards = React.lazy(() => import('./screens/Diary').then(m => ({ default: m.DiaryCards })));
const Medications = React.lazy(() => import('./screens/Meds').then(m => ({ default: m.Medications })));

export type Route = 'dashboard' | 'tasks' | 'reflect' | 'practices' | 'trends' | 'crisis' | 'settings' | 'erp' | 'diary' | 'meds';

const NAV: { id: Route; label: string; icon: typeof HomeIcon }[] = [
  { id: 'dashboard', label: 'Today', icon: HomeIcon },
  { id: 'tasks', label: 'Tasks', icon: TaskIcon },
  { id: 'reflect', label: 'Reflect', icon: MoodIcon },
  { id: 'diary', label: 'Diary Cards', icon: MoodIcon },
  { id: 'erp', label: 'ERP Tracker', icon: ShieldIcon },
  { id: 'practices', label: 'Practices', icon: LeafIcon },
  { id: 'meds', label: 'Medications', icon: LeafIcon },
  { id: 'trends', label: 'Rhythm', icon: ChartIcon },
  { id: 'crisis', label: 'Crisis plan', icon: ShieldIcon },
];

export function App() {
  const { settings, loading, presence, route, setRoute, initialize, setQuiet } = useStore();

  useEffect(() => {
    void initialize();
  }, [initialize]);

  // No-op unless main launched us in screenshot mode; then it steers route/theme.
  useScreenshotDriver((r) => setRoute(r as Route), !loading && !!settings);

  if (loading || !settings) {
    return (
      <div className="h-full bg-base-bg dark:bg-night-bg">
        <Spinner />
      </div>
    );
  }

  if (!settings.onboarded || !settings.privacyConsentAt) {
    return (
      <Suspense fallback={<Spinner />}>
        <Onboarding />
      </Suspense>
    );
  }

  return (
    <div className="flex h-full bg-base-bg text-text-primary dark:bg-night-bg dark:text-night-text">
      <aside className="app-drag flex w-60 shrink-0 flex-col gap-1 border-r border-base-border px-4 pb-5 pt-12 dark:border-night-border overflow-y-auto">
        <div className="app-no-drag mb-4 flex items-center gap-2.5 px-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-soft bg-brand text-white shadow-hearth dark:bg-night-brand dark:text-night-bg">
            <HearthMark width={20} height={20} />
          </span>
          <span className="font-display text-xl font-semibold tracking-tight">Hearth</span>
        </div>
        
        {/* Gamification purposefully removed to align with intrinsic reflection standards */}

        <nav className="app-no-drag flex flex-1 flex-col gap-1" aria-label="Main Navigation">
          {NAV.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setRoute(id)}
              className={`nav-item ${route === id ? 'active' : ''}`}
              aria-current={route === id ? 'page' : undefined}
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
            role="switch"
            aria-checked={presence.quietActive}
          >
            <MoonIcon width={18} height={18} />
            {presence.quietActive ? 'Brighten' : 'Quiet'}
          </button>
        )}

        <button
          onClick={() => setRoute('settings')}
          className={`nav-item app-no-drag ${route === 'settings' ? 'active' : ''}`}
          aria-current={route === 'settings' ? 'page' : undefined}
        >
          <GearIcon width={18} height={18} />
          Settings
        </button>
      </aside>

      <main className="relative flex-1 overflow-y-auto" tabIndex={-1}>
        <div className="app-drag absolute inset-x-0 top-0 h-12" />
        <div className="mx-auto max-w-4xl px-10 pb-16 pt-12">
          <AnimatePresence mode="wait">
            <motion.div
              key={route}
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <Suspense fallback={<div className="flex h-64 items-center justify-center"><Spinner /></div>}>
                {route === 'dashboard' && <Dashboard onNavigate={(r: string) => setRoute(r as Route)} />}
                {route === 'tasks' && <Tasks />}
                {route === 'reflect' && <Reflect />}
                {route === 'diary' && <DiaryCards />}
                {route === 'erp' && <ErpTracker />}
                {route === 'practices' && <Practices />}
                {route === 'meds' && <Medications />}
                {route === 'trends' && <Trends />}
                {route === 'crisis' && <CrisisPlanScreen />}
                {route === 'settings' && <SettingsScreen />}
              </Suspense>
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
