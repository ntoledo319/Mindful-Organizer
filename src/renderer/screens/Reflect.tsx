import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { PageHeader, Scale } from '../components/ui';
import { formatDistanceToNow } from 'date-fns';

type Tab = 'mood' | 'sleep' | 'journal';

const JOURNAL_PROMPTS = [
  'What is taking up the most room in your head right now?',
  'Name one thing that went less badly than you feared.',
  'What would you say to a friend who had your day?',
  'Where did you feel most like yourself today?',
];

export function Reflect() {
  const [tab, setTab] = useState<Tab>('mood');
  return (
    <div>
      <PageHeader title="Reflect" subtitle="A quiet check-in. No streaks to break, no scores to chase." />
      <div className="mb-6 flex gap-2 border-b border-base-border dark:border-night-border pb-4" role="tablist" aria-label="Reflection categories">
        {(['mood', 'sleep', 'journal'] as Tab[]).map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            aria-controls={`panel-${t}`}
            id={`tab-${t}`}
            onClick={() => setTab(t)}
            className={tab === t ? 'btn-primary' : 'btn-ghost'}
          >
            {t[0].toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>
      <div id="panel-mood" role="tabpanel" aria-labelledby="tab-mood" hidden={tab !== 'mood'}>
        {tab === 'mood' && <MoodPane />}
      </div>
      <div id="panel-sleep" role="tabpanel" aria-labelledby="tab-sleep" hidden={tab !== 'sleep'}>
        {tab === 'sleep' && <SleepPane />}
      </div>
      <div id="panel-journal" role="tabpanel" aria-labelledby="tab-journal" hidden={tab !== 'journal'}>
        {tab === 'journal' && <JournalPane />}
      </div>
    </div>
  );
}

function MoodPane() {
  const queryClient = useQueryClient();
  const [mood, setMood] = useState(6);
  const [energy, setEnergy] = useState(5);
  const [anxiety, setAnxiety] = useState(3);
  const [notes, setNotes] = useState('');

  const { data: recent = [] } = useQuery({
    queryKey: ['moods'],
    queryFn: () => api.listMoods(8),
  });

  const saveMutation = useMutation({
    mutationFn: () => api.createMood({ moodScore: mood, energyLevel: energy, anxietyLevel: anxiety, notes: notes || null }),
    onSuccess: () => {
      setNotes('');
      queryClient.invalidateQueries({ queryKey: ['moods'] });
      queryClient.invalidateQueries({ queryKey: ['snapshot'] });
    },
  });

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
      <div className="surface-card space-y-6 p-7">
        <Scale label="Mood" value={mood} onChange={setMood} tone="brand" />
        <Scale label="Energy" value={energy} onChange={setEnergy} tone="success" />
        <Scale label="Anxiety" value={anxiety} onChange={setAnxiety} min={0} tone="error" />
        <textarea
          className="field min-h-[72px] resize-none"
          placeholder="Anything worth noting? (optional)"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          aria-label="Notes for check-in"
        />
        <button className="btn-primary w-full" onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
          {saveMutation.isPending ? 'Saving...' : 'Save check-in'}
        </button>
      </div>
      <RecentList
        title="Recent check-ins"
        empty="Your first check-in will appear here."
        items={recent.map((m) => ({
          id: m.id,
          primary: `Mood ${m.moodScore} · Energy ${m.energyLevel ?? '—'} · Anxiety ${m.anxietyLevel ?? '—'}`,
          secondary: relTime(m.timestamp),
          note: m.notes,
        }))}
      />
    </div>
  );
}

function SleepPane() {
  const queryClient = useQueryClient();
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [bedtime, setBedtime] = useState('23:00');
  const [wake, setWake] = useState('07:00');
  const [quality, setQuality] = useState(6);

  const { data: recent = [] } = useQuery({
    queryKey: ['sleep'],
    queryFn: () => api.listSleep(8),
  });

  const saveMutation = useMutation({
    mutationFn: () => api.createSleep({ date, bedtime, wakeTime: wake, quality }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sleep'] });
      queryClient.invalidateQueries({ queryKey: ['snapshot'] });
    },
  });

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
      <div className="surface-card space-y-5 p-7">
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Night of</span>
          <input type="date" className="field" value={date} onChange={(e) => setDate(e.target.value)} />
        </label>
        <div className="grid grid-cols-2 gap-4">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Bedtime</span>
            <input type="time" className="field" value={bedtime} onChange={(e) => setBedtime(e.target.value)} />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Woke</span>
            <input type="time" className="field" value={wake} onChange={(e) => setWake(e.target.value)} />
          </label>
        </div>
        <Scale label="How rested?" value={quality} onChange={setQuality} tone="brand" />
        <button className="btn-primary w-full" onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
          {saveMutation.isPending ? 'Logging...' : 'Log sleep'}
        </button>
      </div>
      <RecentList
        title="Recent nights"
        empty="Log a night and Hearth starts reading your rhythm."
        items={recent.map((s) => ({
          id: s.id,
          primary: `${s.durationHours}h · quality ${s.quality}/10`,
          secondary: s.date,
          note: null,
        }))}
      />
    </div>
  );
}

function JournalPane() {
  const queryClient = useQueryClient();
  const [prompt] = useState(() => JOURNAL_PROMPTS[Math.floor(Math.random() * JOURNAL_PROMPTS.length)]);
  const [content, setContent] = useState('');

  const { data: entries = [] } = useQuery({
    queryKey: ['journal'],
    queryFn: () => api.listJournal(10),
  });

  const saveMutation = useMutation({
    mutationFn: () => api.createJournal({ content: content.trim(), prompt }),
    onSuccess: () => {
      setContent('');
      queryClient.invalidateQueries({ queryKey: ['journal'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: api.deleteJournal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journal'] });
    },
  });

  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
      <div className="surface-card space-y-4 p-7 relative">
        <p className="font-display text-xl italic text-brand dark:text-night-brand">{prompt}</p>
        <textarea
          className="field min-h-[220px] resize-none leading-relaxed text-base"
          placeholder="Write as much or as little as you like…"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          aria-label="Journal entry text"
        />
        <button 
          className="btn-primary w-full" 
          onClick={() => saveMutation.mutate()} 
          disabled={!content.trim() || saveMutation.isPending}
        >
          {saveMutation.isPending ? 'Saving...' : 'Keep this entry'}
        </button>
      </div>
      <div className="space-y-3">
        {entries.length === 0 ? (
          <div className="surface-card px-6 py-10 text-center text-sm text-text-muted dark:text-night-muted/70">
            Entries stay on this machine, only for you.
          </div>
        ) : (
          entries.map((e) => (
            <div key={e.id} className="surface-card group px-6 py-5">
              <div className="flex items-start justify-between gap-3">
                <p className="text-base leading-relaxed text-text-primary dark:text-night-text/90">{e.content}</p>
                <button
                  onClick={() => deleteMutation.mutate(e.id)}
                  className="shrink-0 text-xs font-medium text-text-muted/50 opacity-0 transition group-hover:opacity-100 hover:text-semantic-error focus:opacity-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-semantic-error rounded-soft px-1"
                  aria-label="Delete entry"
                >
                  Remove
                </button>
              </div>
              <p className="mt-3 text-xs text-text-muted/60 dark:text-night-muted/50">{relTime(e.timestamp)}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function RecentList({
  title,
  empty,
  items,
}: {
  title: string;
  empty: string;
  items: { id: number; primary: string; secondary: string; note: string | null }[];
}) {
  return (
    <div>
      <h3 className="mb-4 font-display text-xl font-medium text-text-primary dark:text-night-text">{title}</h3>
      {items.length === 0 ? (
        <div className="surface-card px-6 py-10 text-center text-sm text-text-muted dark:text-night-muted">{empty}</div>
      ) : (
        <ul className="space-y-3">
          {items.map((it) => (
            <li key={it.id} className="surface-card px-5 py-4">
              <p className="text-sm font-medium text-text-primary dark:text-night-text">{it.primary}</p>
              <p className="mt-0.5 text-xs text-text-muted dark:text-night-muted/60">{it.secondary}</p>
              {it.note && <p className="mt-2 text-sm text-text-muted dark:text-night-text/80 leading-snug">{it.note}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function relTime(iso: string): string {
  try {
    // SQLite datetime('now') is UTC without a zone suffix; normalise it.
    const d = new Date(iso.includes('T') ? iso : iso.replace(' ', 'T') + 'Z');
    return formatDistanceToNow(d, { addSuffix: true });
  } catch {
    return iso;
  }
}
