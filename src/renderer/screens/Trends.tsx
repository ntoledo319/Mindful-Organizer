import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import type { TrendPoint } from '@shared/types';
import { EmptyState, Modal, PageHeader, QueryErrorState, Spinner } from '../components/ui';
import { ChartIcon } from '../components/icons';

export function Trends() {
  const [days, setDays] = useState(14);
  const [showExportModal, setShowExportModal] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['trends', days],
    queryFn: () => api.getTrends(days),
  });

  if (isLoading) return <Spinner />;
  if (isError || !data) {
    return <QueryErrorState title="Rhythm didn't load" onRetry={() => void refetch()} />;
  }

  const empty = !data.mood.length && !data.sleep.length && !data.energy.length;

  const saveSummary = async () => {
    setExporting(true);
    setExportMessage(null);
    try {
      const result = await api.exportSessionSummary(days);
      if (result.status === 'saved') {
        setExportMessage('Saved. The PDF stays wherever you chose to put it.');
      } else if (result.status === 'empty') {
        setExportMessage('Add a mood, energy, or sleep entry before making a summary.');
      } else {
        setExportMessage('Nothing was saved.');
      }
    } catch {
      setExportMessage('Paulatim could not save the PDF. Choose another location and try again.');
    } finally {
      setExporting(false);
    }
  };

  const closeExport = () => {
    setShowExportModal(false);
    setExportMessage(null);
  };

  return (
    <div>
      <PageHeader
        title="Rhythm"
        subtitle="Patterns, not performance. The shape of a few weeks tells more than any single day."
        action={
          <div className="flex gap-2" role="group" aria-label="Trend window">
            {[7, 14, 30].map((d) => (
              <button key={d} onClick={() => setDays(d)} className={days === d ? 'btn-primary' : 'btn-ghost'} aria-pressed={days === d}>
                {d}d
              </button>
            ))}
            <button
              onClick={() => setShowExportModal(true)}
              className="btn-primary ml-4"
            >
              Save session summary
            </button>
          </div>
        }
      />

      <Modal open={showExportModal} onClose={closeExport} title="Carry the pattern into a conversation.">
        <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-brand dark:text-night-brand">
          Your data, your choice
        </p>
        <p className="mb-6 text-sm leading-relaxed text-text-muted dark:text-night-muted">
          Paulatim will make a {days}-day PDF from your mood, energy, and sleep observations. It is a personal
          reflection—not a medical record or diagnosis—and it is generated entirely on this device.
        </p>
        <button
          onClick={() => void saveSummary()}
          className="btn-primary w-full justify-center"
          disabled={exporting || empty}
        >
          {exporting ? 'Preparing PDF…' : 'Choose where to save'}
        </button>
        {empty && <p className="mt-3 text-sm text-text-muted dark:text-night-muted">Add a check-in or sleep entry first.</p>}
        {exportMessage && (
          <p className="mt-3 text-sm text-text-muted dark:text-night-muted" role="status" aria-live="polite">
            {exportMessage}
          </p>
        )}
        <button type="button" className="btn-ghost mt-3 w-full" onClick={closeExport}>
          Close
        </button>
      </Modal>

      {empty ? (
        <EmptyState
          illustration={<ChartIcon width={42} height={42} />}
          title="Not enough yet"
          body="A few check-ins and sleep logs from now, your rhythm will start to take shape here — mood, energy, and rest, side by side."
        />
      ) : (
        <div className="space-y-6">
          <TrendCard title="Mood" points={data.mood} max={10} color="var(--paulatim-brand)" unit="/10" />
          <TrendCard title="Energy" points={data.energy} max={10} color="var(--paulatim-warning)" unit="/10" />
          <TrendCard title="Sleep" points={data.sleep} max={12} color="var(--paulatim-success)" unit="h" />
        </div>
      )}
    </div>
  );
}



function TrendCard({
  title,
  points,
  max,
  color,
  unit,
}: {
  title: string;
  points: TrendPoint[];
  max: number;
  color: string;
  unit: string;
}) {
  if (!points.length) {
    return (
      <div className="surface-card px-6 py-6 border-l-4 border-l-base-border dark:border-l-night-border">
        <h3 className="font-display text-xl font-medium text-text-primary dark:text-night-text">{title}</h3>
        <p className="mt-1 text-base text-text-muted dark:text-night-text/80">No data in this window yet.</p>
      </div>
    );
  }

  const W = 640;
  const H = 140;
  const pad = 12;
  const vals = points.map((p) => p.value ?? 0);
  const latest = vals[vals.length - 1];
  const avg = Math.round((vals.reduce((a, b) => a + b, 0) / vals.length) * 10) / 10;

  const x = (i: number) => (points.length === 1 ? W / 2 : pad + (i / (points.length - 1)) * (W - pad * 2));
  const y = (v: number) => H - pad - (v / max) * (H - pad * 2);
  const line = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${x(i).toFixed(1)} ${y(p.value ?? 0).toFixed(1)}`).join(' ');
  const area = `${line} L ${x(points.length - 1).toFixed(1)} ${H - pad} L ${x(0).toFixed(1)} ${H - pad} Z`;
  const id = `grad-${title}`;

  return (
    <div className="surface-card px-6 py-6">
      <div className="mb-4 flex items-baseline justify-between">
        <h3 className="font-display text-xl font-medium text-text-primary dark:text-night-text">{title}</h3>
        <span className="text-sm font-medium text-text-muted dark:text-night-muted">
          now <span className="font-semibold text-text-primary dark:text-night-text ml-1 mr-3" style={{ color }}>{latest}{unit}</span> avg {avg}{unit}
        </span>
      </div>
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="h-32 w-full"
        preserveAspectRatio="none"
        role="img"
        aria-label={`${title}: latest ${latest}${unit}, average ${avg}${unit}`}
      >
        <defs>
          <linearGradient id={id} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.25" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={area} fill={`url(#${id})`} />
        <path d={line} fill="none" stroke={color} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" />
        {points.map((p, i) => (
          <circle key={i} cx={x(i)} cy={y(p.value ?? 0)} r={3.5} fill={color} className="drop-shadow-sm" />
        ))}
      </svg>
    </div>
  );
}
