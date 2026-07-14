import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { api } from '../lib/api';
import { spoonWarning } from '@shared/spoons';
import { transitionGentle, hoverTactile } from '../lib/motion';
import type { WellnessSnapshot, CrisisSignal } from '@shared/types';
import type { Route } from '../App';
import { Spinner } from '../components/ui';
import { LeafIcon, CheckIcon } from '../components/icons';

const SEVERITY_STYLE: Record<CrisisSignal['severity'], string> = {
  urgent: 'border-semantic-error/40 bg-semantic-error/10 text-semantic-error',
  moderate: 'border-semantic-error/30 bg-semantic-error/5 text-semantic-error',
  mild: 'border-semantic-warning/30 bg-semantic-warning/10 text-text-primary dark:text-night-text',
  info: 'border-semantic-success/20 bg-semantic-success/5 text-text-primary dark:text-night-text',
};

function SpoonMeter({ snap }: { snap: WellnessSnapshot }) {
  const warn = spoonWarning(snap.spoonsRemaining, snap.spoonsTotal);
  const pct = snap.spoonsTotal ? (snap.spoonsRemaining / snap.spoonsTotal) * 100 : 0;
  const label =
    warn === 'empty'
      ? 'Spent for today — rest is the task now.'
      : warn === 'low'
        ? 'Running low. Be choosy with what comes next.'
        : warn === 'mindful'
          ? 'A mindful amount left. Pace yourself.'
          : 'Plenty in reserve.';
  
  const bar = warn === 'empty' || warn === 'low' ? 'bg-semantic-error' : warn === 'mindful' ? 'bg-semantic-warning' : 'bg-semantic-success';
  
  return (
    <div className="surface-card p-5">
      <div className="flex items-baseline justify-between">
        <h3 className="text-sm font-medium text-text-muted dark:text-night-muted">Energy budget</h3>
        <span className="font-display text-lg font-semibold text-text-primary dark:text-night-text">
          {snap.spoonsRemaining}
          <span className="text-sm text-text-muted dark:text-night-muted"> / {snap.spoonsTotal} spoons</span>
        </span>
      </div>
      <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-black/5 dark:bg-white/10">
        <motion.div
          className={`h-full rounded-full ${bar}`}
          initial={{ width: 0 }}
          animate={{ width: `${Math.max(pct, 3)}%` }}
          transition={transitionGentle}
        />
      </div>
      <p className="mt-2 text-xs text-text-muted dark:text-night-muted">{label}</p>
    </div>
  );
}

function StatItem({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div>
      <h3 className="text-sm font-medium text-text-muted dark:text-night-muted">{label}</h3>
      <p className="mt-1 font-display text-2xl font-semibold text-text-primary dark:text-night-text">{value}</p>
      <p className="mt-0.5 text-xs text-text-muted dark:text-night-muted">{hint}</p>
    </div>
  );
}

export function Dashboard({ onNavigate }: { onNavigate: (r: Route) => void }) {
  const { data: briefing, isLoading: briefingLoading } = useQuery({ 
    queryKey: ['briefing'], 
    queryFn: api.getBriefing 
  });
  
  const { data: snap, isLoading: snapLoading } = useQuery({ 
    queryKey: ['snapshot'], 
    queryFn: api.getSnapshot 
  });

  if (briefingLoading || snapLoading || !briefing || !snap) return <Spinner />;

  return (
    <div className="flex flex-col lg:flex-row gap-12">
      {/* 62% Editorial Canvas (Primary Read) */}
      <div className="flex-1 lg:w-[62%] space-y-10">
        <div>
          <p className="text-sm text-text-muted dark:text-night-muted mb-2">{briefing.greeting}</p>
          <h1 className="font-display text-4xl font-normal leading-tight text-text-primary dark:text-night-text">
            {briefing.energyForecast}
          </h1>
        </div>

        {briefing.signals.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={transitionGentle}
            className={`rounded-soft border px-5 py-4 ${SEVERITY_STYLE[briefing.signals[0].severity]}`}
            role="alert"
          >
            <p className="text-sm font-semibold">{briefing.signals[0].description}</p>
            <p className="mt-1 text-sm opacity-90">{briefing.signals[0].recommendation}</p>
            <button
              onClick={() => onNavigate('crisis')}
              className="mt-3 inline-flex rounded-soft bg-black/10 px-4 py-1.5 text-xs font-medium transition hover:bg-black/20 dark:bg-white/10 dark:hover:bg-white/20 focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 focus:outline-none"
            >
              Open crisis plan
            </button>
          </motion.div>
        )}

        <div>
          <h3 className="mb-4 font-display text-xl font-medium text-text-primary dark:text-night-text">Insights</h3>
          <ul className="space-y-4">
            {briefing.insights.map((line, i) => (
              <li key={i} className="text-base leading-relaxed text-text-muted dark:text-night-text/80 max-w-2xl">
                {line}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 38% Marginalia (Metrics & Actions) */}
      <div className="shrink-0 lg:w-[38%] space-y-8 pt-2 lg:pt-0">
        
        <SpoonMeter snap={snap} />

        <div className="surface-card p-5 grid grid-cols-2 gap-4">
          <StatItem
            label="Mood"
            value={snap.moodScore != null ? `${snap.moodScore}/10` : '—'}
            hint={snap.moodScore != null ? 'last reading' : 'no data'}
          />
          <StatItem
            label="Sleep"
            value={snap.sleepHours != null ? `${snap.sleepHours}h` : '—'}
            hint={snap.sleepQuality != null ? `quality ${snap.sleepQuality}/10` : 'no log'}
          />
        </div>

        <div className="space-y-4">
          <h3 className="text-xs uppercase tracking-widest font-semibold text-text-muted dark:text-night-muted">Suggested Focus</h3>
          {briefing.suggestedSkill && (
            <motion.button
              {...hoverTactile}
              onClick={() => onNavigate('practices')}
              className="w-full flex items-center gap-4 rounded-soft bg-brand/5 border border-brand/10 px-4 py-4 text-left transition dark:bg-night-brand/10 dark:border-night-brand/20"
            >
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-brand/10 text-brand dark:bg-night-brand/20 dark:text-night-brand">
                <LeafIcon width={20} height={20} />
              </span>
              <span>
                <span className="block text-sm font-medium text-text-primary dark:text-night-text">
                  {briefing.suggestedSkill.technique}
                </span>
                <span className="block mt-0.5 text-xs text-text-muted dark:text-night-muted">
                  {briefing.suggestedSkill.reason}
                </span>
              </span>
            </motion.button>
          )}

          <div className="surface-card p-5">
            <h3 className="mb-4 text-sm font-medium text-text-primary dark:text-night-text">Upcoming Tasks</h3>
            {briefing.recommendedTasks.length > 0 ? (
              <ul className="space-y-3">
                {briefing.recommendedTasks.map((t) => (
                  <li key={t.id} className="flex items-start gap-3">
                    <span className="mt-0.5 text-brand dark:text-night-brand">
                      <CheckIcon width={16} height={16} />
                    </span>
                    <span className="text-sm text-text-muted dark:text-night-text/80 leading-snug">
                      {t.title}
                    </span>
                    <span className="ml-auto shrink-0 text-xs text-text-muted/60 dark:text-night-muted/60">
                      {t.spoonCost} sp
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm italic text-text-muted dark:text-night-muted">
                No tasks queued that fit your energy. That's allowed.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
