import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { useStore } from '../state/store';
import type { Trends as TrendData, TrendPoint } from '@shared/types';
import { PageHeader, EmptyState, Spinner } from '../components/ui';
import { ChartIcon } from '../components/icons';

export function Trends() {
  const { dataVersion } = useStore();
  const [days, setDays] = useState(14);
  const [data, setData] = useState<TrendData | null>(null);

  useEffect(() => {
    void api.getTrends(days).then(setData);
  }, [days, dataVersion]);

  if (!data) return <Spinner />;

  const empty = !data.mood.length && !data.sleep.length && !data.energy.length;

  return (
    <div>
      <PageHeader
        title="Rhythm"
        subtitle="Patterns, not performance. The shape of a few weeks tells more than any single day."
        action={
          <div className="flex gap-2">
            {[7, 14, 30].map((d) => (
              <button key={d} onClick={() => setDays(d)} className={days === d ? 'btn-primary' : 'btn-ghost'}>
                {d}d
              </button>
            ))}
          </div>
        }
      />

      {empty ? (
        <EmptyState
          illustration={<ChartIcon width={42} height={42} />}
          title="Not enough yet"
          body="A few check-ins and sleep logs from now, your rhythm will start to take shape here — mood, energy, and rest, side by side."
        />
      ) : (
        <div className="space-y-4">
          <TrendCard title="Mood" points={data.mood} max={10} color="#3E5C50" unit="/10" />
          <TrendCard title="Energy" points={data.energy} max={10} color="#A79FD0" unit="/10" />
          <TrendCard title="Sleep" points={data.sleep} max={12} color="#6E8C7E" unit="h" />
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
      <div className="glass-card px-5 py-6">
        <h3 className="font-display text-lg font-semibold text-charcoal dark:text-cream">{title}</h3>
        <p className="mt-1 text-sm text-charcoal-mute dark:text-cream/50">No data in this window yet.</p>
      </div>
    );
  }

  const W = 640;
  const H = 120;
  const pad = 8;
  const vals = points.map((p) => p.value ?? 0);
  const latest = vals[vals.length - 1];
  const avg = Math.round((vals.reduce((a, b) => a + b, 0) / vals.length) * 10) / 10;

  const x = (i: number) => (points.length === 1 ? W / 2 : pad + (i / (points.length - 1)) * (W - pad * 2));
  const y = (v: number) => H - pad - (v / max) * (H - pad * 2);
  const line = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${x(i).toFixed(1)} ${y(p.value ?? 0).toFixed(1)}`).join(' ');
  const area = `${line} L ${x(points.length - 1).toFixed(1)} ${H - pad} L ${x(0).toFixed(1)} ${H - pad} Z`;
  const id = `grad-${title}`;

  return (
    <div className="glass-card px-5 py-5">
      <div className="mb-2 flex items-baseline justify-between">
        <h3 className="font-display text-lg font-semibold text-charcoal dark:text-cream">{title}</h3>
        <span className="text-sm text-charcoal-mute dark:text-cream/50">
          now <span className="font-medium" style={{ color }}>{latest}{unit}</span> · avg {avg}{unit}
        </span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} className="h-28 w-full" preserveAspectRatio="none">
        <defs>
          <linearGradient id={id} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.25" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={area} fill={`url(#${id})`} />
        <path d={line} fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        {points.map((p, i) => (
          <circle key={i} cx={x(i)} cy={y(p.value ?? 0)} r={2.5} fill={color} />
        ))}
      </svg>
    </div>
  );
}
