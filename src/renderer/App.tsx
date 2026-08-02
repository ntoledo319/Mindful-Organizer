import React, { Suspense, useCallback, useEffect, useRef } from 'react';
import { AnimatePresence, MotionConfig, motion } from 'framer-motion';
import { useStore } from './state/store';
import { useScreenshotDriver } from './lib/screenshot';
import { pageVariants } from './lib/motion';
import { QueryErrorState, Spinner } from './components/ui';
import { ScreenErrorBoundary } from './components/ScreenErrorBoundary';
import {
  CORE_CAPABILITIES,
  UTILITY_CAPABILITIES,
  capabilityFor,
  isRoute,
  type Route,
} from './capabilities';
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

export type { Route } from './capabilities';

const ICON_BY_ROUTE: Partial<Record<Route, typeof HomeIcon>> = {
  dashboard: HomeIcon,
  tasks: TaskIcon,
  reflect: MoodIcon,
  practices: LeafIcon,
  trends: ChartIcon,
  crisis: ShieldIcon,
  settings: GearIcon,
};

export function App() {
  return (
    <MotionConfig reducedMotion="user">
      <AppContent />
    </MotionConfig>
  );
}

function AppContent() {
  const { settings, loading, initError, presence, route, setRoute, initialize, setQuiet } = useStore();
  const mainRef = useRef<HTMLElement>(null);
  const hasPresentedInitialRoute = useRef(false);
  const appReady = !loading && settings !== null;
  const activeRoute: Route = isRoute(route) ? route : 'dashboard';
  const navigate = useCallback((nextRoute: Route) => setRoute(nextRoute), [setRoute]);

  useEffect(() => {
    void initialize();
  }, [initialize]);

  useEffect(() => {
    if (isRoute(route)) return;
    setRoute('dashboard');
  }, [route, setRoute]);

  useEffect(() => {
    if (settings?.theme !== 'system') return;
    const preference = window.matchMedia('(prefers-color-scheme: dark)');
    const applyPreference = () => document.documentElement.classList.toggle('dark', preference.matches);
    applyPreference();
    preference.addEventListener('change', applyPreference);
    return () => preference.removeEventListener('change', applyPreference);
  }, [settings?.theme]);

  useEffect(() => {
    if (!appReady) return;
    if (hasPresentedInitialRoute.current) mainRef.current?.focus();
    else hasPresentedInitialRoute.current = true;
  }, [activeRoute, appReady]);

  // No-op unless main launched us in screenshot mode; then it steers route/theme.
  useScreenshotDriver(navigate, appReady);

  if (initError) {
    return (
      <div className="h-full bg-base-bg dark:bg-night-bg">
        <div className="mx-auto max-w-xl px-10 pb-16 pt-24">
          <QueryErrorState
            title="Hearth couldn't finish starting up"
            body="Your local records are still on this device. Try starting Hearth again."
            onRetry={() => void initialize()}
          />
        </div>
      </div>
    );
  }

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

  const currentCapability = capabilityFor(activeRoute);

  return (
    <div data-app-shell className="flex h-full bg-base-bg text-text-primary dark:bg-night-bg dark:text-night-text">
      <aside className="app-drag flex w-60 shrink-0 flex-col gap-1 border-r border-base-border px-4 pb-5 pt-12 dark:border-night-border overflow-y-auto">
        <div className="app-no-drag mb-4 flex items-center gap-2.5 px-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-soft bg-brand text-white shadow-hearth dark:bg-night-brand dark:text-night-bg">
            <HearthMark width={20} height={20} />
          </span>
          <span className="font-display text-xl font-semibold tracking-tight">Hearth</span>
        </div>

        {/* Gamification purposefully removed to align with intrinsic reflection standards */}

        <nav className="app-no-drag flex flex-1 flex-col gap-1" aria-label="Main Navigation">
          {CORE_CAPABILITIES.map(({ route: routeId, navLabel }) => {
            const Icon = ICON_BY_ROUTE[routeId] ?? HomeIcon;
            return (
              <button
                key={routeId}
                onClick={() => navigate(routeId)}
                className={`nav-item ${activeRoute === routeId ? 'active' : ''}`}
                aria-current={activeRoute === routeId ? 'page' : undefined}
              >
                <Icon width={18} height={18} aria-hidden="true" />
                {navLabel}
              </button>
            );
          })}
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

        <div className="app-no-drag mt-2 space-y-1 border-t border-base-border pt-3 dark:border-night-border">
          {UTILITY_CAPABILITIES.map(({ route: routeId, navLabel }) => {
            const Icon = ICON_BY_ROUTE[routeId] ?? HomeIcon;
            return (
              <button
                key={routeId}
                onClick={() => navigate(routeId)}
                className={`nav-item w-full ${activeRoute === routeId ? 'active' : ''}`}
                aria-current={activeRoute === routeId ? 'page' : undefined}
              >
                <Icon width={18} height={18} aria-hidden="true" />
                {navLabel}
              </button>
            );
          })}
        </div>
      </aside>

      <main
        ref={mainRef}
        className="relative flex-1 overflow-y-auto focus:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand dark:focus-visible:ring-night-brand"
        tabIndex={-1}
        aria-label={`${currentCapability?.title ?? 'Hearth'} view`}
      >
        <div className="app-drag absolute inset-x-0 top-0 h-12" />
        <div className="mx-auto max-w-4xl px-10 pb-16 pt-12">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeRoute}
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <ScreenErrorBoundary>
                <Suspense fallback={<div className="flex h-64 items-center justify-center"><Spinner /></div>}>
                  {activeRoute === 'dashboard' && <Dashboard onNavigate={navigate} />}
                  {activeRoute === 'tasks' && <Tasks />}
                  {activeRoute === 'reflect' && <Reflect />}
                  {activeRoute === 'diary' && <DiaryCards />}
                  {activeRoute === 'erp' && <ErpTracker />}
                  {activeRoute === 'practices' && <Practices />}
                  {activeRoute === 'meds' && <Medications />}
                  {activeRoute === 'trends' && <Trends />}
                  {activeRoute === 'crisis' && <CrisisPlanScreen />}
                  {activeRoute === 'settings' && <SettingsScreen />}
                </Suspense>
              </ScreenErrorBoundary>
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
