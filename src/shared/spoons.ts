// A small, user-controlled way to budget finite daily energy. Paulatim never
// infers someone's capacity from a diagnosis, condition label, or check-in.
// Legacy condition labels remain only as backward-compatible metadata.

import type { Condition } from './types';

export const DEFAULT_DAILY_SPOONS = 12;
export const MIN_DAILY_SPOONS = 4;
export const MAX_DAILY_SPOONS = 24;

export function normalizeDailySpoons(value: number): number {
  if (!Number.isFinite(value)) return DEFAULT_DAILY_SPOONS;
  return Math.min(MAX_DAILY_SPOONS, Math.max(MIN_DAILY_SPOONS, Math.round(value)));
}

// Kept as a compatibility seam for existing onboarding/settings callers. The
// parameter is intentionally ignored so selecting a condition can never lower
// a person's capacity behind their back.
export function dailySpoonsFor(_conditions: Condition[]): number {
  return DEFAULT_DAILY_SPOONS;
}

// Estimate the spoon cost of a task from its energy requirement (1-10) and
// estimated duration. Used as a sensible default when the user doesn't set one.
export function estimateSpoonCost(energyRequired: number, estimatedMinutes: number | null): number {
  const energyPart = energyRequired / 4; // 1-10 -> 0.25-2.5
  const durationPart = estimatedMinutes ? Math.min(estimatedMinutes / 45, 3) : 0.5;
  return Math.round((energyPart + durationPart) * 2) / 2; // round to nearest 0.5
}

export type SpoonWarning = 'plenty' | 'mindful' | 'low' | 'empty';

export function spoonWarning(remaining: number, total: number): SpoonWarning {
  const ratio = total > 0 ? remaining / total : 0;
  if (remaining <= 0) return 'empty';
  if (ratio <= 0.2) return 'low';
  if (ratio <= 0.5) return 'mindful';
  return 'plenty';
}
