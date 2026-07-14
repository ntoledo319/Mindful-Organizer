import type Database from 'better-sqlite3';
import { getDb } from './db';
import { estimateSpoonCost, normalizeDailySpoons } from '../src/shared/spoons';
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
  presence: true,
  quietMode: 'auto',
  quietDim: 0.4,
  focusGuard: true,
  nudges: true,
  privacyConsentAt: null,
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

function insertTask(db: Database.Database, input: TaskInput): Task {
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

export function createTask(input: TaskInput): Task {
  return insertTask(getDb(), input);
}

export function replaceTaskWithSubtasks(id: number, subtasks: TaskInput[]): Task[] {
  if (!subtasks.length) throw new Error('At least one subtask is required');
  const db = getDb();
  const replace = db.transaction(() => {
    getTask(db, id); // fail before writing if the source task no longer exists
    const created = subtasks.map((subtask) => insertTask(db, subtask));
    db.prepare('DELETE FROM tasks WHERE id = ?').run(id);
    return created;
  });
  return replace();
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
  
  // Gamification: Award XP when completed
  if (completed) {
    const xpGain = Math.round((cur.spoonCost || 1) * 10);
    const g = getGamification();
    const newXp = g.currentXp + xpGain;
    let newLevel = g.currentLevel;
    let remainingXp = newXp;
    
    // Level up logic (e.g. 100 XP per level)
    const xpNeeded = newLevel * 100;
    if (remainingXp >= xpNeeded) {
      newLevel += 1;
      remainingXp -= xpNeeded;
    }
    
    db.prepare(`UPDATE gamification SET current_level=?, current_xp=?, total_xp=total_xp+? WHERE id=?`).run(
      newLevel, remainingXp, xpGain, g.id
    );
  } else {
    // Reverse XP if unchecking
    const xpLoss = Math.round((cur.spoonCost || 1) * 10);
    const g = getGamification();
    let newXp = g.currentXp - xpLoss;
    let newLevel = g.currentLevel;
    if (newXp < 0 && newLevel > 1) {
      newLevel -= 1;
      newXp = (newLevel * 100) + newXp; // Add negative XP to previous level's cap
    }
    newXp = Math.max(0, newXp); // Floor at 0 for level 1
    
    db.prepare(`UPDATE gamification SET current_level=?, current_xp=?, total_xp=MAX(0, total_xp-?) WHERE id=?`).run(
      newLevel, newXp, xpLoss, g.id
    );
  }
  
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

function normalizeConsentTimestamp(value: unknown): string | null {
  if (typeof value !== 'string' || value.trim().length < 20) return null;
  return Number.isNaN(Date.parse(value)) ? null : value;
}

export function getSettings(): Settings {
  const stored = readSetting<Partial<Settings>>('app', {});
  return {
    ...DEFAULT_SETTINGS,
    ...stored,
    dailySpoons: normalizeDailySpoons(stored.dailySpoons ?? DEFAULT_SETTINGS.dailySpoons),
    privacyConsentAt: normalizeConsentTimestamp(stored.privacyConsentAt),
  };
}

export function saveSettings(patch: Partial<Settings>): Settings {
  const next = { ...getSettings(), ...patch };
  next.dailySpoons = normalizeDailySpoons(next.dailySpoons);
  next.privacyConsentAt = normalizeConsentTimestamp(next.privacyConsentAt);
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

// --- Structured reflection and local system features -----------------------

import type {
  ErpSession,
  ErpInput,
  DiaryCard,
  DiaryCardInput,
  Medication,
  MedicationInput,
  Gamification
} from '../src/shared/types';

function mapErpSession(r: Row): ErpSession {
  return {
    id: r.id as number,
    targetObsession: r.target_obsession as string,
    exposureActivity: r.exposure_activity as string,
    preAnxiety: r.pre_anxiety as number,
    postAnxiety: r.post_anxiety as number,
    durationMinutes: r.duration_minutes as number,
    notes: (r.notes as string) ?? null,
    timestamp: r.timestamp as string,
  };
}

export function listErpSessions(limit: number): ErpSession[] {
  return getDb()
    .prepare('SELECT * FROM erp_sessions ORDER BY timestamp DESC LIMIT ?')
    .all(limit)
    .map((r) => mapErpSession(r as Row));
}

export function createErpSession(input: ErpInput): ErpSession {
  const db = getDb();
  const info = db
    .prepare(
      `INSERT INTO erp_sessions (target_obsession, exposure_activity, pre_anxiety, post_anxiety, duration_minutes, notes)
       VALUES (@target, @activity, @pre, @post, @duration, @notes)`
    )
    .run({
      target: input.targetObsession,
      activity: input.exposureActivity,
      pre: input.preAnxiety,
      post: input.postAnxiety,
      duration: input.durationMinutes,
      notes: input.notes ?? null,
    });
  return mapErpSession(db.prepare('SELECT * FROM erp_sessions WHERE id = ?').get(info.lastInsertRowid) as Row);
}

function mapDiaryCard(r: Row): DiaryCard {
  return {
    id: r.id as number,
    date: r.date as string,
    urgesSelfHarm: (r.urges_self_harm as number) ?? null,
    urgesQuitTherapy: (r.urges_quit_therapy as number) ?? null,
    emotionsSadness: (r.emotions_sadness as number) ?? null,
    emotionsFear: (r.emotions_fear as number) ?? null,
    skillsUsed: (r.skills_used as string) ?? null,
    notes: (r.notes as string) ?? null,
    timestamp: r.timestamp as string,
  };
}

export function listDiaryCards(limit: number): DiaryCard[] {
  return getDb()
    .prepare('SELECT * FROM diary_cards ORDER BY date DESC LIMIT ?')
    .all(limit)
    .map((r) => mapDiaryCard(r as Row));
}

export function createDiaryCard(input: DiaryCardInput): DiaryCard {
  const db = getDb();
  const info = db
    .prepare(
      `INSERT INTO diary_cards (date, urges_self_harm, urges_quit_therapy, emotions_sadness, emotions_fear, skills_used, notes)
       VALUES (@date, @harm, @quit, @sad, @fear, @skills, @notes)`
    )
    .run({
      date: input.date,
      harm: input.urgesSelfHarm ?? null,
      quit: input.urgesQuitTherapy ?? null,
      sad: input.emotionsSadness ?? null,
      fear: input.emotionsFear ?? null,
      skills: input.skillsUsed ?? null,
      notes: input.notes ?? null,
    });
  return mapDiaryCard(db.prepare('SELECT * FROM diary_cards WHERE id = ?').get(info.lastInsertRowid) as Row);
}

function mapMedication(r: Row): Medication {
  return {
    id: r.id as number,
    name: r.name as string,
    dosage: r.dosage as string,
    frequency: r.frequency as string,
    reminderTime: (r.reminder_time as string) ?? null,
    active: !!r.active,
  };
}

export function listMedications(): Medication[] {
  return getDb()
    .prepare('SELECT * FROM medications ORDER BY name ASC')
    .all()
    .map((r) => mapMedication(r as Row));
}

export function createMedication(input: MedicationInput): Medication {
  const db = getDb();
  const info = db
    .prepare(
      `INSERT INTO medications (name, dosage, frequency, reminder_time, active)
       VALUES (@name, @dosage, @frequency, @reminder_time, @active)`
    )
    .run({
      name: input.name,
      dosage: input.dosage,
      frequency: input.frequency,
      reminder_time: input.reminderTime ?? null,
      active: input.active === false ? 0 : 1,
    });
  return mapMedication(db.prepare('SELECT * FROM medications WHERE id = ?').get(info.lastInsertRowid) as Row);
}

export function updateMedication(id: number, patch: Partial<MedicationInput>): Medication {
  const db = getDb();
  const cur = mapMedication(db.prepare('SELECT * FROM medications WHERE id = ?').get(id) as Row);
  const merged = {
    name: patch.name ?? cur.name,
    dosage: patch.dosage ?? cur.dosage,
    frequency: patch.frequency ?? cur.frequency,
    reminder_time: patch.reminderTime !== undefined ? patch.reminderTime : cur.reminderTime,
    active: (patch.active !== undefined ? patch.active : cur.active) ? 1 : 0,
    id,
  };
  db.prepare(
    `UPDATE medications SET name=@name, dosage=@dosage, frequency=@frequency,
       reminder_time=@reminder_time, active=@active WHERE id=@id`
  ).run(merged);
  return mapMedication(db.prepare('SELECT * FROM medications WHERE id = ?').get(id) as Row);
}

export function deleteMedication(id: number): void {
  getDb().prepare('DELETE FROM medications WHERE id = ?').run(id);
}

function mapGamification(r: Row): Gamification {
  return {
    id: r.id as number,
    currentLevel: r.current_level as number,
    currentXp: r.current_xp as number,
    totalXp: r.total_xp as number,
  };
}

export function getGamification(): Gamification {
  const db = getDb();
  let row = db.prepare('SELECT * FROM gamification LIMIT 1').get() as Row | undefined;
  if (!row) {
    db.prepare('INSERT INTO gamification (current_level, current_xp, total_xp) VALUES (1, 0, 0)').run();
    row = db.prepare('SELECT * FROM gamification LIMIT 1').get() as Row;
  }
  return mapGamification(row);
}
