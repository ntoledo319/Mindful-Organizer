// Dev-only demo seed. Populates the local SQLite DB with a warm, realistic
// fortnight of data so the Store screenshots look alive. The only caller is
// runScreenshots() (electron/screenshot.ts), which main.ts reaches solely when
// HEARTH_SCREENSHOT=1 — so this never runs in a normal or packaged launch.
import { getDb } from './db';
import * as repo from './repo';

function isoDaysAgo(days: number, hour = 9, minute = 0): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  d.setHours(hour, minute, 0, 0);
  // SQLite datetime() comparisons use 'YYYY-MM-DD HH:MM:SS'.
  return d.toISOString().slice(0, 19).replace('T', ' ');
}

function dateDaysAgo(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

// A gentle two-week arc: a rough patch mid-window that lifts back toward steady.
// Kept clear of the crisis thresholds (recent mood >= 5, sleep >= 6h) so the
// dashboard reads warm, not alarmed.
const MOOD_ARC = [6, 7, 5, 6, 4, 5, 6, 7, 6, 5, 7, 8, 7, 8];
const ENERGY_ARC = [5, 6, 4, 5, 4, 5, 6, 7, 6, 5, 6, 7, 7, 8];
const ANXIETY_ARC = [4, 3, 5, 4, 6, 5, 4, 3, 4, 4, 3, 2, 3, 2];
const SLEEP_HOURS = [6.5, 7.0, 5.5, 6.0, 5.0, 6.5, 7.5, 8.0, 7.0, 6.5, 7.5, 8.0, 7.5, 8.0];
const SLEEP_QUALITY = [6, 7, 5, 6, 4, 6, 8, 8, 7, 6, 8, 9, 8, 9];

export function seedDemoData(): void {
  const db = getDb();
  const already = (db.prepare('SELECT COUNT(*) n FROM tasks').get() as { n: number }).n;
  if (already > 0) return; // idempotent — a seeded DB is left alone

  repo.saveSettings({
    displayName: 'Maya',
    conditions: ['adhd', 'anxiety'],
    onboarded: true,
    theme: 'light',
    dailySpoons: 12,
  });

  // Tasks — a believable mix of areas, priorities, and energy costs. A couple
  // already done today so the dashboard shows progress and spent spoons.
  repo.createTask({ title: 'Refill prescription before the weekend', priority: 'high', category: 'Health', energyRequired: 3, estimatedDuration: 20 });
  repo.createTask({ title: 'Draft the project update for Lena', priority: 'high', category: 'Work', energyRequired: 7, estimatedDuration: 60 });
  repo.createTask({ title: 'Ten-minute kitchen reset', priority: 'medium', category: 'Home', energyRequired: 2, estimatedDuration: 10 });
  repo.createTask({ title: 'Reply to Sam about the weekend', priority: 'low', category: 'Life', energyRequired: 2, estimatedDuration: 5 });
  repo.createTask({ title: 'Walk to the park and back', priority: 'medium', category: 'Health', energyRequired: 4, estimatedDuration: 30 });
  repo.createTask({ title: 'Sort the overflowing inbox', priority: 'medium', category: 'Work', energyRequired: 6, estimatedDuration: 45 });

  const done1 = repo.createTask({ title: 'Take morning meds', priority: 'high', category: 'Health', energyRequired: 1, estimatedDuration: 2 });
  const done2 = repo.createTask({ title: 'Make the bed', priority: 'low', category: 'Home', energyRequired: 1, estimatedDuration: 5 });
  for (const t of [done1, done2]) {
    db.prepare(`UPDATE tasks SET completed = 1, completed_at = datetime('now'), updated_at = datetime('now') WHERE id = ?`).run(t.id);
  }

  // Mood + sleep across ~2 weeks, oldest first, with explicit dated rows.
  const insMood = db.prepare(
    `INSERT INTO mood_entries (timestamp, mood_score, energy_level, anxiety_level, emotions, notes)
     VALUES (@ts, @m, @e, @a, @emo, @notes)`,
  );
  const insSleep = db.prepare(
    `INSERT INTO sleep_logs (date, bedtime, wake_time, quality, duration_hours, notes)
     VALUES (@date, @bed, @wake, @q, @dur, @notes)`,
  );
  const n = MOOD_ARC.length;
  for (let i = 0; i < n; i++) {
    const daysAgo = n - 1 - i; // i=0 → oldest, last → today
    insMood.run({
      ts: isoDaysAgo(daysAgo, 8, 30),
      m: MOOD_ARC[i],
      e: ENERGY_ARC[i],
      a: ANXIETY_ARC[i],
      emo: null,
      notes: i === n - 1 ? 'Steadier than last week. The walks are helping.' : null,
    });
    insSleep.run({
      date: dateDaysAgo(daysAgo),
      bed: '23:30',
      wake: '07:00',
      q: SLEEP_QUALITY[i],
      dur: SLEEP_HOURS[i],
      notes: null,
    });
  }

  repo.createJournal({
    title: 'A smaller, kinder list',
    content:
      "Tried matching the list to the energy I actually had instead of the energy I wished for. " +
      "Got the meds refilled and went for the walk. The update for Lena can wait until tomorrow when I'm fresher — " +
      "and noticing that without guilt feels like the whole point.",
    moodScore: 7,
    prompt: 'Where did you feel most like yourself today?',
  });

  repo.logPractice({ kind: 'breathing', technique: 'Box breathing', durationSeconds: 240, preDistress: 6, postDistress: 3 });
  repo.logPractice({ kind: 'grounding', technique: '5-4-3-2-1 senses', durationSeconds: 180, preDistress: 7, postDistress: 4 });

  repo.saveCrisisPlan({
    warningSigns: ['Skipping meals', 'Avoiding messages for days', 'Sleeping past noon'],
    copingStrategies: ['Step outside for five minutes', 'Text one person', 'Box breathing, four rounds'],
    contacts: [
      { name: 'Sam', relationship: 'Sister', phone: '555-0142' },
      { name: 'Dr. Okafor', relationship: 'Therapist', phone: '555-0199' },
    ],
    safeNote: "You've come through every hard day so far. This one is not the exception. Rest counts as progress.",
  });
}
