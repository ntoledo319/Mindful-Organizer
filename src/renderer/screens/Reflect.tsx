import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { useStore } from '../state/store';
import type { MoodEntry, SleepLog, JournalEntry } from '@shared/types';
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
      <div className="mb-5 flex gap-2">
        {(['mood', 'sleep', 'journal'] as Tab[]).map((t) => (
          <button key={t} onClick={() => setTab(t)} className={tab === t ? 'btn-primary' : 'btn-ghost'}>
            {t[0].toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>
      {tab === 'mood' && <MoodPane />}
      {tab === 'sleep' && <SleepPane />}
      {tab === 'journal' && <JournalPane />}
    </div>
  );
}

function MoodPane() {
  const { bumpData } = useStore();
  const [mood, setMood] = useState(6);
  const [energy, setEnergy] = useState(5);
  const [anxiety, setAnxiety] = useState(3);
  const [notes, setNotes] = useState('');
  const [recent, setRecent] = useState<MoodEntry[]>([]);

  const load = () => void api.listMoods(8).then(setRecent);
  useEffect(load, []);

  const save = () => {
    void api
      .createMood({ moodScore: mood, energyLevel: energy, anxietyLevel: anxiety, notes: notes || null })
      .then(() => {
        setNotes('');
        load();
        bumpData();
      });
  };

  return (
    <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
      <div className="glass-card space-y-5 p-6">
        <Scale label="Mood" value={mood} onChange={setMood} />
        <Scale label="Energy" value={energy} onChange={setEnergy} tone="lavender" />
        <Scale label="Anxiety" value={anxiety} onChange={setAnxiety} min={0} tone="ember" />
        <textarea
          className="field min-h-[72px] resize-none"
          placeholder="Anything worth noting? (optional)"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
        <button className="btn-primary w-full" onClick={save}>
          Save check-in
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
  const { bumpData } = useStore();
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [bedtime, setBedtime] = useState('23:00');
  const [wake, setWake] = useState('07:00');
  const [quality, setQuality] = useState(6);
  const [recent, setRecent] = useState<SleepLog[]>([]);

  const load = () => void api.listSleep(8).then(setRecent);
  useEffect(load, []);

  const save = () => {
    void api.createSleep({ date, bedtime, wakeTime: wake, quality }).then(() => {
      load();
      bumpData();
    });
  };

  return (
    <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
      <div className="glass-card space-y-4 p-6">
        <label className="block">
          <span className="mb-1.5 block text-sm font-medium text-charcoal-soft dark:text-cream/70">Night of</span>
          <input type="date" className="field" value={date} onChange={(e) => setDate(e.target.value)} />
        </label>
        <div className="grid grid-cols-2 gap-3">
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-charcoal-soft dark:text-cream/70">Bedtime</span>
            <input type="time" className="field" value={bedtime} onChange={(e) => setBedtime(e.target.value)} />
          </label>
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-charcoal-soft dark:text-cream/70">Woke</span>
            <input type="time" className="field" value={wake} onChange={(e) => setWake(e.target.value)} />
          </label>
        </div>
        <Scale label="How rested?" value={quality} onChange={setQuality} />
        <button className="btn-primary w-full" onClick={save}>
          Log sleep
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
  const { bumpData } = useStore();
  const [prompt] = useState(() => JOURNAL_PROMPTS[Math.floor(Math.random() * JOURNAL_PROMPTS.length)]);
  const [content, setContent] = useState('');
  const [entries, setEntries] = useState<JournalEntry[]>([]);

  const load = () => void api.listJournal(10).then(setEntries);
  useEffect(load, []);

  const save = () => {
    if (!content.trim()) return;
    void api.createJournal({ content: content.trim(), prompt }).then(() => {
      setContent('');
      load();
      bumpData();
    });
  };

  return (
    <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
      <div className="glass-card space-y-3 p-6">
        <p className="font-display text-lg italic text-sage dark:text-eucalyptus">{prompt}</p>
        <textarea
          className="field min-h-[180px] resize-none leading-relaxed"
          placeholder="Write as much or as little as you like…"
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <button className="btn-primary w-full" onClick={save} disabled={!content.trim()}>
          Keep this entry
        </button>
      </div>
      <div className="space-y-2">
        {entries.length === 0 ? (
          <div className="glass-card px-5 py-8 text-center text-sm text-charcoal-mute dark:text-cream/50">
            Entries stay on this machine, only for you.
          </div>
        ) : (
          entries.map((e) => (
            <div key={e.id} className="glass-card group px-5 py-4">
              <div className="flex items-start justify-between gap-2">
                <p className="text-sm leading-relaxed text-charcoal-soft dark:text-cream/75">{e.content}</p>
                <button
                  onClick={() => void api.deleteJournal(e.id).then(load)}
                  className="shrink-0 text-xs text-charcoal-mute opacity-0 transition group-hover:opacity-100 hover:text-ember"
                >
                  Remove
                </button>
              </div>
              <p className="mt-2 text-xs text-charcoal-mute dark:text-cream/40">{relTime(e.timestamp)}</p>
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
      <h3 className="mb-3 font-display text-lg font-semibold text-charcoal dark:text-cream">{title}</h3>
      {items.length === 0 ? (
        <div className="glass-card px-5 py-8 text-center text-sm text-charcoal-mute dark:text-cream/50">{empty}</div>
      ) : (
        <ul className="space-y-2">
          {items.map((it) => (
            <li key={it.id} className="glass-card px-4 py-3">
              <p className="text-sm font-medium text-charcoal dark:text-cream">{it.primary}</p>
              <p className="text-xs text-charcoal-mute dark:text-cream/40">{it.secondary}</p>
              {it.note && <p className="mt-1 text-sm text-charcoal-soft dark:text-cream/60">{it.note}</p>}
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
