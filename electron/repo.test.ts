import Database from 'better-sqlite3';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import * as repo from './repo';
import { SCHEMA } from './schema';

// repo.ts talks to the encrypted store through electron/db.ts; these tests
// swap that module for a plain in-memory SQLite wearing the same schema and
// consent triggers, so the repository logic itself runs unmodified.
const holder = vi.hoisted(() => ({ db: null as unknown as Database.Database }));

vi.mock('./db', () => ({
  getDb: () => holder.db,
  closeDb: () => undefined,
}));

beforeEach(() => {
  holder.db = new Database(':memory:');
  holder.db.exec(SCHEMA);
});

afterEach(() => holder.db.close());

function grantConsent(): void {
  repo.saveSettings({ privacyConsentAt: '2026-07-14T12:00:00.000Z' });
}

describe('settings', () => {
  it('defaults nudges off and round-trips saved settings', () => {
    // M9: OS notifications are opt-in for an app whose pitch is privacy.
    expect(repo.getSettings().nudges).toBe(false);

    grantConsent();
    const saved = repo.saveSettings({ displayName: 'Maya', nudges: true });
    expect(saved.nudges).toBe(true);
    expect(repo.getSettings().displayName).toBe('Maya');
    expect(repo.getSettings().nudges).toBe(true);
  });
});

describe('tasks', () => {
  it('creates, lists, updates, toggles, and deletes a task', () => {
    grantConsent();
    const task = repo.createTask({
      title: 'Refill prescription',
      priority: 'high',
      energyRequired: 3,
      estimatedDuration: 20,
    });
    expect(task.id).toBeGreaterThan(0);
    expect(task.completed).toBe(false);
    expect(task.spoonCost).toBeGreaterThan(0);
    expect(repo.listTasks(false).map((t) => t.id)).toContain(task.id);

    const renamed = repo.updateTask(task.id, { title: 'Refill prescription Thursday' });
    expect(renamed.title).toBe('Refill prescription Thursday');

    const done = repo.toggleTask(task.id);
    expect(done.completed).toBe(true);
    expect(done.completedAt).not.toBeNull();
    expect(repo.listTasks(false)).toHaveLength(0);
    expect(repo.listTasks(true)).toHaveLength(1);

    const undone = repo.toggleTask(task.id);
    expect(undone.completed).toBe(false);
    expect(undone.completedAt).toBeNull();

    repo.deleteTask(task.id);
    expect(repo.listTasks(true)).toHaveLength(0);
  });

  it('awards XP on completion and reverses it on uncheck', () => {
    grantConsent();
    const task = repo.createTask({ title: 'Make the bed', spoonCost: 2 });
    repo.toggleTask(task.id);
    let g = repo.getGamification();
    expect(g.totalXp).toBe(20);
    expect(g.currentXp).toBe(20);

    repo.toggleTask(task.id);
    g = repo.getGamification();
    expect(g.totalXp).toBe(0);
    expect(g.currentXp).toBe(0);
  });

  it('rolls back the task flip when the XP write fails', () => {
    grantConsent();
    const task = repo.createTask({ title: 'Atomicity probe', spoonCost: 2 });
    // Force the gamification half of toggleTask to fail; the completion flip
    // must roll back with it instead of persisting alone.
    holder.db.exec('DROP TABLE gamification');

    expect(() => repo.toggleTask(task.id)).toThrow();
    const after = repo.listTasks(true)[0];
    expect(after.completed).toBe(false);
    expect(after.completedAt).toBeNull();
  });
});

describe('check-ins and journal', () => {
  it('round-trips mood, sleep, and journal entries', () => {
    grantConsent();
    const mood = repo.createMood({ moodScore: 7, energyLevel: 6, anxietyLevel: 3 });
    expect(mood.moodScore).toBe(7);
    expect(repo.listMoods(10)).toHaveLength(1);

    // Wake before bedtime means the night crossed midnight.
    const sleep = repo.createSleep({ date: '2026-07-14', bedtime: '23:30', wakeTime: '07:00', quality: 8 });
    expect(sleep.durationHours).toBe(7.5);
    expect(repo.listSleep(10)[0].date).toBe('2026-07-14');

    const entry = repo.createJournal({ content: 'A smaller, kinder list.', moodScore: 7 });
    expect(repo.listJournal(10)).toHaveLength(1);
    repo.deleteJournal(entry.id);
    expect(repo.listJournal(10)).toHaveLength(0);
  });
});
