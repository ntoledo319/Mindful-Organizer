import { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useStore } from '../state/store';
import type { SessionKind } from '@shared/types';
import { InlineError, PageHeader, QueryErrorState, Scale, Spinner } from '../components/ui';
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
  { kind: 'breathing', technique: 'Box breathing', blurb: 'Four counts in, hold, out, hold. A slower rhythm to follow.', durationSeconds: 96 },
  { kind: 'grounding', technique: '5-4-3-2-1 senses', blurb: 'Name what you see, hear, touch, smell, and taste. Return attention to now.', durationSeconds: 120 },
  { kind: 'meditation', technique: 'Body scan', blurb: 'Move attention slowly head to toe. No fixing, just noticing.', durationSeconds: 180 },
  { kind: 'focus', technique: '25-minute focus block', blurb: 'One thing, protected. Paulatim holds the door.', durationSeconds: 1500 },
];

export function Practices() {
  const { settings, presence } = useStore();
  const queryClient = useQueryClient();
  const [active, setActive] = useState<Practice | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const historyQuery = useQuery({
    queryKey: ['practices'],
    queryFn: () => api.listPractices(8),
  });
  const history = historyQuery.data ?? [];

  const focusHold = presence?.focus ?? null;

  const start = async (p: Practice) => {
    setActionError(null);
    if (p.kind === 'focus' && settings?.focusGuard) {
      try {
        await api.startFocus({ seconds: p.durationSeconds, intention: null });
      } catch {
        setActionError('Paulatim could not start the focus hold. Try again, or turn the hold off in Settings.');
      }
      return;
    }
    setActive(p);
  };

  return (
    <div>
      <PageHeader title="Practices" subtitle="Small steadying acts, chosen for how today feels." />

      {actionError && <div className="mb-6"><InlineError>{actionError}</InlineError></div>}

      {focusHold && !active && (
        <div className="surface-card mb-6 flex items-center justify-between gap-4 px-6 py-5 border-l-4 border-l-brand">
          <div>
            <p className="font-display text-lg font-medium text-text-primary dark:text-night-text">
              A focus block is running
            </p>
            <p className="text-base text-text-muted dark:text-night-text/80 mt-1">
              Paulatim is holding the door. The hold lives over your screen — end it there, with Esc, or here.
            </p>
          </div>
          <button
            className="btn-ghost shrink-0"
            onClick={() => {
              setActionError(null);
              void api.endFocus().catch(() => setActionError('Paulatim could not end the focus hold here. Use Esc or the tray, then try again.'));
            }}
          >
            End now
          </button>
        </div>
      )}

      {active ? (
        <PracticeRunner
          practice={active}
          onDone={() => {
            setActive(null);
            queryClient.invalidateQueries({ queryKey: ['practices'] });
            queryClient.invalidateQueries({ queryKey: ['snapshot'] });
            queryClient.invalidateQueries({ queryKey: ['briefing'] });
          }}
          onCancel={() => setActive(null)}
        />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {PRACTICES.map((p) => (
              <button
                key={p.technique}
                onClick={() => void start(p)}
                className="surface-card group flex flex-col items-start gap-2 p-6 text-left transition hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 focus:outline-none motion-reduce:hover:translate-y-0"
              >
                <span className="font-display text-xl font-medium text-text-primary dark:text-night-text">{p.technique}</span>
                <span className="text-base text-text-muted dark:text-night-text/80">{p.blurb}</span>
                <span className="mt-3 text-sm font-medium text-brand dark:text-night-brand flex items-center gap-1">
                  {Math.round(p.durationSeconds / 60)} min
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="opacity-0 -translate-x-2 transition-all group-hover:opacity-100 group-hover:translate-x-0">
                    <line x1="5" y1="12" x2="19" y2="12" />
                    <polyline points="12 5 19 12 12 19" />
                  </svg>
                </span>
              </button>
            ))}
          </div>

          {historyQuery.isLoading && <Spinner />}
          {historyQuery.isError && (
            <div className="mt-8">
              <QueryErrorState title="Practice history didn't load" onRetry={() => void historyQuery.refetch()} />
            </div>
          )}
          {!historyQuery.isError && history.length > 0 && (
            <div className="mt-10">
              <h3 className="mb-4 font-display text-xl font-medium text-text-primary dark:text-night-text border-b border-base-border dark:border-night-border pb-2">Lately</h3>
              <ul className="space-y-1">
                {history.map((h) => (
                  <li key={h.id} className="group flex items-center justify-between px-2 py-3 border-b border-base-border dark:border-night-border last:border-0 hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
                    <span className="text-base font-medium text-text-primary dark:text-night-text">{h.technique}</span>
                    <span className="text-xs text-text-muted dark:text-night-muted/80">{relTime(h.timestamp)}</span>
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
  const [isFinishing, setIsFinishing] = useState(false);
  const [finishError, setFinishError] = useState(false);

  // Using useState to track the interval, but keeping React out of the exact millisecond firing to prevent lag.
  useEffect(() => {
    if (phase !== 'run') return;
    let r = remaining;
    const interval = setInterval(() => {
      r -= 1;
      setRemaining(r);
      if (r <= 0) {
        clearInterval(interval);
        setPhase('post');
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [phase]);

  const finish = () => {
    setIsFinishing(true);
    setFinishError(false);
    void api
      .logPractice({
        kind: practice.kind,
        technique: practice.technique,
        durationSeconds: practice.durationSeconds - remaining,
        preDistress: pre,
        postDistress: post,
      })
      .then(onDone)
      .catch(() => {
        setIsFinishing(false);
        setFinishError(true);
      });
  };

  const mm = String(Math.floor(remaining / 60)).padStart(2, '0');
  const ss = String(remaining % 60).padStart(2, '0');

  return (
    <div className="surface-card flex flex-col items-center gap-8 px-6 py-16 text-center">
      <h2 className="font-display text-3xl font-medium text-text-primary dark:text-night-text">{practice.technique}</h2>

      {phase === 'pre' && (
        <div className="w-full max-w-sm space-y-6">
          <p className="text-base text-text-muted dark:text-night-text/80">
            Before we start — how much distress are you holding right now?
          </p>
          <Scale label="Distress" value={pre} onChange={setPre} min={0} tone="error" />
          <div className="flex justify-center gap-3 pt-2">
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
            <div className="flex h-64 w-64 items-center justify-center rounded-full bg-base-bg dark:bg-night-bg shadow-inner border border-base-border dark:border-night-border relative overflow-hidden">
              <div className="absolute inset-0 bg-brand/5 dark:bg-night-brand/10" style={{ transform: `translateY(${(1 - remaining / practice.durationSeconds) * 100}%)`, transition: 'transform 1s linear' }} />
              <span className="font-display text-6xl font-medium tabular-nums text-text-primary dark:text-night-text relative z-10" role="timer" aria-label={`${mm} minutes ${ss} seconds remaining`}>
                {mm}:{ss}
              </span>
            </div>
          )}
          <p className="max-w-sm text-base text-text-muted dark:text-night-text/80">{practice.blurb}</p>
          <button className="btn-ghost" onClick={() => setPhase('post')}>
            I'm done
          </button>
        </>
      )}

      {phase === 'post' && (
        <div className="w-full max-w-sm space-y-6">
          <p className="text-base text-text-muted dark:text-night-text/80">And now? No right answer.</p>
          <Scale label="Distress" value={post} onChange={setPost} min={0} tone="success" />
          <button className="btn-primary w-full" onClick={finish} disabled={isFinishing}>
            {isFinishing ? 'Saving...' : 'Save & close'}
          </button>
          {finishError && <InlineError>Paulatim could not save this practice. Try again.</InlineError>}
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
