import { useEffect } from 'react';
import type { Route } from '../App';

// Renderer half of the screenshot tooling. Entirely inert in normal launches —
// window.__hearthShot only exists when the Electron main process started us in
// screenshot mode (see electron/preload.ts + electron/screenshot.ts). When it
// does, the main process sends route/theme specs and we apply them, then signal
// that the view has settled so main can capture a clean frame.

interface GotoSpec {
  route?: Route;
  theme?: 'light' | 'dark';
}

interface ShotBridge {
  onGoto: (cb: (spec: GotoSpec) => void) => void;
  ready: () => void;
}

declare global {
  interface Window {
    __hearthShot?: ShotBridge;
  }
}

export function useScreenshotDriver(setRoute: (r: Route) => void, appReady: boolean): void {
  useEffect(() => {
    const shot = window.__hearthShot;
    if (!shot) return;

    shot.onGoto((spec) => {
      if (spec.theme) {
        document.documentElement.classList.toggle('dark', spec.theme === 'dark');
      }
      if (spec.route) setRoute(spec.route);
      // Let screens fetch their data and Framer Motion's ~0.22s route transition
      // settle, then wait two animation frames so the new route has actually
      // painted before signaling — a fixed timer alone races the paint and can
      // capture a blank frame mid-transition.
      window.setTimeout(() => {
        requestAnimationFrame(() => requestAnimationFrame(() => shot.ready()));
      }, 1400);
    });
  }, [setRoute]);

  // Tell main the app shell has mounted (used for the onboarding capture, which
  // has no route to navigate to).
  useEffect(() => {
    if (appReady) window.__hearthShot?.ready();
  }, [appReady]);
}
