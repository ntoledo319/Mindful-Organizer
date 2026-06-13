import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { api, onPresence } from '../lib/api';
import type { Settings, PresenceState } from '@shared/types';

// Minimal app-wide state: settings (incl. theme + onboarding), live presence
// (the dim/focus state from main), and a refresh counter screens can watch to
// know data changed. Everything else is loaded per-screen so each view owns its
// own data lifecycle.

interface Store {
  settings: Settings | null;
  presence: PresenceState | null;
  loading: boolean;
  saveSettings: (patch: Partial<Settings>) => Promise<void>;
  setQuiet: (active: boolean) => Promise<void>;
  dataVersion: number;
  bumpData: () => void;
}

const Ctx = createContext<Store | null>(null);

export function StoreProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [presence, setPresence] = useState<PresenceState | null>(null);
  const [loading, setLoading] = useState(true);
  const [dataVersion, setDataVersion] = useState(0);

  useEffect(() => {
    void Promise.all([api.getSettings(), api.getPresence()]).then(([s, p]) => {
      setSettings(s);
      setPresence(p);
      setLoading(false);
    });
  }, []);

  // Live pushes from main: a setting changed from the tray, the dim went up or
  // down, a focus hold started or ended. Mirror both so the UI stays honest.
  useEffect(() => {
    const prevFocus = { current: presence?.focus ?? null };
    return onPresence(({ state, settings: s }) => {
      setSettings(s);
      setPresence(state);
      // A focus hold that just ended wrote a practice session — refresh views.
      if (prevFocus.current && !state.focus) setDataVersion((v) => v + 1);
      prevFocus.current = state.focus;
    });
  }, []);

  // Apply theme to <html> whenever it changes.
  useEffect(() => {
    if (!settings) return;
    const root = document.documentElement;
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const dark = settings.theme === 'dark' || (settings.theme === 'system' && prefersDark);
    root.classList.toggle('dark', dark);
  }, [settings]);

  const saveSettings = useCallback(async (patch: Partial<Settings>) => {
    const next = await api.saveSettings(patch);
    setSettings(next);
  }, []);

  const setQuiet = useCallback(async (active: boolean) => {
    setPresence(await api.setQuietActive(active));
  }, []);

  const bumpData = useCallback(() => setDataVersion((v) => v + 1), []);

  const value = useMemo(
    () => ({ settings, presence, loading, saveSettings, setQuiet, dataVersion, bumpData }),
    [settings, presence, loading, saveSettings, setQuiet, dataVersion, bumpData],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useStore(): Store {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useStore must be used within StoreProvider');
  return ctx;
}
