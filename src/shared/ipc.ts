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
  WellnessSnapshot,
  DailyBriefing,
  Settings,
  Trends,
  PresenceState,
  ErpSession,
  ErpInput,
  DiaryCard,
  DiaryCardInput,
  Medication,
  MedicationInput,
  Gamification,
  SessionSummaryExportResult,
  PersonalDataExportResult,
  AppInfo,
} from './types';

// The full surface the renderer can call. Each method maps 1:1 to an IPC
// channel of the same name. Defining it once keeps preload + main honest.
export interface AmpleApi {
  // tasks
  listTasks(includeCompleted: boolean): Promise<Task[]>;
  createTask(input: TaskInput): Promise<Task>;
  replaceTaskWithSubtasks(id: number, subtasks: TaskInput[]): Promise<Task[]>;
  updateTask(id: number, patch: Partial<TaskInput>): Promise<Task>;
  toggleTask(id: number): Promise<Task>;
  deleteTask(id: number): Promise<void>;

  // mood / sleep
  listMoods(limit: number): Promise<MoodEntry[]>;
  createMood(input: MoodInput): Promise<MoodEntry>;
  listSleep(limit: number): Promise<SleepLog[]>;
  createSleep(input: SleepInput): Promise<SleepLog>;

  // journal
  listJournal(limit: number): Promise<JournalEntry[]>;
  createJournal(input: JournalInput): Promise<JournalEntry>;
  deleteJournal(id: number): Promise<void>;

  // practices
  listPractices(limit: number): Promise<PracticeSession[]>;
  logPractice(input: PracticeInput): Promise<PracticeSession>;

  // crisis plan
  getCrisisPlan(): Promise<CrisisPlan>;
  saveCrisisPlan(plan: CrisisPlan): Promise<CrisisPlan>;

  // intelligence
  getSnapshot(): Promise<WellnessSnapshot>;
  getBriefing(): Promise<DailyBriefing>;
  getTrends(days: number): Promise<Trends>;
  exportSessionSummary(days: number): Promise<SessionSummaryExportResult>;

  // settings
  getSettings(): Promise<Settings>;
  saveSettings(patch: Partial<Settings>): Promise<Settings>;
  exportAllData(): Promise<PersonalDataExportResult>;
  deleteAllData(): Promise<void>;

  // presence — the acting layer that reaches past Ample's own window
  getPresence(): Promise<PresenceState>;
  setQuietActive(active: boolean): Promise<PresenceState>;
  startFocus(input: { seconds: number; intention?: string | null }): Promise<PresenceState>;
  endFocus(): Promise<PresenceState>;

  // restored features
  listErpSessions(limit: number): Promise<ErpSession[]>;
  createErpSession(input: ErpInput): Promise<ErpSession>;
  
  listDiaryCards(limit: number): Promise<DiaryCard[]>;
  createDiaryCard(input: DiaryCardInput): Promise<DiaryCard>;
  
  listMedications(): Promise<Medication[]>;
  createMedication(input: MedicationInput): Promise<Medication>;
  updateMedication(id: number, patch: Partial<MedicationInput>): Promise<Medication>;
  deleteMedication(id: number): Promise<void>;
  
  getGamification(): Promise<Gamification>;

  // misc
  heroDataUrl(): Promise<string | null>;
  getAppInfo(): Promise<AppInfo>;
}

export const IPC_CHANNELS: (keyof AmpleApi)[] = [
  'listTasks',
  'createTask',
  'replaceTaskWithSubtasks',
  'updateTask',
  'toggleTask',
  'deleteTask',
  'listMoods',
  'createMood',
  'listSleep',
  'createSleep',
  'listJournal',
  'createJournal',
  'deleteJournal',
  'listPractices',
  'logPractice',
  'getCrisisPlan',
  'saveCrisisPlan',
  'getSnapshot',
  'getBriefing',
  'getTrends',
  'exportSessionSummary',
  'getSettings',
  'saveSettings',
  'exportAllData',
  'deleteAllData',
  'getPresence',
  'setQuietActive',
  'startFocus',
  'endFocus',
  'listErpSessions',
  'createErpSession',
  'listDiaryCards',
  'createDiaryCard',
  'listMedications',
  'createMedication',
  'updateMedication',
  'deleteMedication',
  'getGamification',
  'heroDataUrl',
  'getAppInfo',
];
