// Shared domain contract between the Electron main process (data layer)
// and the renderer (UI). No runtime imports here — types only — so it is
// safe to load from either side.

export type Condition = 'adhd' | 'anxiety' | 'depression' | 'ocd' | 'ptsd' | 'bipolar';

export const CONDITIONS: { id: Condition; label: string; blurb: string }[] = [
  { id: 'adhd', label: 'ADHD', blurb: 'Attention, momentum, and gentle structure' },
  { id: 'anxiety', label: 'Anxiety', blurb: 'Grounding when the noise rises' },
  { id: 'depression', label: 'Depression', blurb: 'Energy-matched, low-friction starts' },
  { id: 'ocd', label: 'OCD', blurb: 'Exposure tracking without judgment' },
  { id: 'ptsd', label: 'PTSD', blurb: 'A predictable, safe baseline' },
  { id: 'bipolar', label: 'Bipolar', blurb: 'Watching the rhythm of sleep and energy' },
];

export type Priority = 'low' | 'medium' | 'high' | 'urgent';

export interface Task {
  id: number;
  title: string;
  description: string | null;
  priority: Priority;
  category: string;
  energyRequired: number; // 1-10
  dueDate: string | null; // ISO date
  completed: boolean;
  completedAt: string | null;
  estimatedDuration: number | null; // minutes
  spoonCost: number;
  createdAt: string;
  updatedAt: string;
}

export interface TaskInput {
  title: string;
  description?: string | null;
  priority?: Priority;
  category?: string;
  energyRequired?: number;
  dueDate?: string | null;
  estimatedDuration?: number | null;
  spoonCost?: number;
}

export interface MoodEntry {
  id: number;
  timestamp: string;
  moodScore: number; // 1-10
  energyLevel: number | null; // 1-10
  anxietyLevel: number | null; // 0-10
  emotions: string | null;
  notes: string | null;
}

export interface MoodInput {
  moodScore: number;
  energyLevel?: number | null;
  anxietyLevel?: number | null;
  emotions?: string | null;
  notes?: string | null;
}

export interface SleepLog {
  id: number;
  date: string;
  bedtime: string;
  wakeTime: string;
  quality: number; // 1-10
  durationHours: number;
  notes: string | null;
}

export interface SleepInput {
  date: string;
  bedtime: string;
  wakeTime: string;
  quality: number;
  notes?: string | null;
}

export interface JournalEntry {
  id: number;
  timestamp: string;
  title: string | null;
  content: string;
  moodScore: number | null;
  prompt: string | null;
}

export interface JournalInput {
  title?: string | null;
  content: string;
  moodScore?: number | null;
  prompt?: string | null;
}

export type SessionKind = 'breathing' | 'grounding' | 'meditation' | 'focus';

export interface PracticeSession {
  id: number;
  kind: SessionKind;
  technique: string;
  durationSeconds: number;
  preDistress: number | null;
  postDistress: number | null;
  timestamp: string;
}

export interface PracticeInput {
  kind: SessionKind;
  technique: string;
  durationSeconds: number;
  preDistress?: number | null;
  postDistress?: number | null;
}

export interface CrisisContact {
  name: string;
  relationship: string;
  phone: string;
}

export interface CrisisPlan {
  warningSigns: string[];
  copingStrategies: string[];
  contacts: CrisisContact[];
  safeNote: string;
}

export type CrisisSeverity = 'info' | 'mild' | 'moderate' | 'urgent';

export interface CrisisSignal {
  severity: CrisisSeverity;
  sources: string[];
  description: string;
  recommendation: string;
}

export interface WellnessSnapshot {
  timestamp: string;
  moodScore: number | null;
  energyScore: number | null;
  sleepHours: number | null;
  sleepQuality: number | null;
  tasksCompletedToday: number;
  tasksPending: number;
  spoonsRemaining: number;
  spoonsTotal: number;
}

export interface DailyBriefing {
  date: string;
  greeting: string;
  energyForecast: string;
  insights: string[];
  suggestedSkill: { kind: SessionKind; technique: string; reason: string } | null;
  recommendedTasks: Task[];
  signals: CrisisSignal[];
}

export type QuietMode = 'off' | 'auto' | 'on';

export interface Settings {
  conditions: Condition[];
  displayName: string;
  onboarded: boolean;
  theme: 'light' | 'dark' | 'system';
  dailySpoons: number;
  // --- presence: how Paulatim shows up beyond its own window ---
  presence: boolean; // live in the tray / menu bar
  quietMode: QuietMode; // dim the screen when you're drained
  quietDim: number; // 0.1–0.8: how deep the dim goes when quiet is active
  focusGuard: boolean; // raise a calm full-screen hold during focus blocks
  nudges: boolean; // gentle notifications (focus finished, an urgent signal)
  privacyConsentAt: string | null; // express local-data consent captured during onboarding
}

// Live state of the acting layer, mirrored from the main process to the UI.
export interface PresenceState {
  quietActive: boolean; // the dimming overlay is up right now
  quietMode: QuietMode;
  focus: { endsAt: string; intention: string | null; seconds: number } | null;
}

export interface PresenceUpdate {
  state: PresenceState;
  settings: Settings;
}

export interface TrendPoint {
  date: string;
  value: number | null;
}

export interface Trends {
  mood: TrendPoint[];
  sleep: TrendPoint[];
  energy: TrendPoint[];
}

export interface SessionSummaryExportResult {
  status: 'saved' | 'cancelled' | 'empty';
  filePath?: string;
}

export interface PersonalDataExportResult {
  status: 'saved' | 'cancelled';
  filePath?: string;
}

// Version/platform info for the renderer's About block and bug reports.
// Carries no personal data.
export interface AppInfo {
  version: string;
  os: string;
  arch: string;
}

// --- Structured reflection and local system features ---

export interface ErpSession {
  id: number;
  targetObsession: string;
  exposureActivity: string;
  preAnxiety: number; // 0-10
  postAnxiety: number; // 0-10
  durationMinutes: number;
  notes: string | null;
  timestamp: string;
}

export interface ErpInput {
  targetObsession: string;
  exposureActivity: string;
  preAnxiety: number;
  postAnxiety: number;
  durationMinutes: number;
  notes?: string | null;
}

export interface DiaryCard {
  id: number;
  date: string;
  urgesSelfHarm: number | null; // 0-5
  urgesQuitTherapy: number | null; // 0-5
  emotionsSadness: number | null; // 0-5
  emotionsFear: number | null; // 0-5
  skillsUsed: string | null;
  notes: string | null;
  timestamp: string;
}

export interface DiaryCardInput {
  date: string;
  urgesSelfHarm?: number | null;
  urgesQuitTherapy?: number | null;
  emotionsSadness?: number | null;
  emotionsFear?: number | null;
  skillsUsed?: string | null;
  notes?: string | null;
}

export interface Medication {
  id: number;
  name: string;
  dosage: string;
  frequency: string;
  reminderTime: string | null;
  active: boolean;
}

export interface MedicationInput {
  name: string;
  dosage: string;
  frequency: string;
  reminderTime?: string | null;
  active?: boolean;
}

export interface Gamification {
  id: number;
  currentLevel: number;
  currentXp: number;
  totalXp: number;
}
