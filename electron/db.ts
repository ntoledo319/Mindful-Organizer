import Database from 'better-sqlite3';
import { app } from 'electron';
import { join } from 'node:path';
import { mkdirSync } from 'node:fs';

// Single, local, offline-first SQLite store. No cloud, no telemetry — the
// whole point of Hearth is that your psychological data never leaves the
// machine. WAL mode keeps reads fast while a write is in flight.

let db: Database.Database | null = null;

const SCHEMA = `
CREATE TABLE IF NOT EXISTS tasks (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  title              TEXT    NOT NULL,
  description        TEXT,
  priority           TEXT    NOT NULL DEFAULT 'medium',
  category           TEXT    NOT NULL DEFAULT 'Life',
  energy_required    INTEGER NOT NULL DEFAULT 5,
  due_date           TEXT,
  completed          INTEGER NOT NULL DEFAULT 0,
  completed_at       TEXT,
  estimated_duration INTEGER,
  spoon_cost         REAL    NOT NULL DEFAULT 1,
  created_at         TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at         TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS mood_entries (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp     TEXT    NOT NULL DEFAULT (datetime('now')),
  mood_score    INTEGER NOT NULL CHECK (mood_score BETWEEN 1 AND 10),
  energy_level  INTEGER CHECK (energy_level BETWEEN 1 AND 10),
  anxiety_level INTEGER CHECK (anxiety_level BETWEEN 0 AND 10),
  emotions      TEXT,
  notes         TEXT
);

CREATE TABLE IF NOT EXISTS sleep_logs (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  date           TEXT    NOT NULL,
  bedtime        TEXT    NOT NULL,
  wake_time      TEXT    NOT NULL,
  quality        INTEGER NOT NULL CHECK (quality BETWEEN 1 AND 10),
  duration_hours REAL    NOT NULL,
  notes          TEXT,
  created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS journal_entries (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp  TEXT    NOT NULL DEFAULT (datetime('now')),
  title      TEXT,
  content    TEXT    NOT NULL,
  mood_score INTEGER CHECK (mood_score BETWEEN 1 AND 10),
  prompt     TEXT
);

CREATE TABLE IF NOT EXISTS practice_sessions (
  id               INTEGER PRIMARY KEY AUTOINCREMENT,
  kind             TEXT    NOT NULL,
  technique        TEXT    NOT NULL,
  duration_seconds INTEGER NOT NULL,
  pre_distress     INTEGER,
  post_distress    INTEGER,
  timestamp        TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS settings (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_mood_ts ON mood_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_sleep_date ON sleep_logs(date);
CREATE INDEX IF NOT EXISTS idx_journal_ts ON journal_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_practice_ts ON practice_sessions(timestamp);
`;

export function getDb(): Database.Database {
  if (db) return db;
  const dir = join(app.getPath('userData'), 'data');
  mkdirSync(dir, { recursive: true });
  const file = join(dir, 'hearth.db');
  db = new Database(file);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');
  db.exec(SCHEMA);
  return db;
}

export function closeDb(): void {
  if (db) {
    db.close();
    db = null;
  }
}
