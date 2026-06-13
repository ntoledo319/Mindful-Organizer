import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { useStore } from '../state/store';
import type { SessionKind, PracticeSession } from '@shared/types';
import { PageHeader, Scale } from '../components/ui';
import { BreathOrb } from '../components/BreathOrb';
import { formatDistanceToNow } from 'date-fns';

interface Practice {
  kind: SessionKind;
  technique: string;
  blurb: string;
  durationSeconds: number;
}

// Each practice maps to an evidence-rooted technique from the original wellness
// modules (breathing / grounding / meditation / focus). Kept short and finishable.
const PRACTICES: Practice[] = [
  { kind: 'breathing', technique: 'Box breathing', blurb: 'Four counts in, hold, out, hold. Steadies a racing system.', durationSeconds: 96 },
  { kind: 'grounding', technique: '5-4-3-2-1 senses', blurb: 'Name what you see, hear, touch, smell, taste. Pulls you back to now.', durationSeconds: 120 },
  { kind: 'meditation', technique: 'Body scan', blurb: 'Move attention slowly head to toe. No fixing, just noticing.', durationSeconds: 180 },
  { kind: 'focus', technique: '25-minute focus block', blurb: 'One thing, protected. Hearth holds the door.', durationSeconds: 1500 },
];

export function Practices() {
  const { bumpData, settings, presence, dataVersion } = useStore();
  const [active, setActive] = useState<Practice | null>(null);
  const [history, setHistory] = useState<PracticeSession[]>([]);

  const load = () => void api.listPractices(8).then(setHistory);
  useEffect(load, [dataVersion]); // refresh after a guarded focus block ends in main

  // A focus block with the guard on hands the whole thing to the acting layer:
  // Hearth dims everything else and holds the door. Otherwise it runs in-window.
  const start = (p: Practice) => {
    if (p.kind === 'focus' && settings?.focusGuard) {
      void api.startFocus({ seconds: p.durationSeconds, intention: null });
      return;
    }
    setActive(p);
  };

  const focusHold = presence?.focus ?? null;

  return (
    <div>
      <PageHeader title="Practices" subtitle="Small steadying acts, chosen for how today feels." />

      {focusHold && !active && (
        <div className="glass-card mb-4 flex items-center justify-between gap-4 px-5 py-4">
          <div>
            <p className="font-display text-base font-semibold text-charcoal dark:text-cream">
              A focus block is running
            </p>
            <p className="text-sm text-charcoal-mute dark:text-cream/55">
              Hearth is holding the door. The hold lives over your screen — end it there, with Esc, or here.
            </p>
          </div>
          <button className="btn-ghost shrink-0" onClick={() => void api.endFocus()}>
            End now
          </button>
        </div>
      )}

      {active ? (
        <PracticeRunner
          practice={active}
          onDone={() => {
            setActive(null);
            load();
            bumpData();
          }}
          onCancel={() => setActive(null)}
        />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {PRACTICES.map((p) => (
              <button
                key={p.technique}
                onClick={() => start(p)}
                className="glass-card group flex flex-col items-start gap-1 p-5 text-left transition hover:-translate-y-0.5 hover:shadow-glow"
              >
                <span className="font-display text-lg font-semibold text-charcoal dark:text-cream">{p.technique}</span>
                <span className="text-sm text-charcoal-mute dark:text-cream/55">{p.blurb}</span>
                <span className="mt-2 text-xs font-medium text-sage dark:text-eucalyptus">
                  {Math.round(p.durationSeconds / 60)} min →
                </span>
              </button>
            ))}
          </div>

          {history.length > 0 && (
            <div className="mt-8">
              <h3 className="mb-3 font-display text-lg font-semibold text-charcoal dark:text-cream">Lately</h3>
              <ul className="space-y-2">
                {history.map((h) => (
                  <li key={h.id} className="glass-card flex items-center justify-between px-4 py-3 text-sm">
                    <span className="font-medium text-charcoal dark:text-cream">{h.technique}</span>
                    <span className="text-xs text-charcoal-mute dark:text-cream/40">{relTime(h.timestamp)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function PracticeRunner({
  practice,
  onDone,
  onCancel,
}: {
  practice: Practice;
  onDone: () => void;
  onCancel: () => void;
}) {
  const [phase, setPhase] = useState<'pre' | 'run' | 'post'>('pre');
  const [pre, setPre] = useState(5);
  const [post, setPost] = useState(4);
  const [remaining, setRemaining] = useState(practice.durationSeconds);

  useEffect(() => {
    if (phase !== 'run') return;
    if (remaining <= 0) {
      setPhase('post');
      return;
    }
    const t = setTimeout(() => setRemaining((r) => r - 1), 1000);
    return () => clearTimeout(t);
  }, [phase, remaining]);

  const finish = () => {
    void api
      .logPractice({
        kind: practice.kind,
        technique: practice.technique,
        durationSeconds: practice.durationSeconds - remaining,
        preDistress: pre,
        postDistress: post,
      })
      .then(onDone);
  };

  const mm = String(Math.floor(remaining / 60)).padStart(2, '0');
  const ss = String(remaining % 60).padStart(2, '0');

  return (
    <div className="glass-card flex flex-col items-center gap-6 px-6 py-12 text-center">
      <h2 className="font-display text-2xl font-semibold text-charcoal dark:text-cream">{practice.technique}</h2>

      {phase === 'pre' && (
        <div className="w-full max-w-xs space-y-5">
          <p className="text-sm text-charcoal-mute dark:text-cream/55">
            Before we start — how much distress are you holding right now?
          </p>
          <Scale label="Distress" value={pre} onChange={setPre} min={0} tone="ember" />
          <div className="flex justify-center gap-2">
            <button className="btn-ghost" onClick={onCancel}>
              Not now
            </button>
            <button className="btn-primary" onClick={() => setPhase('run')}>
              Begin
            </button>
          </div>
        </div>
      )}

      {phase === 'run' && (
        <>
          {practice.kind === 'breathing' ? (
            <BreathOrb running />
          ) : (
            <div className="flex h-56 w-56 items-center justify-center rounded-full bg-gradient-to-br from-eucalyptus/30 to-lavender/40">
              <span className="font-display text-5xl font-semibold tabular-nums text-sage dark:text-eucalyptus">
                {mm}:{ss}
              </span>
            </div>
          )}
          <p className="max-w-xs text-sm text-charcoal-mute dark:text-cream/55">{practice.blurb}</p>
          <button className="btn-ghost" onClick={() => setPhase('post')}>
            I'm done
          </button>
        </>
      )}

      {phase === 'post' && (
        <div className="w-full max-w-xs space-y-5">
          <p className="text-sm text-charcoal-mute dark:text-cream/55">And now? No right answer.</p>
          <Scale label="Distress" value={post} onChange={setPost} min={0} tone="ember" />
          <button className="btn-primary w-full" onClick={finish}>
            Save & close
          </button>
        </div>
      )}
    </div>
  );
}

function relTime(iso: string): string {
  try {
    const d = new Date(iso.includes('T') ? iso : iso.replace(' ', 'T') + 'Z');
    return formatDistanceToNow(d, { addSuffix: true });
  } catch {
    return iso;
  }
}
