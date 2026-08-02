import Database from 'better-sqlite3';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import * as repo from './repo';
import * as wellness from './wellness';
import { SCHEMA } from './schema';

// The local-day boundary cases need local and UTC dates to differ at the
// instant under test, so on POSIX this file pins TZ=America/Los_Angeles (both
// V8 and SQLite's 'localtime' honor it per call). Windows ignores the TZ
// variable; there the cases below detect that local and UTC dates coincide
// (or that the box's own zone skews differently) and skip rather than assert
// a zone-specific answer. Run under any machine TZ — the file sets its own.
if (process.platform !== 'win32') process.env.TZ = 'America/Los_Angeles';

const holder = vi.hoisted(() => ({ db: null as unknown as Database.Database }));

vi.mock('./db', () => ({
  getDb: () => holder.db,
  closeDb: () => undefined,
}));

function localIso(d: Date): string {
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${d.getFullYear()}-${mm}-${dd}`;
}

function utcIso(d: Date): string {
  return d.toISOString().slice(0, 10);
}

// 23:30 local time today. In zones behind UTC this instant is already tomorrow
// in UTC — exactly the skew M1 fixes. The roll-over probe starts at 23:45.
const LOCAL_EVENING = new Date();
LOCAL_EVENING.setHours(23, 30, 0, 0);
const LOCAL_LATE = new Date();
LOCAL_LATE.setHours(23, 45, 0, 0);
const LOCAL_DAY_DIFFERS = localIso(LOCAL_EVENING) !== utcIso(LOCAL_EVENING);

beforeEach(() => {
  holder.db = new Database(':memory:');
  holder.db.exec(SCHEMA);
  vi.useFakeTimers();
});

afterEach(() => {
  vi.useRealTimers();
  holder.db.close();
});

function grantConsent(): void {
  repo.saveSettings({ privacyConsentAt: '2026-07-14T12:00:00.000Z' });
}

describe('local-day boundary (M1)', () => {
  it.runIf(LOCAL_DAY_DIFFERS)(
    'counts a task completed at 23:30 local against the local day, not the UTC day',
    () => {
      grantConsent();
      vi.setSystemTime(LOCAL_LATE);
      // Sanity: UTC really has rolled to the next date while local has not.
      expect(utcIso(new Date())).not.toBe(localIso(new Date()));

      const task = repo.createTask({ title: 'Take evening meds', spoonCost: 2 });
      repo.toggleTask(task.id);

      const snap = wellness.snapshot();
      expect(snap.tasksCompletedToday).toBe(1);
      expect(snap.spoonsRemaining).toBe(10); // 12 - 2, against local midnight
      expect(wellness.dailyBriefing().date).toBe(localIso(new Date()));
    },
  );

  it.runIf(LOCAL_DAY_DIFFERS)('rolls the count over at local midnight, not at 00:00 UTC', () => {
    grantConsent();
    vi.setSystemTime(LOCAL_LATE);
    const task = repo.createTask({ title: 'Wind-down routine', spoonCost: 1 });
    repo.toggleTask(task.id);
    expect(wellness.snapshot().tasksCompletedToday).toBe(1);

    // 30 minutes later: past local midnight, still the same UTC date as the
    // completion instant. The old UTC boundary still counted it; the local
    // boundary must not.
    vi.setSystemTime(new Date(LOCAL_LATE.getTime() + 30 * 60 * 1000));
    expect(wellness.snapshot().tasksCompletedToday).toBe(0);
  });

  it.runIf(LOCAL_DAY_DIFFERS)('buckets mood and energy trends by local calendar date, like sleep', () => {
    grantConsent();
    const utcStamp = LOCAL_EVENING.toISOString().slice(0, 19).replace('T', ' ');
    const localDay = localIso(LOCAL_EVENING);
    holder.db
      .prepare('INSERT INTO mood_entries (timestamp, mood_score, energy_level) VALUES (?, ?, ?)')
      .run(utcStamp, 7, 6);
    holder.db
      .prepare('INSERT INTO sleep_logs (date, bedtime, wake_time, quality, duration_hours) VALUES (?, ?, ?, ?, ?)')
      .run(localDay, '23:30', '07:00', 8, 7.5);

    const result = wellness.trends(7);
    expect(result.mood).toEqual([{ date: localDay, value: 7 }]);
    expect(result.energy).toEqual([{ date: localDay, value: 6 }]);
    expect(result.sleep).toEqual([{ date: localDay, value: 7.5 }]);
  });

  it('counts a task completed moments ago against today in any timezone', () => {
    grantConsent();
    vi.setSystemTime('2026-07-15T12:00:00.000Z');
    const task = repo.createTask({ title: 'Midday task', spoonCost: 3 });
    repo.toggleTask(task.id);

    const snap = wellness.snapshot();
    expect(snap.tasksCompletedToday).toBe(1);
    expect(snap.tasksPending).toBe(0);
    expect(snap.spoonsRemaining).toBe(9);
    expect(snap.spoonsTotal).toBe(12);
  });
});

describe('spoon budget edges', () => {
  it('spends spoons down to exactly zero without going negative', () => {
    grantConsent();
    vi.setSystemTime('2026-07-15T12:00:00.000Z');
    repo.toggleTask(repo.createTask({ title: 'Five', spoonCost: 5 }).id);
    expect(wellness.snapshot().spoonsRemaining).toBe(7);

    repo.toggleTask(repo.createTask({ title: 'Seven', spoonCost: 7 }).id);
    expect(wellness.snapshot().spoonsRemaining).toBe(0);
    // An empty budget surfaces the low-spoon insight in the briefing.
    expect(wellness.dailyBriefing().insights.join(' ')).toContain('0 of 12 spoons');
  });

  it('recommends up to three open tasks that fit the remaining budget', () => {
    grantConsent();
    vi.setSystemTime('2026-07-15T12:00:00.000Z');
    repo.createTask({ title: 'Too heavy for today', spoonCost: 13 });
    for (const title of ['One', 'Two', 'Three', 'Four']) {
      repo.createTask({ title, spoonCost: 1 });
    }

    const recommended = wellness.dailyBriefing().recommendedTasks;
    expect(recommended.map((t) => t.title)).toEqual(['One', 'Two', 'Three']);
  });

  it('only recommends tasks whose cost fits the spoons left', () => {
    grantConsent();
    vi.setSystemTime('2026-07-15T12:00:00.000Z');
    repo.toggleTask(repo.createTask({ title: 'Big morning push', spoonCost: 11 }).id);
    repo.createTask({ title: 'Costs two', spoonCost: 2 });
    repo.createTask({ title: 'Costs one', spoonCost: 1 });

    const recommended = wellness.dailyBriefing().recommendedTasks;
    expect(recommended.map((t) => t.title)).toEqual(['Costs one']);
  });
});
