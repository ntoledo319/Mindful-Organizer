import { useEffect, useRef, useState } from 'react';

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
  return (
    <div className="flex flex-col items-center gap-6">
      <div className="relative flex h-64 w-64 items-center justify-center">
        <div
          className="absolute inset-0 rounded-full bg-gradient-to-br from-eucalyptus/50 to-lavender/60 blur-2xl transition-transform ease-in-out"
          style={{ transform: `scale(${running ? phase.scale : 0.85})`, transitionDuration: `${phase.seconds}s` }}
        />
        <div
          className="relative flex h-40 w-40 items-center justify-center rounded-full bg-gradient-to-br from-sage to-sage-light text-cream shadow-glow transition-transform ease-in-out"
          style={{ transform: `scale(${running ? phase.scale : 0.85})`, transitionDuration: `${phase.seconds}s` }}
        >
          <span className="font-display text-lg font-medium">{running ? phase.label : 'Ready'}</span>
        </div>
      </div>
    </div>
  );
}
