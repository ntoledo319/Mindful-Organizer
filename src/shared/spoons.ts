// Spoon Theory — a way to budget finite daily energy. Ported from the
// original profiles/spoon_theory.py defaults. A "spoon" is one unit of the
// limited energy a person living with chronic illness or mental-health
// conditions has to spend across a day.

import type { Condition } from './types';

export const DEFAULT_DAILY_SPOONS = 12;

// Conditions shift the baseline budget. Depression and PTSD tend to compress
// available energy; this is a gentle default the user can override.
const CONDITION_SPOON_DELTA: Record<Condition, number> = {
  adhd: 0,
  anxiety: -1,
  depression: -3,
  ocd: -1,
  ptsd: -2,
  bipolar: 0,
};

export function dailySpoonsFor(conditions: Condition[]): number {
  const delta = conditions.reduce((sum, c) => sum + (CONDITION_SPOON_DELTA[c] ?? 0), 0);
  // Never drop below a floor of 6 — the budget should still feel livable.
  return Math.max(6, DEFAULT_DAILY_SPOONS + delta);
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
