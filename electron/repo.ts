import type Database from 'better-sqlite3';
import { getDb } from './db';
import { estimateSpoonCost } from '../src/shared/spoons';
import type {
  Task,
  TaskInput,
  MoodEntry,
  MoodInput,
  SleepLog,
  SleepInput,
  JournalEntry,
  JournalInput,
  PracticeSession,
  PracticeInput,
  CrisisPlan,
  Settings,
  Condition,
} from '../src/shared/types';

type Row = Record<string, unknown>;

const DEFAULT_SETTINGS: Settings = {
  conditions: [],
  displayName: '',
  onboarded: false,
  theme: 'system',
  dailySpoons: 12,
};

// --- row mappers -----------------------------------------------------------

function mapTask(r: Row): Task {
  return {
    id: r.id as number,
    title: r.title as string,
    description: (r.description as string) ?? null,
    priority: r.priority as Task['priority'],
    category: r.category as string,
    energyRequired: r.energy_required as number,
    dueDate: (r.due_date as string) ?? null,
    completed: !!r.completed,
    completedAt: (r.completed_at as string) ?? null,
    estimatedDuration: (r.estimated_duration as number) ?? null,
    spoonCost: r.spoon_cost as number,
    createdAt: r.created_at as string,
    updatedAt: r.updated_at as string,
  };
}

function mapMood(r: Row): MoodEntry {
  return {
    id: r.id as number,
    timestamp: r.timestamp as string,
    moodScore: r.mood_score as number,
    energyLevel: (r.energy_level as number) ?? null,
    anxietyLevel: (r.anxiety_level as number) ?? null,
    emotions: (r.emotions as string) ?? null,
    notes: (r.notes as string) ?? null,
  };
}

function mapSleep(r: Row): SleepLog {
  return {
    id: r.id as number,
    date: r.date as string,
    bedtime: r.bedtime as string,
    wakeTime: r.wake_time as string,
    quality: r.quality as number,
    durationHours: r.duration_hours as number,
    notes: (r.notes as string) ?? null,
  };
}

function mapJournal(r: Row): JournalEntry {
  return {
    id: r.id as number,
    timestamp: r.timestamp as string,
    title: (r.title as string) ?? null,
    content: r.content as string,
    moodScore: (r.mood_score as number) ?? null,
    prompt: (r.prompt as string) ?? null,
  };
}

function mapPractice(r: Row): PracticeSession {
  return {
    id: r.id as number,
    kind: r.kind as PracticeSession['kind'],
    technique: r.technique as string,
    durationSeconds: r.duration_seconds as number,
    preDistress: (r.pre_distress as number) ?? null,
    postDistress: (r.post_distress as number) ?? null,
    timestamp: r.timestamp as string,
  };
}

// --- tasks -----------------------------------------------------------------

export function listTasks(includeCompleted: boolean): Task[] {
  const db = getDb();
  const sql = includeCompleted
    ? `SELECT * FROM tasks ORDER BY completed ASC,
        CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
        due_date IS NULL, due_date ASC`
    : `SELECT * FROM tasks WHERE completed = 0 ORDER BY
        CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
        due_date IS NULL, due_date ASC`;
  return db.prepare(sql).all().map((r) => mapTask(r as Row));
}

function getTask(db: Database.Database, id: number): Task {
  const row = db.prepare('SELECT * FROM tasks WHERE id = ?').get(id) as Row | undefined;
  if (!row) throw new Error(`Task ${id} not found`);
  return mapTask(row);
}

export function createTask(input: TaskInput): Task {
  const db = getDb();
  const energy = input.energyRequired ?? 5;
  const spoonCost = input.spoonCost ?? estimateSpoonCost(energy, input.estimatedDuration ?? null);
  const info = db
    .prepare(
      `INSERT INTO tasks (title, description, priority, category, energy_required, due_date, estimated_duration, spoon_cost)
       VALUES (@title, @description, @priority, @category, @energy_required, @due_date, @estimated_duration, @spoon_cost)`,
    )
    .run({
      title: input.title,
      description: input.description ?? null,
      priority: input.priority ?? 'medium',
      category: input.category ?? 'Life',
      energy_required: energy,
      due_date: input.dueDate ?? null,
      estimated_duration: input.estimatedDuration ?? null,
      spoon_cost: spoonCost,
    });
  return getTask(db, info.lastInsertRowid as number);
}

export function updateTask(id: number, patch: Partial<TaskInput>): Task {
  const db = getDb();
  const cur = getTask(db, id);
  const merged = {
    title: patch.title ?? cur.title,
    description: patch.description ?? cur.description,
    priority: patch.priority ?? cur.priority,
    category: patch.category ?? cur.category,
    energy_required: patch.energyRequired ?? cur.energyRequired,
    due_date: patch.dueDate ?? cur.dueDate,
    estimated_duration: patch.estimatedDuration ?? cur.estimatedDuration,
    spoon_cost: patch.spoonCost ?? cur.spoonCost,
    id,
  };
  db.prepare(
    `UPDATE tasks SET title=@title, description=@description, priority=@priority,
       category=@category, energy_required=@energy_required, due_date=@due_date,
       estimated_duration=@estimated_duration, spoon_cost=@spoon_cost,
       updated_at=datetime('now') WHERE id=@id`,
  ).run(merged);
  return getTask(db, id);
}

export function toggleTask(id: number): Task {
  const db = getDb();
  const cur = getTask(db, id);
  const completed = cur.completed ? 0 : 1;
  db.prepare(
    `UPDATE tasks SET completed=?, completed_at=?, updated_at=datetime('now') WHERE id=?`,
  ).run(completed, completed ? new Date().toISOString() : null, id);
  return getTask(db, id);
}

export function deleteTask(id: number): void {
  getDb().prepare('DELETE FROM tasks WHERE id = ?').run(id);
}

// --- mood / sleep ----------------------------------------------------------

export function listMoods(limit: number): MoodEntry[] {
  return getDb()
    .prepare('SELECT * FROM mood_entries ORDER BY timestamp DESC LIMIT ?')
    .all(limit)
    .map((r) => mapMood(r as Row));
}

export function createMood(input: MoodInput): MoodEntry {
  const db = getDb();
  const info = db
    .prepare(
      `INSERT INTO mood_entries (mood_score, energy_level, anxiety_level, emotions, notes)
       VALUES (@mood_score, @energy_level, @anxiety_level, @emotions, @notes)`,
    )
    .run({
      mood_score: input.moodScore,
      energy_level: input.energyLevel ?? null,
      anxiety_level: input.anxietyLevel ?? null,
      emotions: input.emotions ?? null,
      notes: input.notes ?? null,
    });
  return mapMood(db.prepare('SELECT * FROM mood_entries WHERE id = ?').get(info.lastInsertRowid) as Row);
}

export function listSleep(limit: number): SleepLog[] {
  return getDb()
    .prepare('SELECT * FROM sleep_logs ORDER BY date DESC LIMIT ?')
    .all(limit)
    .map((r) => mapSleep(r as Row));
}

function computeDuration(bedtime: string, wakeTime: string): number {
  // Times are HH:MM. Wake before bed means it crossed midnight.
  const [bh, bm] = bedtime.split(':').map(Number);
  const [wh, wm] = wakeTime.split(':').map(Number);
  let mins = wh * 60 + wm - (bh * 60 + bm);
  if (mins <= 0) mins += 24 * 60;
  return Math.round((mins / 60) * 10) / 10;
}

export function createSleep(input: SleepInput): SleepLog {
  const db = getDb();
  const duration = computeDuration(input.bedtime, input.wakeTime);
  const info = db
    .prepare(
      `INSERT INTO sleep_logs (date, bedtime, wake_time, quality, duration_hours, notes)
       VALUES (@date, @bedtime, @wake_time, @quality, @duration_hours, @notes)`,
    )
    .run({
      date: input.date,
      bedtime: input.bedtime,
      wake_time: input.wakeTime,
      quality: input.quality,
      duration_hours: duration,
      notes: input.notes ?? null,
    });
  return mapSleep(db.prepare('SELECT * FROM sleep_logs WHERE id = ?').get(info.lastInsertRowid) as Row);
}

// --- journal ---------------------------------------------------------------

export function listJournal(limit: number): JournalEntry[] {
  return getDb()
    .prepare('SELECT * FROM journal_entries ORDER BY timestamp DESC LIMIT ?')
    .all(limit)
    .map((r) => mapJournal(r as Row));
}

export function createJournal(input: JournalInput): JournalEntry {
  const db = getDb();
  const info = db
    .prepare(
      `INSERT INTO journal_entries (title, content, mood_score, prompt)
       VALUES (@title, @content, @mood_score, @prompt)`,
    )
    .run({
      title: input.title ?? null,
      content: input.content,
      mood_score: input.moodScore ?? null,
      prompt: input.prompt ?? null,
    });
  return mapJournal(db.prepare('SELECT * FROM journal_entries WHERE id = ?').get(info.lastInsertRowid) as Row);
}

export function deleteJournal(id: number): void {
  getDb().prepare('DELETE FROM journal_entries WHERE id = ?').run(id);
}

// --- practices -------------------------------------------------------------

export function listPractices(limit: number): PracticeSession[] {
  return getDb()
    .prepare('SELECT * FROM practice_sessions ORDER BY timestamp DESC LIMIT ?')
    .all(limit)
    .map((r) => mapPractice(r as Row));
}

export function logPractice(input: PracticeInput): PracticeSession {
  const db = getDb();
  const info = db
    .prepare(
      `INSERT INTO practice_sessions (kind, technique, duration_seconds, pre_distress, post_distress)
       VALUES (@kind, @technique, @duration_seconds, @pre_distress, @post_distress)`,
    )
    .run({
      kind: input.kind,
      technique: input.technique,
      duration_seconds: input.durationSeconds,
      pre_distress: input.preDistress ?? null,
      post_distress: input.postDistress ?? null,
    });
  return mapPractice(db.prepare('SELECT * FROM practice_sessions WHERE id = ?').get(info.lastInsertRowid) as Row);
}

// --- settings + crisis plan (stored as JSON in settings table) -------------

function readSetting<T>(key: string, fallback: T): T {
  const row = getDb().prepare('SELECT value FROM settings WHERE key = ?').get(key) as Row | undefined;
  if (!row) return fallback;
  try {
    return JSON.parse(row.value as string) as T;
  } catch {
    return fallback;
  }
}

function writeSetting(key: string, value: unknown): void {
  getDb()
    .prepare('INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value')
    .run(key, JSON.stringify(value));
}

export function getSettings(): Settings {
  return { ...DEFAULT_SETTINGS, ...readSetting<Partial<Settings>>('app', {}) };
}

export function saveSettings(patch: Partial<Settings>): Settings {
  const next = { ...getSettings(), ...patch };
  writeSetting('app', next);
  return next;
}

const EMPTY_PLAN: CrisisPlan = {
  warningSigns: [],
  copingStrategies: [],
  contacts: [],
  safeNote: '',
};

export function getCrisisPlan(): CrisisPlan {
  return readSetting<CrisisPlan>('crisis_plan', EMPTY_PLAN);
}

export function saveCrisisPlan(plan: CrisisPlan): CrisisPlan {
  writeSetting('crisis_plan', plan);
  return plan;
}

export function userConditions(): Condition[] {
  return getSettings().conditions;
}
