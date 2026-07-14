const TABLE_SCHEMA = `
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

CREATE TABLE IF NOT EXISTS erp_sessions (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  target_obsession   TEXT    NOT NULL,
  exposure_activity  TEXT    NOT NULL,
  pre_anxiety        INTEGER NOT NULL CHECK (pre_anxiety BETWEEN 0 AND 10),
  post_anxiety       INTEGER NOT NULL CHECK (post_anxiety BETWEEN 0 AND 10),
  duration_minutes   INTEGER NOT NULL,
  notes              TEXT,
  timestamp          TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS diary_cards (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  date               TEXT    NOT NULL,
  urges_self_harm    INTEGER CHECK (urges_self_harm BETWEEN 0 AND 5),
  urges_quit_therapy INTEGER CHECK (urges_quit_therapy BETWEEN 0 AND 5),
  emotions_sadness   INTEGER CHECK (emotions_sadness BETWEEN 0 AND 5),
  emotions_fear      INTEGER CHECK (emotions_fear BETWEEN 0 AND 5),
  skills_used        TEXT,
  notes              TEXT,
  timestamp          TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS medications (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  name               TEXT    NOT NULL,
  dosage             TEXT    NOT NULL,
  frequency          TEXT    NOT NULL,
  reminder_time      TEXT,
  active             INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS medication_logs (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  medication_id      INTEGER NOT NULL,
  taken_at           TEXT    NOT NULL DEFAULT (datetime('now')),
  status             TEXT    NOT NULL DEFAULT 'taken',
  FOREIGN KEY(medication_id) REFERENCES medications(id)
);

CREATE TABLE IF NOT EXISTS gamification (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  current_level      INTEGER NOT NULL DEFAULT 1,
  current_xp         INTEGER NOT NULL DEFAULT 0,
  total_xp           INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS clinical_profiles (
  id                 INTEGER PRIMARY KEY AUTOINCREMENT,
  profile_type       TEXT    NOT NULL,
  active             INTEGER NOT NULL DEFAULT 1,
  settings_json      TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_mood_ts ON mood_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_sleep_date ON sleep_logs(date);
CREATE INDEX IF NOT EXISTS idx_journal_ts ON journal_entries(timestamp);
CREATE INDEX IF NOT EXISTS idx_practice_ts ON practice_sessions(timestamp);
CREATE INDEX IF NOT EXISTS idx_erp_ts ON erp_sessions(timestamp);
CREATE INDEX IF NOT EXISTS idx_diary_date ON diary_cards(date);
`;

const HAS_VALID_CONSENT = `EXISTS (
  SELECT 1 FROM settings
  WHERE key = 'app'
    AND json_type(value, '$.privacyConsentAt') = 'text'
    AND length(trim(json_extract(value, '$.privacyConsentAt'))) >= 20
    AND julianday(json_extract(value, '$.privacyConsentAt')) IS NOT NULL
)`;

const NEW_HAS_VALID_CONSENT = `(
  COALESCE(json_type(NEW.value, '$.privacyConsentAt'), '') = 'text'
  AND length(trim(COALESCE(json_extract(NEW.value, '$.privacyConsentAt'), ''))) >= 20
  AND julianday(json_extract(NEW.value, '$.privacyConsentAt')) IS NOT NULL
)`;

const SENSITIVE_TABLES = [
  'tasks',
  'mood_entries',
  'sleep_logs',
  'journal_entries',
  'practice_sessions',
  'erp_sessions',
  'diary_cards',
  'medications',
  'medication_logs',
  'gamification',
  'clinical_profiles',
];

const CONSENT_TRIGGER_NAMES = [
  'settings_app_requires_consent_insert',
  'settings_app_requires_consent_update',
  'settings_app_requires_consent_delete',
  'settings_other_requires_consent_insert',
  'settings_other_requires_consent_update',
  ...SENSITIVE_TABLES.flatMap((table) => [
    `${table}_requires_consent_insert`,
    `${table}_requires_consent_update`,
  ]),
];

const DROP_CONSENT_TRIGGERS = CONSENT_TRIGGER_NAMES.map(
  (name) => `DROP TRIGGER IF EXISTS ${name};`,
).join('\n');

const CONSENT_TRIGGERS = `
${DROP_CONSENT_TRIGGERS}

CREATE TRIGGER IF NOT EXISTS settings_app_requires_consent_insert
BEFORE INSERT ON settings
WHEN NEW.key = 'app' AND NOT ${NEW_HAS_VALID_CONSENT}
BEGIN
  SELECT RAISE(ABORT, 'Explicit privacy consent is required before storing personal settings.');
END;

CREATE TRIGGER IF NOT EXISTS settings_app_requires_consent_update
BEFORE UPDATE OF value ON settings
WHEN NEW.key = 'app' AND NOT ${NEW_HAS_VALID_CONSENT}
BEGIN
  SELECT RAISE(ABORT, 'Use Erase all data to withdraw privacy consent.');
END;

CREATE TRIGGER IF NOT EXISTS settings_app_requires_consent_delete
BEFORE DELETE ON settings
WHEN OLD.key = 'app'
BEGIN
  SELECT RAISE(ABORT, 'Use Erase all data to withdraw privacy consent.');
END;

CREATE TRIGGER IF NOT EXISTS settings_other_requires_consent_insert
BEFORE INSERT ON settings
WHEN NEW.key <> 'app' AND NOT ${HAS_VALID_CONSENT}
BEGIN
  SELECT RAISE(ABORT, 'Explicit privacy consent is required before storing personal data.');
END;

CREATE TRIGGER IF NOT EXISTS settings_other_requires_consent_update
BEFORE UPDATE OF value ON settings
WHEN NEW.key <> 'app' AND NOT ${HAS_VALID_CONSENT}
BEGIN
  SELECT RAISE(ABORT, 'Explicit privacy consent is required before storing personal data.');
END;

${SENSITIVE_TABLES.map(
  (table) => `
CREATE TRIGGER IF NOT EXISTS ${table}_requires_consent_insert
BEFORE INSERT ON ${table}
WHEN NOT ${HAS_VALID_CONSENT}
BEGIN
  SELECT RAISE(ABORT, 'Explicit privacy consent is required before storing personal data.');
END;

CREATE TRIGGER IF NOT EXISTS ${table}_requires_consent_update
BEFORE UPDATE ON ${table}
WHEN NOT ${HAS_VALID_CONSENT}
BEGIN
  SELECT RAISE(ABORT, 'Explicit privacy consent is required before storing personal data.');
END;
`,
).join('\n')}
`;

export const SCHEMA = `${TABLE_SCHEMA}\n${CONSENT_TRIGGERS}`;
