import { useRef, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../lib/api';
import { estimateSpoonCost } from '@shared/spoons';
import { listItemVariants, hoverTactile } from '../lib/motion';
import type { Task, TaskInput, Priority } from '@shared/types';
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

const STATUS_TABS = [
  { label: 'Open', value: false },
  { label: 'All', value: true },
] as const;

// Seed steps for Smart Decompose. Keyword presets cover the common shapes;
// anything else gets a generic scaffold the user rewrites in the preview
// dialog before anything is committed — "Step 1" never reaches the list
// unless the person chooses to keep it.
function proposedSteps(t: Task): string[] {
  const tStr = t.title.toLowerCase();
  let steps: string[];
  if (tStr.includes('clean') || tStr.includes('tidy')) {
    steps = ['Gather supplies', 'Pick up floor', 'Wipe surfaces', 'Take out trash'];
  } else if (tStr.includes('write') || tStr.includes('essay') || tStr.includes('paper')) {
    steps = ['Create outline', 'Draft intro', 'Write body paragraphs', 'Review & edit'];
  } else if (tStr.includes('pay') || tStr.includes('bill')) {
    steps = ['Gather statements', 'Log into accounts', 'Schedule payments'];
  } else if (tStr.includes('cook') || tStr.includes('dinner') || tStr.includes('meal')) {
    steps = ['Check ingredients', 'Prep veg/protein', 'Cook', 'Clean as you go'];
  } else {
    steps = ['Step 1', 'Step 2', 'Step 3'];
  }
  return steps.map((s) => `${t.title}: ${s}`);
}

export function Tasks() {
  const queryClient = useQueryClient();
  const [showDone, setShowDone] = useState(false);
  const [open, setOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<Task | null>(null);
  const [decomposeTarget, setDecomposeTarget] = useState<Task | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Task | null>(null);
  const statusTabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  const { data: tasks, isLoading, isError, refetch } = useQuery({
    queryKey: ['tasks', showDone],
    queryFn: () => api.listTasks(showDone),
  });

  const invalidateTaskViews = () => {
    queryClient.invalidateQueries({ queryKey: ['tasks'] });
    queryClient.invalidateQueries({ queryKey: ['snapshot'] });
    queryClient.invalidateQueries({ queryKey: ['briefing'] });
  };

  const toggleMutation = useMutation({
    mutationFn: api.toggleTask,
    onSuccess: invalidateTaskViews,
  });

  const deleteMutation = useMutation({
    mutationFn: api.deleteTask,
    onSuccess: invalidateTaskViews,
  });

  const createMutation = useMutation({
    mutationFn: api.createTask,
    onSuccess: invalidateTaskViews,
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, patch }: { id: number; patch: Partial<TaskInput> }) => api.updateTask(id, patch),
    onSuccess: invalidateTaskViews,
  });

  const decomposeMutation = useMutation({
    mutationFn: ({ task, titles }: { task: Task; titles: string[] }) =>
      api.replaceTaskWithSubtasks(
        task.id,
        titles.map((title) => ({
          title,
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
    onSuccess: invalidateTaskViews,
  });

  const onStatusTabKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>, index: number) => {
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    event.preventDefault();
    const next =
      event.key === 'ArrowRight'
        ? (index + 1) % STATUS_TABS.length
        : (index - 1 + STATUS_TABS.length) % STATUS_TABS.length;
    setShowDone(STATUS_TABS[next].value);
    statusTabRefs.current[next]?.focus();
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

      {(toggleMutation.isError || deleteMutation.isError) && (
        <div className="mb-5">
          <InlineError>Ample could not update this task. Try the action again.</InlineError>
        </div>
      )}

      <div className="mb-6 flex gap-2 border-b border-base-border dark:border-night-border pb-4" role="tablist" aria-label="Task status">
        {STATUS_TABS.map((t, i) => (
          <button
            key={t.label}
            ref={(el) => {
              statusTabRefs.current[i] = el;
            }}
            role="tab"
            aria-selected={showDone === t.value}
            tabIndex={showDone === t.value ? 0 : -1}
            onClick={() => setShowDone(t.value)}
            onKeyDown={(e) => onStatusTabKeyDown(e, i)}
            className={showDone === t.value ? 'btn-primary' : 'btn-ghost'}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tasks.length === 0 ? (
        <EmptyState
          illustration={<TaskIcon width={42} height={42} />}
          title="A clear slate"
          body="Nothing is on the list right now. Add one next step and Ample will show how it fits the energy budget for today."
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
                    <span className={`h-1.5 w-1.5 rounded-full ${PRIORITY_DOT[t.priority]}`} role="img" aria-label={`Priority: ${t.priority}`} />
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
                      setEditTarget(t);
                    }}
                    className="app-no-drag rounded-soft p-2 text-text-muted transition hover:bg-brand/10 hover:text-brand focus-visible:ring-2 focus-visible:ring-brand focus:outline-none"
                    title="Edit task"
                    aria-label={`Edit ${t.title}`}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z" />
                    </svg>
                  </motion.button>
                  <motion.button
                    {...hoverTactile}
                    onClick={(e) => {
                      e.stopPropagation();
                      setDecomposeTarget(t);
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
                    onClick={() => setDeleteTarget(t)}
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

      <TaskFormModal
        key={editTarget ? `edit-${editTarget.id}` : 'new'}
        open={open || editTarget !== null}
        initialTask={editTarget}
        onClose={() => {
          setOpen(false);
          setEditTarget(null);
        }}
        onSubmit={async (input) => {
          if (editTarget) await updateMutation.mutateAsync({ id: editTarget.id, patch: input });
          else await createMutation.mutateAsync(input);
        }}
      />

      {decomposeTarget && (
        <DecomposeModal
          key={decomposeTarget.id}
          task={decomposeTarget}
          isCommitting={decomposeMutation.isPending}
          isError={decomposeMutation.isError}
          onClose={() => {
            setDecomposeTarget(null);
            decomposeMutation.reset();
          }}
          onCommit={async (titles) => {
            await decomposeMutation.mutateAsync({ task: decomposeTarget, titles });
            setDecomposeTarget(null);
          }}
        />
      )}

      <Modal open={deleteTarget !== null} onClose={() => setDeleteTarget(null)} title="Delete task?">
        <p className="text-sm leading-relaxed text-text-muted dark:text-night-muted">
          Delete “{deleteTarget?.title}”? This cannot be undone.
        </p>
        <div className="mt-6 flex justify-end gap-3">
          <button className="btn-ghost" onClick={() => setDeleteTarget(null)}>
            Cancel
          </button>
          <button
            className="btn-primary bg-semantic-error hover:bg-semantic-error/90"
            onClick={() => {
              if (deleteTarget) deleteMutation.mutate(deleteTarget.id);
              setDeleteTarget(null);
            }}
          >
            Delete
          </button>
        </div>
      </Modal>
    </div>
  );
}

function TaskFormModal({
  open,
  onClose,
  initialTask,
  onSubmit,
}: {
  open: boolean;
  onClose: () => void;
  initialTask: Task | null; // null → creating a new task
  onSubmit: (input: TaskInput) => Promise<void>;
}) {
  const editing = initialTask !== null;
  const [title, setTitle] = useState(initialTask?.title ?? '');
  const [priority, setPriority] = useState<Priority>(initialTask?.priority ?? 'medium');
  const [category, setCategory] = useState(initialTask?.category ?? 'Life');
  const [energy, setEnergy] = useState(initialTask?.energyRequired ?? 5);
  const [duration, setDuration] = useState(initialTask?.estimatedDuration ?? 30);
  const [dueDate, setDueDate] = useState(initialTask?.dueDate ?? '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const submit = async () => {
    if (!title.trim()) return;
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      const estCost = estimateSpoonCost(energy, duration);
      await onSubmit({
        title: title.trim(),
        priority,
        category,
        energyRequired: energy,
        estimatedDuration: duration,
        dueDate: dueDate || null,
        // Sent explicitly so an edit's cost tracks its new energy/duration
        // (create derives the identical value server-side when omitted).
        spoonCost: estCost,
      });
      onClose();
    } catch {
      setSubmitError(editing ? 'Ample could not save these changes. Review the fields and try again.' : 'Ample could not add this task. Review the fields and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const estCost = estimateSpoonCost(energy, duration);

  return (
    <Modal open={open} onClose={onClose} title={editing ? 'Edit task' : 'New task'}>
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
            {isSubmitting ? 'Saving…' : editing ? 'Save changes' : 'Add task'}
          </button>
        </div>
      </div>
    </Modal>
  );
}

function DecomposeModal({
  task,
  isCommitting,
  isError,
  onClose,
  onCommit,
}: {
  task: Task;
  isCommitting: boolean;
  isError: boolean;
  onClose: () => void;
  onCommit: (titles: string[]) => Promise<void>;
}) {
  const [steps, setSteps] = useState<string[]>(() => proposedSteps(task));
  const trimmed = steps.map((s) => s.trim()).filter(Boolean);

  const setStep = (index: number, value: string) =>
    setSteps((current) => current.map((s, i) => (i === index ? value : s)));
  const removeStep = (index: number) => setSteps((current) => current.filter((_, i) => i !== index));

  return (
    <Modal open onClose={onClose} title={`Break down “${task.title}”`}>
      <div className="space-y-5 pt-2">
        <p className="text-sm leading-relaxed text-text-muted dark:text-night-muted">
          Shape these steps until they fit — edit, remove, or add your own. Committing replaces the
          original task with exactly what you see, in one transaction.
        </p>
        <div className="space-y-2">
          {steps.map((step, i) => (
            <div key={i} className="flex items-center gap-2">
              <input
                className="field"
                value={step}
                onChange={(e) => setStep(i, e.target.value)}
                aria-label={`Step ${i + 1}`}
              />
              <button
                type="button"
                className="btn-ghost shrink-0 px-2 text-text-muted hover:text-semantic-error"
                onClick={() => removeStep(i)}
                disabled={steps.length <= 1}
                aria-label={`Remove step ${i + 1}`}
              >
                <TrashIcon width={14} height={14} />
              </button>
            </div>
          ))}
        </div>
        <div>
          <button type="button" className="btn-ghost" onClick={() => setSteps((current) => [...current, ''])}>
            <PlusIcon width={14} height={14} />
            Add a step
          </button>
        </div>
        {trimmed.length === 0 && (
          <p className="text-sm text-text-muted dark:text-night-muted">
            Add at least one step, or cancel to keep the original task.
          </p>
        )}
        {isError && <InlineError>Ample could not replace this task. Your steps are unchanged — try again.</InlineError>}
        <div className="flex justify-end gap-3 pt-2">
          <button className="btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button
            className="btn-primary"
            disabled={trimmed.length === 0 || isCommitting}
            onClick={() => void onCommit(trimmed)}
          >
            {isCommitting ? 'Replacing…' : `Replace with ${trimmed.length} ${trimmed.length === 1 ? 'step' : 'steps'}`}
          </button>
        </div>
      </div>
    </Modal>
  );
}
