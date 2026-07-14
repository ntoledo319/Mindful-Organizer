import Database from 'better-sqlite3';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { SCHEMA } from './schema';

let db: Database.Database;

beforeEach(() => {
  db = new Database(':memory:');
  db.exec(SCHEMA);
});

afterEach(() => db.close());

function grantConsent(): void {
  db.prepare('INSERT INTO settings (key, value) VALUES (?, ?)').run(
    'app',
    JSON.stringify({
      displayName: 'Maya',
      onboarded: true,
      privacyConsentAt: '2026-07-14T12:00:00.000Z',
    }),
  );
}

describe('database consent guard', () => {
  it('rejects sensitive writes before express consent', () => {
    expect(() =>
      db.prepare('INSERT INTO tasks (title) VALUES (?)').run('Private task'),
    ).toThrow(/Explicit privacy consent/);
    expect(() =>
      db.prepare('INSERT INTO gamification DEFAULT VALUES').run(),
    ).toThrow(/Explicit privacy consent/);
    expect(() =>
      db.prepare('INSERT INTO settings (key, value) VALUES (?, ?)').run(
        'app',
        JSON.stringify({
          displayName: 'Maya',
          onboarded: true,
          privacyConsentAt: 'this is long but not a timestamp',
        }),
      ),
    ).toThrow(/Explicit privacy consent/);
    expect(() =>
      db.prepare('INSERT INTO settings (key, value) VALUES (?, ?)').run(
        'app',
        JSON.stringify({ displayName: 'Maya', onboarded: true }),
      ),
    ).toThrow(/Explicit privacy consent/);
  });

  it('accepts writes only after a timestamped opt-in is stored', () => {
    grantConsent();
    db.prepare('INSERT INTO tasks (title) VALUES (?)').run('Private task');
    expect(
      (db.prepare('SELECT COUNT(*) AS count FROM tasks').get() as { count: number }).count,
    ).toBe(1);
  });

  it('requires the destructive erase flow instead of silently clearing consent', () => {
    grantConsent();
    expect(() =>
      db.prepare('UPDATE settings SET value = ? WHERE key = ?').run(
        JSON.stringify({ displayName: 'Maya', onboarded: true, privacyConsentAt: null }),
        'app',
      ),
    ).toThrow(/Erase all data/);
    expect(() =>
      db.prepare('DELETE FROM settings WHERE key = ?').run('app'),
    ).toThrow(/Erase all data/);
  });
});
