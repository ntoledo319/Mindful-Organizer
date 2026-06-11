import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { api } from '../lib/api';
import type { Settings } from '@shared/types';

// Minimal app-wide state: settings (incl. theme + onboarding) and a refresh
// counter screens can watch to know data changed. Everything else is loaded
// per-screen so each view owns its own data lifecycle.

interface Store {
  settings: Settings | null;
  loading: boolean;
  saveSettings: (patch: Partial<Settings>) => Promise<void>;
  dataVersion: number;
  bumpData: () => void;
}

const Ctx = createContext<Store | null>(null);

export function StoreProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);
  const [dataVersion, setDataVersion] = useState(0);

  useEffect(() => {
    void api.getSettings().then((s) => {
      setSettings(s);
      setLoading(false);
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

  const bumpData = useCallback(() => setDataVersion((v) => v + 1), []);

  const value = useMemo(
    () => ({ settings, loading, saveSettings, dataVersion, bumpData }),
    [settings, loading, saveSettings, dataVersion, bumpData],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useStore(): Store {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useStore must be used within StoreProvider');
  return ctx;
}
