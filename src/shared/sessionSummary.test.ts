import { describe, expect, it } from 'vitest';
import { buildSessionSummaryHtml, hasSummaryData, normalizeSummaryDays } from './sessionSummary';
import type { Trends } from './types';

const trends: Trends = {
  mood: [
    { date: '2026-07-12', value: 4 },
    { date: '2026-07-13', value: 8 },
  ],
  energy: [{ date: '2026-07-13', value: 6 }],
  sleep: [{ date: '2026-07-12', value: 7.5 }],
};

describe('session summary', () => {
  it('normalizes unsupported windows to 14 days', () => {
    expect(normalizeSummaryDays(7)).toBe(7);
    expect(normalizeSummaryDays(30)).toBe(30);
    expect(normalizeSummaryDays(365)).toBe(14);
  });

  it('detects whether there is anything to export', () => {
    expect(hasSummaryData(trends)).toBe(true);
    expect(hasSummaryData({ mood: [], energy: [], sleep: [] })).toBe(false);
  });

  it('renders escaped user data, observed averages, and a safety disclaimer', () => {
    const html = buildSessionSummaryHtml({
      days: 30,
      displayName: '<Alex & Sam>',
      generatedAt: new Date('2026-07-14T12:00:00Z'),
      trends,
    });

    expect(html).toContain('&lt;Alex &amp; Sam&gt;');
    expect(html).toContain('<strong>6.0</strong>');
    expect(html).toContain('not a clinical record');
    expect(html).toContain('2026-07-13');
    expect(html).not.toContain('<Alex & Sam>');
  });
});
