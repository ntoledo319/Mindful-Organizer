import { useEffect, useRef, useState } from 'react';
import { useReducedMotion } from 'framer-motion';

// A breathing pacer. The orb expands on inhale, holds, contracts on exhale,
// holds again — the classic box pattern by default but configurable per phase.
// Motion drives the breath; we never use a countdown bar, which feels clinical.

interface Phase {
  label: string;
  seconds: number;
  scale: number;
}

const BOX: Phase[] = [
  { label: 'Breathe in', seconds: 4, scale: 1.15 },
  { label: 'Hold', seconds: 4, scale: 1.15 },
  { label: 'Breathe out', seconds: 4, scale: 0.78 },
  { label: 'Hold', seconds: 4, scale: 0.78 },
];

export function BreathOrb({ running }: { running: boolean }) {
  const [phaseIdx, setPhaseIdx] = useState(0);
  const timer = useRef<ReturnType<typeof setTimeout>>();
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    if (!running) {
      setPhaseIdx(0);
      return;
    }
    const phase = BOX[phaseIdx];
    timer.current = setTimeout(() => setPhaseIdx((i) => (i + 1) % BOX.length), phase.seconds * 1000);
    return () => clearTimeout(timer.current);
  }, [running, phaseIdx]);

  const phase = BOX[phaseIdx];
  const scale = reduceMotion ? 1 : running ? phase.scale : 0.85;
  const transitionDuration = reduceMotion ? '0ms' : `${phase.seconds}s`;

  return (
    <div className="flex flex-col items-center gap-6" role="timer" aria-live="polite" aria-atomic="true">
      <div className="relative flex h-64 w-64 items-center justify-center">
        <div
          className="absolute inset-0 rounded-full bg-gradient-to-br from-brand/35 to-semantic-warning/20 blur-2xl transition-transform ease-in-out dark:from-night-brand/35 dark:to-night-warning/20"
          style={{ transform: `scale(${scale})`, transitionDuration }}
          aria-hidden="true"
        />
        <div
          className="relative flex h-40 w-40 items-center justify-center rounded-full bg-gradient-to-br from-brand to-semantic-error text-white shadow-glow transition-transform ease-in-out dark:from-night-brand dark:to-night-warning dark:text-night-bg"
          style={{ transform: `scale(${scale})`, transitionDuration }}
        >
          <span className="font-display text-lg font-medium">{running ? phase.label : 'Ready'}</span>
        </div>
      </div>
    </div>
  );
}
