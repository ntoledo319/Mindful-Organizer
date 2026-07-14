import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../lib/api';
import { estimateSpoonCost } from '@shared/spoons';
import { listItemVariants, hoverTactile } from '../lib/motion';
import type { Task, Priority } from '@shared/types';
import { EmptyState, InlineError, Modal, PageHeader, QueryErrorState, Scale, Spinner } from '../components/ui';
import { PlusIcon, CheckIcon, TrashIcon, TaskIcon } from '../components/icons';

const PRIORITIES: Priority[] = ['low', 'medium', 'high', 'urgent'];
const PRIORITY_DOT: Record<Priority, string> = {
  low: 'bg-semantic-success',
  medium: 'bg-brand',
  high: 'bg-semantic-warning',
  urgent: 'bg-semantic-error',
};

const CATEGORIES = ['Life', 'Work', 'Health', 'Home', 'People', 'Money'];

export function Tasks() {
  const queryClient = useQueryClient();
  const [showDone, setShowDone] = useState(false);
  const [open, setOpen] = useState(false);

  const { data: tasks, isLoading, isError, refetch } = useQuery({
    queryKey: ['tasks', showDone],
    queryFn: () => api.listTasks(showDone),
  });

  const toggleMutation = useMutation({
    mutationFn: api.toggleTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['snapshot'] });
      queryClient.invalidateQueries({ queryKey: ['briefing'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: api.deleteTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['snapshot'] });
      queryClient.invalidateQueries({ queryKey: ['briefing'] });
    },
  });

  const createMutation = useMutation({
    mutationFn: api.createTask,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['snapshot'] });
      queryClient.invalidateQueries({ queryKey: ['briefing'] });
    },
  });

  const decomposeMutation = useMutation({
    mutationFn: ({ task, titles }: { task: Task; titles: string[] }) =>
      api.replaceTaskWithSubtasks(
        task.id,
        titles.map((title) => ({
          title: `${task.title}: ${title}`,
          priority: task.priority,
          category: task.category,
          energyRequired: Math.max(1, Math.round(task.energyRequired / titles.length)),
          estimatedDuration:
            task.estimatedDuration == null
              ? null
              : Math.max(5, Math.round(task.estimatedDuration / titles.length)),
          dueDate: task.dueDate,
        })),
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['snapshot'] });
      queryClient.invalidateQueries({ queryKey: ['briefing'] });
    },
  });


  const smartDecompose = (t: Task) => {
    const tStr = t.title.toLowerCase();
    const subtasks: string[] = [];
    if (tStr.includes('clean') || tStr.includes('tidy')) {
      subtasks.push('Gather supplies', 'Pick up floor', 'Wipe surfaces', 'Take out trash');
    } else if (tStr.includes('write') || tStr.includes('essay') || tStr.includes('paper')) {
      subtasks.push('Create outline', 'Draft intro', 'Write body paragraphs', 'Review & edit');
    } else if (tStr.includes('pay') || tStr.includes('bill')) {
      subtasks.push('Gather statements', 'Log into accounts', 'Schedule payments');
    } else if (tStr.includes('cook') || tStr.includes('dinner') || tStr.includes('meal')) {
      subtasks.push('Check ingredients', 'Prep veg/protein', 'Cook', 'Clean as you go');
    } else {
      subtasks.push('Step 1', 'Step 2', 'Step 3');
    }
    
    if (confirm(`Smart Decompose will break "${t.title}" into:\n- ${subtasks.join('\n- ')}\n\nProceed?`)) {
      decomposeMutation.mutate({ task: t, titles: subtasks });
    }
  };

  if (isLoading) return <Spinner />;
  if (isError || !tasks) {
    return <QueryErrorState title="Tasks didn't load" onRetry={() => void refetch()} />;
  }

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

      {(toggleMutation.isError || deleteMutation.isError || decomposeMutation.isError) && (
        <div className="mb-5">
          <InlineError>Hearth could not update this task. Try the action again.</InlineError>
        </div>
      )}

      <div className="mb-6 flex gap-2 border-b border-base-border dark:border-night-border pb-4" role="tablist" aria-label="Task status">
        <button
          role="tab"
          aria-selected={!showDone}
          onClick={() => setShowDone(false)}
          className={!showDone ? 'btn-primary' : 'btn-ghost'}
        >
          Open
        </button>
        <button 
          role="tab"
          aria-selected={showDone}
          onClick={() => setShowDone(true)} 
          className={showDone ? 'btn-primary' : 'btn-ghost'}
        >
          All
        </button>
      </div>

      {tasks.length === 0 ? (
        <EmptyState
          illustration={<TaskIcon width={42} height={42} />}
          title="A clear slate"
          body="Nothing is on the list right now. Add one next step and Hearth will show how it fits the energy budget for today."
          action={
            <button className="btn-primary" onClick={() => setOpen(true)}>
              Add the first one
            </button>
          }
        />
      ) : (
        <ul className="space-y-1">
          <AnimatePresence initial={false}>
            {tasks.map((t) => (
              <motion.li
                key={t.id}
                layout
                variants={listItemVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="group flex items-center gap-4 border-b border-base-border px-2 py-4 last:border-0 dark:border-night-border transition-colors hover:bg-black/5 dark:hover:bg-white/5"
              >
                <button
                  onClick={() => toggleMutation.mutate(t.id)}
                  aria-label={t.completed ? 'Mark incomplete' : 'Mark complete'}
                  className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border transition focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 focus:outline-none ${
                    t.completed
                      ? 'border-brand bg-brand text-white dark:border-night-brand dark:bg-night-brand dark:text-night-bg'
                      : 'border-text-muted hover:border-brand dark:border-night-muted dark:hover:border-night-brand'
                  }`}
                >
                  {t.completed && <CheckIcon width={14} height={14} />}
                </button>
                <div className="min-w-0 flex-1">
                  <p
                    className={`truncate text-base font-medium ${
                      t.completed ? 'text-text-muted line-through dark:text-night-muted' : 'text-text-primary dark:text-night-text'
                    }`}
                  >
                    {t.title}
                  </p>
                  <div className="mt-1 flex items-center gap-2 text-xs text-text-muted dark:text-night-muted/80">
                    <span className={`h-1.5 w-1.5 rounded-full ${PRIORITY_DOT[t.priority]}`} aria-label={`Priority: ${t.priority}`} />
                    {t.category}
                    <span>· {t.spoonCost} spoons</span>
                    {t.dueDate && <span>· due {t.dueDate}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity focus-within:opacity-100">
                  <motion.button
                    {...hoverTactile}
                    onClick={(e) => {
                      e.stopPropagation();
                      smartDecompose(t);
                    }}
                    className="app-no-drag rounded-soft p-2 text-text-muted transition hover:bg-brand/10 hover:text-brand focus-visible:ring-2 focus-visible:ring-brand focus:outline-none"
                    title="Smart Decompose"
                    aria-label={`Decompose ${t.title}`}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                      <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
                      <line x1="12" y1="22.08" x2="12" y2="12" />
                      <line x1="12" y1="12" x2="16.5" y2="9.5" />
                    </svg>
                  </motion.button>
                  <motion.button
                    {...hoverTactile}
                    onClick={() => {
                      if (window.confirm(`Delete “${t.title}”? This cannot be undone.`)) deleteMutation.mutate(t.id);
                    }}
                    className="app-no-drag rounded-soft p-2 text-text-muted transition hover:bg-semantic-error/10 hover:text-semantic-error focus-visible:ring-2 focus-visible:ring-semantic-error focus:outline-none"
                    aria-label={`Delete ${t.title}`}
                  >
                    <TrashIcon width={16} height={16} />
                  </motion.button>
                </div>
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
      )}

      <NewTaskModal open={open} onClose={() => setOpen(false)} onCreate={async (t) => { await createMutation.mutateAsync(t); }} />
    </div>
  );
}

function NewTaskModal({ open, onClose, onCreate }: { open: boolean; onClose: () => void; onCreate: (task: Parameters<typeof api.createTask>[0]) => Promise<void>; }) {
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState<Priority>('medium');
  const [category, setCategory] = useState('Life');
  const [energy, setEnergy] = useState(5);
  const [duration, setDuration] = useState(30);
  const [dueDate, setDueDate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const reset = () => {
    setTitle('');
    setPriority('medium');
    setCategory('Life');
    setEnergy(5);
    setDuration(30);
    setDueDate('');
  };

  const submit = async () => {
    if (!title.trim()) return;
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      await onCreate({
        title: title.trim(),
        priority,
        category,
        energyRequired: energy,
        estimatedDuration: duration,
        dueDate: dueDate || null,
      });
      reset();
      onClose();
    } catch {
      setSubmitError('Hearth could not add this task. Review the fields and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const estCost = estimateSpoonCost(energy, duration);

  return (
    <Modal open={open} onClose={onClose} title="New task">
      <div className="space-y-5 pt-2">
        <input
          autoFocus
          className="field text-lg"
          placeholder="What needs doing?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => {
            if (e.key === 'Enter') submit();
          }}
          aria-label="Task title"
        />
        <div className="grid grid-cols-2 gap-4">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Priority</span>
            <select className="field" value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>
              {PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {p[0].toUpperCase() + p.slice(1)}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Area</span>
            <select className="field" value={category} onChange={(e) => setCategory(e.target.value)}>
              {CATEGORIES.map((c) => (
                <option key={c}>{c}</option>
              ))}
            </select>
          </label>
        </div>
        <Scale label="Energy this will take" value={energy} onChange={setEnergy} />
        <div className="grid grid-cols-2 gap-4">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Minutes (est.)</span>
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
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Due</span>
            <input type="date" className="field" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
          </label>
        </div>
        <div className="rounded-soft bg-black/5 dark:bg-white/5 p-3 flex justify-between items-center">
          <span className="text-sm font-medium text-text-primary dark:text-night-text">Estimated cost</span>
          <span className="font-display text-lg font-semibold text-brand dark:text-night-brand">{estCost} spoons</span>
        </div>
        {submitError && <InlineError>{submitError}</InlineError>}
        <div className="flex justify-end gap-3 pt-2">
          <button className="btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button className="btn-primary" onClick={submit} disabled={!title.trim() || isSubmitting}>
            {isSubmitting ? 'Adding...' : 'Add task'}
          </button>
        </div>
      </div>
    </Modal>
  );
}
