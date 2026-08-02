import { create } from 'zustand';
import { api, onPresence } from '../lib/api';
import type { Settings, PresenceState } from '@shared/types';

interface Store {
  settings: Settings | null;
  presence: PresenceState | null;
  loading: boolean;
  initError: boolean; // first-load IPC failed — App shows a retryable error, not an eternal spinner
  route: string; // Moved manual routing state here for better performance

  // Actions
  setRoute: (route: string) => void;
  initialize: () => Promise<void>;
  saveSettings: (patch: Partial<Settings>) => Promise<void>;
  setQuiet: (active: boolean) => Promise<void>;
}

export const useStore = create<Store>((set) => ({
  settings: null,
  presence: null,
  loading: true,
  initError: false,
  route: 'dashboard',

  setRoute: (route) => set({ route }),

  initialize: async () => {
    set({ loading: true, initError: false });
    try {
      const [settings, presence] = await Promise.all([
        api.getSettings(),
        api.getPresence(),
      ]);

      set({ settings, presence, loading: false });

      // Apply theme
      const applyTheme = (s: Settings) => {
        const root = document.documentElement;
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const dark = s.theme === 'dark' || (s.theme === 'system' && prefersDark);
        root.classList.toggle('dark', dark);
      };
      applyTheme(settings);

      // Live pushes from main
      onPresence(({ state, settings: s }) => {
        set({ settings: s, presence: state });
        applyTheme(s);
      });
    } catch {
      set({ loading: false, initError: true });
    }
  },

  saveSettings: async (patch) => {
    const next = await api.saveSettings(patch);
    set({ settings: next });

    // Re-apply theme if changed
    const root = document.documentElement;
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const dark = next.theme === 'dark' || (next.theme === 'system' && prefersDark);
    root.classList.toggle('dark', dark);
  },

  setQuiet: async (active) => {
    const next = await api.setQuietActive(active);
    set({ presence: next });
  },
}));
