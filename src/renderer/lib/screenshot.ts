import { useEffect } from 'react';
import type { Route } from '../App';

// Renderer half of the screenshot tooling. Entirely inert in normal launches —
// window.__ampleShot only exists when the Electron main process started us in
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
    __ampleShot?: ShotBridge;
  }
}

// Resolve once every <img> currently in the document has decoded, so a capture
// can't fire mid-decode. A per-image timeout keeps a stuck decode from wedging
// the whole run; capped overall by main's waitForReady timeout.
function waitForImages(): Promise<void> {
  const imgs = Array.from(document.images);
  return Promise.all(
    imgs.map((img) => {
      const ready = img.complete && img.naturalWidth > 0 ? img.decode().catch(() => {}) : decodeWhenLoaded(img);
      return Promise.race([ready, new Promise<void>((r) => window.setTimeout(r, 5000))]);
    }),
  ).then(() => undefined);
}

function decodeWhenLoaded(img: HTMLImageElement): Promise<void> {
  return new Promise<void>((resolve) => {
    const finish = () => img.decode().catch(() => {}).then(() => resolve());
    img.addEventListener('load', finish, { once: true });
    img.addEventListener('error', () => resolve(), { once: true });
  });
}

export function useScreenshotDriver(setRoute: (r: Route) => void, appReady: boolean): void {
  useEffect(() => {
    const shot = window.__ampleShot;
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
        // The onboarding hero is a multi-megabyte PNG loaded as a data URL; its
        // decode can outlast the timer, so the gradient fallback would be
        // captured instead. Wait for every <img> to finish decoding before the
        // two-frame paint barrier so the captured frame is always complete.
        void waitForImages().then(() => {
          requestAnimationFrame(() => requestAnimationFrame(() => shot.ready()));
        });
      }, 1400);
    });
  }, [setRoute]);

  // Tell main the app shell has mounted (used for the onboarding capture, which
  // has no route to navigate to).
  useEffect(() => {
    if (appReady) window.__ampleShot?.ready();
  }, [appReady]);
}
