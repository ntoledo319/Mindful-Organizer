import type { Trends, TrendPoint } from './types';

export interface SessionSummaryInput {
  days: number;
  displayName: string;
  generatedAt: Date;
  trends: Trends;
}

export function normalizeSummaryDays(days: number): 7 | 14 | 30 {
  return days === 7 || days === 30 ? days : 14;
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function values(points: TrendPoint[]): number[] {
  return points.flatMap((point) => (point.value == null ? [] : [point.value]));
}

function average(points: TrendPoint[]): string {
  const present = values(points);
  if (!present.length) return 'No entries';
  return (present.reduce((sum, value) => sum + value, 0) / present.length).toFixed(1);
}

function latest(points: TrendPoint[]): string {
  const present = values(points);
  return present.length ? present[present.length - 1].toFixed(1) : '—';
}

function valueFor(points: TrendPoint[], date: string): string {
  const value = points.find((point) => point.date === date)?.value;
  return value == null ? '—' : value.toFixed(1);
}

export function hasSummaryData(trends: Trends): boolean {
  return Boolean(trends.mood.length || trends.energy.length || trends.sleep.length);
}

export function buildSessionSummaryHtml(input: SessionSummaryInput): string {
  const days = normalizeSummaryDays(input.days);
  const name = input.displayName.trim();
  const generated = input.generatedAt.toLocaleString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  });
  const dates = Array.from(
    new Set([
      ...input.trends.mood.map((point) => point.date),
      ...input.trends.energy.map((point) => point.date),
      ...input.trends.sleep.map((point) => point.date),
    ]),
  ).sort();

  const rows = dates
    .map(
      (date) => `<tr>
        <td>${escapeHtml(date)}</td>
        <td>${valueFor(input.trends.mood, date)}</td>
        <td>${valueFor(input.trends.energy, date)}</td>
        <td>${valueFor(input.trends.sleep, date)}</td>
      </tr>`,
    )
    .join('');

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Hearth session summary</title>
  <style>
    @page { size: A4; margin: 17mm; }
    * { box-sizing: border-box; }
    body { margin: 0; color: #26302a; background: #fffdf8; font: 13px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    header { padding: 0 0 18px; border-bottom: 2px solid #9fb38c; }
    .eyebrow { margin: 0 0 6px; color: #6b796f; font-size: 10px; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }
    h1 { margin: 0; font: 600 30px/1.15 Georgia, serif; color: #28332d; }
    .meta { margin: 8px 0 0; color: #66716a; }
    .notice { margin: 18px 0; padding: 12px 14px; border: 1px solid #d7cdb9; border-radius: 10px; background: #f6f0e5; }
    .metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 18px 0 22px; }
    .metric { min-height: 96px; padding: 14px; border: 1px solid #dce3d9; border-radius: 12px; background: #f7faf5; }
    .metric strong { display: block; margin-top: 3px; font: 600 24px/1.2 Georgia, serif; }
    .metric small { color: #6b796f; }
    h2 { margin: 24px 0 10px; font: 600 18px/1.2 Georgia, serif; }
    table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
    th, td { padding: 8px 9px; border-bottom: 1px solid #e3e7e1; text-align: right; }
    th:first-child, td:first-child { text-align: left; }
    th { color: #59675e; background: #f1f5ef; font-size: 10px; letter-spacing: .06em; text-transform: uppercase; }
    .questions { margin: 8px 0 0; padding-left: 20px; }
    .questions li { margin: 7px 0; }
    footer { margin-top: 24px; padding-top: 12px; border-top: 1px solid #dce3d9; color: #66716a; font-size: 10px; }
  </style>
</head>
<body>
  <header>
    <p class="eyebrow">Hearth · ${days}-day reflection</p>
    <h1>Session summary</h1>
    <p class="meta">${name ? `Prepared by ${escapeHtml(name)} · ` : ''}Generated locally on ${escapeHtml(generated)}</p>
  </header>

  <div class="notice">
    <strong>A personal reflection, not a clinical record.</strong><br>
    This summary contains user-entered observations. It is not a diagnosis, medical assessment, or substitute for professional care. Missing days remain blank.
  </div>

  <section class="metrics">
    <div class="metric"><small>Average mood</small><strong>${average(input.trends.mood)}</strong><small>Latest ${latest(input.trends.mood)} · 1–10 scale</small></div>
    <div class="metric"><small>Average energy</small><strong>${average(input.trends.energy)}</strong><small>Latest ${latest(input.trends.energy)} · 1–10 scale</small></div>
    <div class="metric"><small>Average sleep</small><strong>${average(input.trends.sleep)}</strong><small>Latest ${latest(input.trends.sleep)} · hours</small></div>
  </section>

  <h2>Daily observations</h2>
  <table>
    <thead><tr><th>Date</th><th>Mood /10</th><th>Energy /10</th><th>Sleep hours</th></tr></thead>
    <tbody>${rows}</tbody>
  </table>

  <h2>Questions to carry into a conversation</h2>
  <ul class="questions">
    <li>What felt different on the steadier days?</li>
    <li>Did sleep and energy move together, or separately?</li>
    <li>Which support or routine is worth trying next?</li>
  </ul>

  <footer>
    Generated entirely on this device. Hearth does not upload this report or the data behind it. Sharing the saved PDF is always the user's choice.
  </footer>
</body>
</html>`;
}
