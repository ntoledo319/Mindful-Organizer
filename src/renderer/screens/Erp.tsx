import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../lib/api';
import { listItemVariants } from '../lib/motion';
import { PageHeader, EmptyState, Modal, Scale } from '../components/ui';
import { PlusIcon, LeafIcon } from '../components/icons';

export function ErpTracker() {
  const [open, setOpen] = useState(false);

  const { data: sessions, isLoading } = useQuery({
    queryKey: ['erpSessions'],
    queryFn: () => api.listErpSessions(50),
  });


  return (
    <div>
      <PageHeader
        title="ERP Tracker"
        subtitle="Face the fear, delay the response. You are stronger than the obsession."
        action={
          <button className="btn-primary" onClick={() => setOpen(true)}>
            <PlusIcon width={16} height={16} />
            Log Session
          </button>
        }
      />

      {!isLoading && sessions?.length === 0 ? (
        <EmptyState
          illustration={<LeafIcon width={42} height={42} />}
          title="No exposures yet"
          body="Every time you sit with the anxiety instead of acting on the compulsion, you rewire your brain. Start your first exposure session today."
          action={
            <button className="btn-primary" onClick={() => setOpen(true)}>
              Log an Exposure
            </button>
          }
        />
      ) : (
        <ul className="space-y-4">
          <AnimatePresence initial={false}>
            {sessions?.map((s) => (
              <motion.li
                key={s.id}
                layout
                variants={listItemVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="surface-card flex flex-col gap-3 px-6 py-5"
              >
                <div className="flex justify-between items-start border-b border-base-border dark:border-night-border pb-3">
                  <div>
                    <h3 className="font-display text-xl font-medium text-text-primary dark:text-night-text">{s.targetObsession}</h3>
                    <p className="text-base text-text-muted dark:text-night-text/80 mt-1">{s.exposureActivity}</p>
                  </div>
                  <div className="text-right shrink-0 ml-4">
                    <span className="text-xs text-text-muted dark:text-night-muted">
                      {new Date(s.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                    </span>
                  </div>
                </div>
                
                <div className="flex gap-6 mt-1 text-sm">
                  <div className="flex flex-col gap-1">
                    <span className="text-xs font-medium text-text-muted dark:text-night-muted/80">Pre-Anxiety</span>
                    <span className="font-medium text-semantic-error">{s.preAnxiety}/10</span>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-xs font-medium text-text-muted dark:text-night-muted/80">Post-Anxiety</span>
                    <span className="font-medium text-semantic-success">{s.postAnxiety}/10</span>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-xs font-medium text-text-muted dark:text-night-muted/80">Duration</span>
                    <span className="font-medium text-text-primary dark:text-night-text/90">{s.durationMinutes} min</span>
                  </div>
                </div>
                {s.notes && (
                  <p className="mt-2 text-base italic text-text-muted dark:text-night-text/70 border-l-2 border-brand pl-4 py-1">"{s.notes}"</p>
                )}
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
      )}

      <NewErpModal open={open} onClose={() => setOpen(false)} />
    </div>
  );
}

function NewErpModal({ open, onClose }: { open: boolean; onClose: () => void; }) {
  const queryClient = useQueryClient();
  const createMutation = useMutation({
    mutationFn: api.createErpSession,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['erpSessions'] });
      queryClient.invalidateQueries({ queryKey: ['snapshot'] });
    },
  });
  const [obsession, setObsession] = useState('');
  const [activity, setActivity] = useState('');
  const [pre, setPre] = useState(5);
  const [post, setPost] = useState(2);
  const [duration, setDuration] = useState(15);
  const [notes, setNotes] = useState('');

  const submit = () => {
    if (!obsession.trim() || !activity.trim()) return;
    createMutation.mutate({
      targetObsession: obsession.trim(),
      exposureActivity: activity.trim(),
      preAnxiety: pre,
      postAnxiety: post,
      durationMinutes: duration,
      notes: notes.trim() || null,
    }, {
      onSuccess: () => {
        setObsession('');
        setActivity('');
        setPre(5);
        setPost(2);
        setDuration(15);
        setNotes('');
        onClose();
      }
    });
  };

  return (
    <Modal open={open} onClose={onClose} title="Log Exposure Session">
      <div className="space-y-6 pt-2 max-h-[70vh] overflow-y-auto px-1">
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Target Obsession</span>
          <input
            autoFocus
            className="field text-lg"
            placeholder="e.g. Contamination, Harm, Checking"
            value={obsession}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setObsession(e.target.value)}
          />
        </label>
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Exposure Activity</span>
          <input
            className="field"
            placeholder="What did you do to trigger it?"
            value={activity}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setActivity(e.target.value)}
          />
        </label>
        
        <div className="space-y-4 border-y border-base-border dark:border-night-border py-4">
          <Scale label="Pre-Exposure Anxiety" value={pre} onChange={setPre} tone="error" />
          <Scale label="Post-Exposure Anxiety" value={post} onChange={setPost} tone="success" />
        </div>
        
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Duration (Minutes)</span>
          <input
            type="number"
            min={1}
            className="field"
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
          />
        </label>
        
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Notes (Optional)</span>
          <textarea
            className="field min-h-[80px] py-3 resize-none"
            placeholder="Did you resist the compulsion? How did it feel?"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </label>

        <div className="flex justify-end gap-3 pt-2 pb-2">
          <button className="btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button className="btn-primary" onClick={submit} disabled={!obsession.trim() || !activity.trim() || createMutation.isPending}>
            {createMutation.isPending ? 'Saving...' : 'Save Session'}
          </button>
        </div>
      </div>
    </Modal>
  );
}
