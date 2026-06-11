import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../lib/api';
import { useStore } from '../state/store';
import { estimateSpoonCost } from '@shared/spoons';
import type { Task, Priority } from '@shared/types';
import { PageHeader, EmptyState, Modal, Scale } from '../components/ui';
import { PlusIcon, CheckIcon, TrashIcon, TaskIcon } from '../components/icons';

const PRIORITIES: Priority[] = ['low', 'medium', 'high', 'urgent'];
const PRIORITY_DOT: Record<Priority, string> = {
  low: 'bg-eucalyptus',
  medium: 'bg-sage',
  high: 'bg-lavender-deep',
  urgent: 'bg-ember',
};

const CATEGORIES = ['Life', 'Work', 'Health', 'Home', 'People', 'Money'];

export function Tasks() {
  const { bumpData } = useStore();
  const [tasks, setTasks] = useState<Task[] | null>(null);
  const [showDone, setShowDone] = useState(false);
  const [open, setOpen] = useState(false);

  const load = () => void api.listTasks(showDone).then(setTasks);
  useEffect(load, [showDone]);

  const refresh = () => {
    load();
    bumpData();
  };

  return (
    <div>
      <PageHeader
        title="Tasks"
        subtitle="Matched to the energy you have, not the energy you wish you had."
        action={
          <button className="btn-primary" onClick={() => setOpen(true)}>
            <PlusIcon width={16} height={16} />
            New task
          </button>
        }
      />

      <div className="mb-4 flex gap-2">
        <button
          onClick={() => setShowDone(false)}
          className={!showDone ? 'btn-primary' : 'btn-ghost'}
        >
          Open
        </button>
        <button onClick={() => setShowDone(true)} className={showDone ? 'btn-primary' : 'btn-ghost'}>
          All
        </button>
      </div>

      {tasks && tasks.length === 0 ? (
        <EmptyState
          illustration={<TaskIcon width={42} height={42} />}
          title="A clear slate"
          body="Nothing on the list right now. When you add something, Hearth will weigh it against your energy budget so you never overcommit a tired day."
          action={
            <button className="btn-primary" onClick={() => setOpen(true)}>
              Add the first one
            </button>
          }
        />
      ) : (
        <ul className="space-y-2">
          <AnimatePresence initial={false}>
            {tasks?.map((t) => (
              <motion.li
                key={t.id}
                layout
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, height: 0 }}
                className="glass-card flex items-center gap-3 px-4 py-3"
              >
                <button
                  onClick={() => {
                    void api.toggleTask(t.id).then(refresh);
                  }}
                  className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border transition ${
                    t.completed
                      ? 'border-sage bg-sage text-cream'
                      : 'border-charcoal/20 hover:border-sage dark:border-white/20'
                  }`}
                >
                  {t.completed && <CheckIcon width={14} height={14} />}
                </button>
                <div className="min-w-0 flex-1">
                  <p
                    className={`truncate text-sm font-medium ${
                      t.completed ? 'text-charcoal-mute line-through dark:text-cream/40' : 'text-charcoal dark:text-cream'
                    }`}
                  >
                    {t.title}
                  </p>
                  <div className="mt-0.5 flex items-center gap-2 text-xs text-charcoal-mute dark:text-cream/50">
                    <span className={`h-2 w-2 rounded-full ${PRIORITY_DOT[t.priority]}`} />
                    {t.category}
                    <span>· {t.spoonCost} spoons</span>
                    {t.dueDate && <span>· due {t.dueDate}</span>}
                  </div>
                </div>
                <button
                  onClick={() => {
                    void api.deleteTask(t.id).then(refresh);
                  }}
                  className="app-no-drag rounded-full p-1.5 text-charcoal-mute transition hover:bg-ember/10 hover:text-ember"
                >
                  <TrashIcon width={16} height={16} />
                </button>
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
      )}

      <NewTaskModal open={open} onClose={() => setOpen(false)} onSaved={refresh} />
    </div>
  );
}

function NewTaskModal({ open, onClose, onSaved }: { open: boolean; onClose: () => void; onSaved: () => void }) {
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState<Priority>('medium');
  const [category, setCategory] = useState('Life');
  const [energy, setEnergy] = useState(5);
  const [duration, setDuration] = useState(30);
  const [dueDate, setDueDate] = useState('');

  const reset = () => {
    setTitle('');
    setPriority('medium');
    setCategory('Life');
    setEnergy(5);
    setDuration(30);
    setDueDate('');
  };

  const submit = () => {
    if (!title.trim()) return;
    void api
      .createTask({
        title: title.trim(),
        priority,
        category,
        energyRequired: energy,
        estimatedDuration: duration,
        dueDate: dueDate || null,
      })
      .then(() => {
        reset();
        onClose();
        onSaved();
      });
  };

  const estCost = estimateSpoonCost(energy, duration);

  return (
    <Modal open={open} onClose={onClose} title="New task">
      <div className="space-y-4">
        <input
          autoFocus
          className="field"
          placeholder="What needs doing?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submit()}
        />
        <div className="grid grid-cols-2 gap-3">
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-charcoal-soft dark:text-cream/70">Priority</span>
            <select className="field" value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>
              {PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {p[0].toUpperCase() + p.slice(1)}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-charcoal-soft dark:text-cream/70">Area</span>
            <select className="field" value={category} onChange={(e) => setCategory(e.target.value)}>
              {CATEGORIES.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </label>
        </div>
        <Scale label="Energy this will take" value={energy} onChange={setEnergy} />
        <div className="grid grid-cols-2 gap-3">
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-charcoal-soft dark:text-cream/70">Minutes (est.)</span>
            <input
              type="number"
              min={5}
              step={5}
              className="field"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
            />
          </label>
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-charcoal-soft dark:text-cream/70">Due</span>
            <input type="date" className="field" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
          </label>
        </div>
        <p className="text-xs text-charcoal-mute dark:text-cream/50">
          Estimated cost: <span className="font-medium text-sage dark:text-eucalyptus">{estCost} spoons</span>
        </p>
        <div className="flex justify-end gap-2 pt-1">
          <button className="btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button className="btn-primary" onClick={submit} disabled={!title.trim()}>
            Add task
          </button>
        </div>
      </div>
    </Modal>
  );
}
