import { getDb } from './db';
import * as repo from './repo';
import { normalizeDailySpoons, spoonWarning } from '../src/shared/spoons';
import type {
  CrisisSignal,
  WellnessSnapshot,
  DailyBriefing,
  Trends,
  TrendPoint,
  Task,
} from '../src/shared/types';

// Cross-module intelligence, ported from core/wellness_orchestrator.py.
// These are deliberately conservative heuristics — they surface *observations*
// and, for the highest-severity signals, route directly to crisis help. They
// are NOT a clinical instrument.

const CRISIS_RECOMMENDATION =
  "If you're struggling right now, you don't have to handle it alone. " +
  'Call or text 988 (Suicide & Crisis Lifeline, US) or open your crisis plan ' +
  'for your contacts and coping steps. If you are in immediate danger, call your ' +
  'local emergency number.';

const mean = (xs: number[]): number | null =>
  xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null;

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

// --- snapshot --------------------------------------------------------------

export function snapshot(): WellnessSnapshot {
  const db = getDb();
  const lastMood = repo.listMoods(1)[0] ?? null;
  const lastSleep = repo.listSleep(1)[0] ?? null;
  const today = todayIso();

  const completedToday = (
    db
      .prepare(`SELECT COUNT(*) n FROM tasks WHERE completed = 1 AND date(completed_at) = ?`)
      .get(today) as { n: number }
  ).n;
  const pending = (
    db.prepare(`SELECT COUNT(*) n FROM tasks WHERE completed = 0`).get() as { n: number }
  ).n;

  const total = normalizeDailySpoons(repo.getSettings().dailySpoons);
  const spentToday = (
    db
      .prepare(`SELECT COALESCE(SUM(spoon_cost),0) s FROM tasks WHERE completed = 1 AND date(completed_at) = ?`)
      .get(today) as { s: number }
  ).s;

  return {
    timestamp: new Date().toISOString(),
    moodScore: lastMood?.moodScore ?? null,
    energyScore: lastMood?.energyLevel ?? null,
    sleepHours: lastSleep?.durationHours ?? null,
    sleepQuality: lastSleep?.quality ?? null,
    tasksCompletedToday: completedToday,
    tasksPending: pending,
    spoonsRemaining: Math.max(0, Math.round((total - spentToday) * 10) / 10),
    spoonsTotal: total,
  };
}

// --- crisis signals --------------------------------------------------------

export function detectCrisisSignals(): CrisisSignal[] {
  const db = getDb();
  const signals: CrisisSignal[] = [];
  const recentMoods = db
    .prepare(`SELECT mood_score FROM mood_entries WHERE timestamp >= datetime('now','-3 days') ORDER BY timestamp DESC`)
    .all() as { mood_score: number }[];
  const moodValues = recentMoods.map((r) => r.mood_score).filter((v) => v != null);

  let avgSleep: number | null = null;

  if (moodValues.length) {
    const avgMood = mean(moodValues);

    const recentSleep = db
      .prepare(`SELECT duration_hours FROM sleep_logs WHERE date >= date('now','-3 days') ORDER BY date DESC`)
      .all() as { duration_hours: number }[];
    avgSleep = mean(recentSleep.map((r) => r.duration_hours).filter((v) => v != null));

    // Mood crash + sleep deprivation
    if (avgMood != null && avgMood <= 3.5 && avgSleep != null && avgSleep < 5) {
      signals.push({
        severity: 'moderate',
        sources: ['mood', 'sleep'],
        description: `Your mood has been low and sleep short over the past few days (avg mood ${avgMood.toFixed(1)}, avg sleep ${avgSleep.toFixed(1)}h).`,
        recommendation:
          'Consider your crisis plan, reach out to a trusted contact, and prioritise rest over productivity today.',
      });
    }

    // Very low absolute mood — urgent regardless of trend
    const latestMood = moodValues[0];
    if (latestMood != null && latestMood <= 2) {
      signals.push({
        severity: 'urgent',
        sources: ['mood'],
        description: `Your most recent mood rating is very low (${latestMood}/10).`,
        recommendation: CRISIS_RECOMMENDATION,
      });
    }

    // Rapid mood drop, severity scales with magnitude
    if (moodValues.length >= 2) {
      const latest = moodValues[0];
      const previous = moodValues[1];
      const drop = previous - latest;
      if (drop >= 4) {
        const urgent = drop >= 6 || latest <= 2;
        const alreadyFlagged = latest <= 2 && latestMood != null && latestMood <= 2;
        if (!alreadyFlagged) {
          signals.push({
            severity: urgent ? 'urgent' : 'moderate',
            sources: ['mood'],
            description: `Your mood dropped from ${previous} to ${latest} recently.`,
            recommendation: urgent
              ? CRISIS_RECOMMENDATION
              : 'A grounding exercise or brief walk may help stabilise your baseline. If it keeps sliding, open your crisis plan.',
          });
        }
      }
    }
  }

  // Medication-style adherence is out of scope for this build; we instead flag
  // a sustained skipped-practice + low-mood pattern below via insights.

  // Surface a neutral observation for anyone who records sustained high energy
  // alongside short sleep. This is never conditioned on, or framed as, a
  // diagnosis.
  const energies = db
    .prepare(`SELECT energy_level FROM mood_entries WHERE timestamp >= datetime('now','-7 days') AND energy_level IS NOT NULL`)
    .all() as { energy_level: number }[];
  const energyVals = energies.map((r) => r.energy_level);
  const avgEnergy = mean(energyVals);
  if (avgEnergy != null && avgEnergy >= 8 && avgSleep != null && avgSleep < 5) {
    signals.push({
      severity: 'info',
      sources: ['energy', 'sleep'],
      description: 'Your recent entries combine high energy with short sleep.',
      recommendation:
        'Consider protecting a regular sleep window and sharing the pattern with someone you trust if it feels unusual or concerning.',
    });
  }

  const rank: Record<CrisisSignal['severity'], number> = { urgent: 0, moderate: 1, mild: 2, info: 3 };
  signals.sort((a, b) => rank[a.severity] - rank[b.severity]);
  return signals;
}

// --- daily briefing --------------------------------------------------------

function suggestSkill(snap: WellnessSnapshot): DailyBriefing['suggestedSkill'] {
  if (snap.energyScore != null && snap.energyScore <= 3) {
    return { kind: 'meditation', technique: 'Body scan', reason: 'Low energy — a gentle reset rather than a push.' };
  }
  if (snap.moodScore != null && snap.moodScore <= 4) {
    return { kind: 'grounding', technique: '5-4-3-2-1 senses', reason: 'A low mood reading — grounding can steady the ground under you.' };
  }
  if (snap.sleepHours != null && snap.sleepHours < 6) {
    return { kind: 'breathing', technique: 'Box breathing', reason: 'Short sleep last night — slow breathing eases the strain.' };
  }
  return { kind: 'focus', technique: '25-minute focus block', reason: 'Steady baseline — a protected block is a good use of it.' };
}

function greetingFor(name: string): string {
  const h = new Date().getHours();
  const part = h < 12 ? 'Good morning' : h < 18 ? 'Good afternoon' : 'Good evening';
  return name ? `${part}, ${name}` : part;
}

function energyForecast(snap: WellnessSnapshot): string {
  const e = snap.energyScore;
  const s = snap.sleepHours;
  if (e == null && s == null) return 'Add a check-in or a night of sleep to give Today more context.';
  if (s != null && s < 5) return 'Short sleep is in your recent log. Choose a lighter plan if that matches how you feel.';
  if (e != null && e >= 7) return 'Your recent energy entry is high. You still choose what belongs in today.';
  if (e != null && e <= 3) return 'Your recent energy entry is low. A smaller next step may fit better.';
  return 'Your recent entry sits in the middle. Use the budget you chose to decide what fits.';
}

export function dailyBriefing(): DailyBriefing {
  const snap = snapshot();
  const settings = repo.getSettings();
  const signals = detectCrisisSignals();
  const insights: string[] = [];

  const warn = spoonWarning(snap.spoonsRemaining, snap.spoonsTotal);
  if (warn === 'low' || warn === 'empty') {
    insights.push(`You have ${snap.spoonsRemaining} of ${snap.spoonsTotal} spoons left today. Consider resting before adding more.`);
  }
  if (snap.tasksCompletedToday > 0) {
    insights.push(`You've finished ${snap.tasksCompletedToday} task${snap.tasksCompletedToday === 1 ? '' : 's'} today. That counts.`);
  }
  if (snap.sleepHours != null && snap.sleepHours >= 7) {
    insights.push(`${snap.sleepHours}h of sleep — a solid foundation to build on.`);
  }
  if (!insights.length) {
    insights.push('A quiet start. Whatever today holds, you only have to take the next small step.');
  }

  // Recommend tasks that fit remaining energy: cheapest spoon-cost first.
  const open = repo
    .listTasks(false)
    .filter((t) => t.spoonCost <= snap.spoonsRemaining)
    .slice(0, 3);

  return {
    date: todayIso(),
    greeting: greetingFor(settings.displayName),
    energyForecast: energyForecast(snap),
    insights,
    suggestedSkill: suggestSkill(snap),
    recommendedTasks: open as Task[],
    signals,
  };
}

// --- trends ----------------------------------------------------------------

export function trends(days: number): Trends {
  const db = getDb();
  const since = `-${days} days`;

  const moodRows = db
    .prepare(`SELECT date(timestamp) d, AVG(mood_score) v FROM mood_entries WHERE timestamp >= datetime('now', ?) GROUP BY d ORDER BY d`)
    .all(since) as { d: string; v: number }[];
  const energyRows = db
    .prepare(`SELECT date(timestamp) d, AVG(energy_level) v FROM mood_entries WHERE energy_level IS NOT NULL AND timestamp >= datetime('now', ?) GROUP BY d ORDER BY d`)
    .all(since) as { d: string; v: number }[];
  const sleepRows = db
    .prepare(`SELECT date d, AVG(duration_hours) v FROM sleep_logs WHERE date >= date('now', ?) GROUP BY d ORDER BY d`)
    .all(since) as { d: string; v: number }[];

  const toPoints = (rows: { d: string; v: number }[]): TrendPoint[] =>
    rows.map((r) => ({ date: r.d, value: r.v == null ? null : Math.round(r.v * 10) / 10 }));

  return {
    mood: toPoints(moodRows),
    sleep: toPoints(sleepRows),
    energy: toPoints(energyRows),
  };
}
