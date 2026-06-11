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
} from './types';

// The full surface the renderer can call. Each method maps 1:1 to an IPC
// channel of the same name. Defining it once keeps preload + main honest.
export interface HearthApi {
  // tasks
  listTasks(includeCompleted: boolean): Promise<Task[]>;
  createTask(input: TaskInput): Promise<Task>;
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

  // settings
  getSettings(): Promise<Settings>;
  saveSettings(patch: Partial<Settings>): Promise<Settings>;

  // misc
  heroDataUrl(): Promise<string | null>;
}

export const IPC_CHANNELS: (keyof HearthApi)[] = [
  'listTasks',
  'createTask',
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
  'getSettings',
  'saveSettings',
  'heroDataUrl',
];
