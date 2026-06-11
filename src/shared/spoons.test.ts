import { describe, it, expect } from 'vitest';
import { dailySpoonsFor, estimateSpoonCost, spoonWarning, DEFAULT_DAILY_SPOONS } from './spoons';

describe('dailySpoonsFor', () => {
  it('returns the default with no conditions', () => {
    expect(dailySpoonsFor([])).toBe(DEFAULT_DAILY_SPOONS);
  });

  it('reduces the budget for depression', () => {
    expect(dailySpoonsFor(['depression'])).toBe(DEFAULT_DAILY_SPOONS - 3);
  });

  it('never drops below the livable floor of 6', () => {
    expect(dailySpoonsFor(['depression', 'ptsd', 'anxiety', 'ocd'])).toBe(6);
  });
});

describe('estimateSpoonCost', () => {
  it('scales with energy and duration and rounds to the nearest half', () => {
    const cost = estimateSpoonCost(5, 45);
    expect(cost % 0.5).toBe(0);
    expect(cost).toBeGreaterThan(0);
  });

  it('costs more for higher-energy, longer tasks', () => {
    expect(estimateSpoonCost(9, 120)).toBeGreaterThan(estimateSpoonCost(2, 15));
  });
});

describe('spoonWarning', () => {
  it('reports empty when nothing remains', () => {
    expect(spoonWarning(0, 12)).toBe('empty');
  });
  it('reports low at or below 20% remaining', () => {
    expect(spoonWarning(2, 12)).toBe('low');
  });
  it('reports plenty when over half remains', () => {
    expect(spoonWarning(10, 12)).toBe('plenty');
  });
});
