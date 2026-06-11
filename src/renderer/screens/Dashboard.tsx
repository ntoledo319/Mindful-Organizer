import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../lib/api';
import { useStore } from '../state/store';
import { spoonWarning } from '@shared/spoons';
import type { DailyBriefing, WellnessSnapshot, CrisisSignal } from '@shared/types';
import type { Route } from '../App';
import { Spinner } from '../components/ui';
import { LeafIcon, CheckIcon } from '../components/icons';

const SEVERITY_STYLE: Record<CrisisSignal['severity'], string> = {
  urgent: 'border-ember/40 bg-ember/10 text-ember',
  moderate: 'border-ember/30 bg-ember/5 text-ember',
  mild: 'border-lavender-deep/30 bg-lavender/15 text-charcoal dark:text-cream',
  info: 'border-sage/20 bg-sage/5 text-charcoal dark:text-cream',
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
  const bar = warn === 'empty' || warn === 'low' ? 'bg-ember' : warn === 'mindful' ? 'bg-lavender-deep' : 'bg-sage';
  return (
    <div className="glass-card p-5">
      <div className="flex items-baseline justify-between">
        <h3 className="text-sm font-medium text-charcoal-soft dark:text-cream/70">Energy budget</h3>
        <span className="font-display text-lg font-semibold text-sage dark:text-eucalyptus">
          {snap.spoonsRemaining}
          <span className="text-sm text-charcoal-mute dark:text-cream/40"> / {snap.spoonsTotal} spoons</span>
        </span>
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-charcoal/8 dark:bg-white/10">
        <motion.div
          className={`h-full rounded-full ${bar}`}
          initial={{ width: 0 }}
          animate={{ width: `${Math.max(pct, 3)}%` }}
          transition={{ type: 'spring', stiffness: 120, damping: 20 }}
        />
      </div>
      <p className="mt-2 text-xs text-charcoal-mute dark:text-cream/50">{label}</p>
    </div>
  );
}

function StatCard({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="glass-card p-5">
      <h3 className="text-sm font-medium text-charcoal-soft dark:text-cream/70">{label}</h3>
      <p className="mt-1 font-display text-2xl font-semibold text-charcoal dark:text-cream">{value}</p>
      <p className="mt-0.5 text-xs text-charcoal-mute dark:text-cream/50">{hint}</p>
    </div>
  );
}

export function Dashboard({ onNavigate }: { onNavigate: (r: Route) => void }) {
  const { dataVersion } = useStore();
  const [briefing, setBriefing] = useState<DailyBriefing | null>(null);
  const [snap, setSnap] = useState<WellnessSnapshot | null>(null);

  useEffect(() => {
    void Promise.all([api.getBriefing(), api.getSnapshot()]).then(([b, s]) => {
      setBriefing(b);
      setSnap(s);
    });
  }, [dataVersion]);

  if (!briefing || !snap) return <Spinner />;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-sm text-charcoal-mute dark:text-cream/50">{briefing.greeting}.</p>
        <h1 className="mt-1 font-display text-3xl font-semibold tracking-tight text-charcoal dark:text-cream">
          {briefing.energyForecast}
        </h1>
      </div>

      {briefing.signals.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          className={`rounded-glass border px-5 py-4 ${SEVERITY_STYLE[briefing.signals[0].severity]}`}
        >
          <p className="text-sm font-semibold">{briefing.signals[0].description}</p>
          <p className="mt-1 text-sm opacity-90">{briefing.signals[0].recommendation}</p>
          <button
            onClick={() => onNavigate('crisis')}
            className="mt-3 inline-flex rounded-full bg-charcoal px-4 py-1.5 text-xs font-medium text-cream dark:bg-cream dark:text-charcoal"
          >
            Open crisis plan
          </button>
        </motion.div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <SpoonMeter snap={snap} />
        <StatCard
          label="Mood"
          value={snap.moodScore != null ? `${snap.moodScore}/10` : '—'}
          hint={snap.moodScore != null ? 'last check-in' : 'no reading yet'}
        />
        <StatCard
          label="Sleep"
          value={snap.sleepHours != null ? `${snap.sleepHours}h` : '—'}
          hint={snap.sleepQuality != null ? `quality ${snap.sleepQuality}/10` : 'no log yet'}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="glass-card p-5">
          <h3 className="mb-3 font-display text-lg font-semibold text-charcoal dark:text-cream">A few things I noticed</h3>
          <ul className="space-y-2">
            {briefing.insights.map((line, i) => (
              <li key={i} className="flex gap-2 text-sm text-charcoal-soft dark:text-cream/70">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-eucalyptus" />
                {line}
              </li>
            ))}
          </ul>
        </div>

        <div className="glass-card flex flex-col p-5">
          <h3 className="mb-3 font-display text-lg font-semibold text-charcoal dark:text-cream">Gentle next step</h3>
          {briefing.suggestedSkill && (
            <button
              onClick={() => onNavigate('practices')}
              className="mb-4 flex items-center gap-3 rounded-2xl bg-lavender/20 px-4 py-3 text-left transition hover:bg-lavender/30 dark:bg-lavender/10"
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-lavender-deep/20 text-sage dark:text-eucalyptus">
                <LeafIcon width={18} height={18} />
              </span>
              <span>
                <span className="block text-sm font-medium text-charcoal dark:text-cream">
                  {briefing.suggestedSkill.technique}
                </span>
                <span className="block text-xs text-charcoal-mute dark:text-cream/50">
                  {briefing.suggestedSkill.reason}
                </span>
              </span>
            </button>
          )}
          {briefing.recommendedTasks.length > 0 ? (
            <ul className="space-y-1.5">
              {briefing.recommendedTasks.map((t) => (
                <li key={t.id} className="flex items-center gap-2 text-sm text-charcoal-soft dark:text-cream/70">
                  <CheckIcon width={15} height={15} className="text-sage/50" />
                  {t.title}
                  <span className="ml-auto text-xs text-charcoal-mute dark:text-cream/40">{t.spoonCost} sp</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-charcoal-mute dark:text-cream/50">
              No tasks queued that fit your energy. That's allowed.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
