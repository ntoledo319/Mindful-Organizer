import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../lib/api';
import { listItemVariants } from '../lib/motion';
import { EmptyState, InlineError, Modal, PageHeader, QueryErrorState, Scale, Spinner } from '../components/ui';
import { PlusIcon, ShieldIcon } from '../components/icons';

export function DiaryCards() {
  const [open, setOpen] = useState(false);

  const { data: cards, isLoading, isError, refetch } = useQuery({
    queryKey: ['diaryCards'],
    queryFn: () => api.listDiaryCards(50),
  });

  if (isLoading) return <Spinner />;
  if (isError || !cards) {
    return <QueryErrorState title="Diary cards didn't load" onRetry={() => void refetch()} />;
  }

  return (
    <div>
      <PageHeader
        title="Diary Cards"
        subtitle="Track urges and emotions daily to build a clear picture of what helps."
        action={
          <button className="btn-primary" onClick={() => setOpen(true)}>
            <PlusIcon width={16} height={16} />
            Log Today
          </button>
        }
      />

      {!isLoading && cards?.length === 0 ? (
        <EmptyState
          illustration={<ShieldIcon width={42} height={42} />}
          title="No diary cards yet"
          body="Diary cards help you identify patterns in urges and emotions. Log your first card today."
          action={
            <button className="btn-primary" onClick={() => setOpen(true)}>
              Log Diary Card
            </button>
          }
        />
      ) : (
        <ul className="space-y-4">
          <AnimatePresence initial={false}>
            {cards?.map((c) => (
              <motion.li
                key={c.id}
                layout
                variants={listItemVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className="surface-card flex flex-col gap-3 px-6 py-5"
              >
                <div className="flex justify-between items-baseline border-b border-base-border dark:border-night-border pb-3">
                  <h3 className="font-display text-xl font-medium text-text-primary dark:text-night-text">
                    {new Date(c.date + 'T12:00:00').toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}
                  </h3>
                  <span className="text-xs text-text-muted dark:text-night-muted">
                    {new Date(c.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mt-2">
                  <div className="flex flex-col gap-1">
                    <span className="text-xs text-text-muted dark:text-night-muted/80">Urge: Self Harm</span>
                    <span className="font-medium text-semantic-error dark:text-night-error">{c.urgesSelfHarm ?? '-'}/5</span>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-xs text-text-muted dark:text-night-muted/80">Urge: Quit Therapy</span>
                    <span className="font-medium text-semantic-error dark:text-night-error">{c.urgesQuitTherapy ?? '-'}/5</span>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-xs text-text-muted dark:text-night-muted/80">Emotion: Sadness</span>
                    <span className="font-medium text-semantic-warning dark:text-night-warning">{c.emotionsSadness ?? '-'}/5</span>
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="text-xs text-text-muted dark:text-night-muted/80">Emotion: Fear</span>
                    <span className="font-medium text-semantic-warning dark:text-night-warning">{c.emotionsFear ?? '-'}/5</span>
                  </div>
                </div>

                {c.skillsUsed && (
                  <div className="mt-3">
                    <span className="text-xs font-medium text-text-muted dark:text-night-muted/80 block mb-1">Skills Used</span>
                    <p className="text-base text-text-primary dark:text-night-text">{c.skillsUsed}</p>
                  </div>
                )}

                {c.notes && (
                  <p className="mt-2 text-base text-text-muted dark:text-night-muted/90 border-l-2 border-brand pl-4 py-1 italic">
                    {c.notes}
                  </p>
                )}
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
      )}

      <NewDiaryCardModal open={open} onClose={() => setOpen(false)} />
    </div>
  );
}

function NewDiaryCardModal({ open, onClose }: { open: boolean; onClose: () => void; }) {
  const queryClient = useQueryClient();
  const createMutation = useMutation({
    mutationFn: api.createDiaryCard,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['diaryCards'] });
      queryClient.invalidateQueries({ queryKey: ['snapshot'] });
    },
  });
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [urgesSelfHarm, setUrgesSelfHarm] = useState(0);
  const [urgesQuitTherapy, setUrgesQuitTherapy] = useState(0);
  const [emotionsSadness, setEmotionsSadness] = useState(0);
  const [emotionsFear, setEmotionsFear] = useState(0);
  const [skills, setSkills] = useState('');
  const [notes, setNotes] = useState('');

  const submit = () => {
    createMutation.mutate({
      date,
      urgesSelfHarm,
      urgesQuitTherapy,
      emotionsSadness,
      emotionsFear,
      skillsUsed: skills.trim() || null,
      notes: notes.trim() || null,
    }, {
      onSuccess: () => {
        setUrgesSelfHarm(0);
        setUrgesQuitTherapy(0);
        setEmotionsSadness(0);
        setEmotionsFear(0);
        setSkills('');
        setNotes('');
        onClose();
      }
    });
  };

  return (
    <Modal open={open} onClose={onClose} title="Log Diary Card">
      <div className="space-y-6 max-h-[70vh] overflow-y-auto px-1 pt-2">
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Date</span>
          <input
            type="date"
            className="field"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </label>
        
        <div className="space-y-2">
          <h4 className="text-sm font-semibold text-text-primary dark:text-night-text border-b border-base-border dark:border-night-border pb-2 mb-3">Urges (0-5)</h4>
          <Scale label="Self-harm" value={urgesSelfHarm} onChange={setUrgesSelfHarm} max={5} tone="error" />
          <div
            className="rounded-soft border border-semantic-error/30 bg-semantic-error/10 px-4 py-3 text-sm leading-relaxed text-text-primary dark:border-night-error/40 dark:text-night-text"
            role={urgesSelfHarm >= 4 ? 'alert' : 'note'}
          >
            <p>
              Ample records this rating locally; it does not monitor it, contact anyone, or detect an emergency.
              If you may act on a self-harm urge, use immediate human support.
            </p>
            <div className="mt-3 flex flex-wrap gap-3">
              <a className="font-semibold text-semantic-error underline underline-offset-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-semantic-error dark:text-night-error" href="tel:988">
                Call 988 (US)
              </a>
              <a className="font-semibold text-semantic-error underline underline-offset-2 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-semantic-error dark:text-night-error" href="sms:988">
                Text 988 (US)
              </a>
              <span>Elsewhere, use your local emergency number.</span>
            </div>
          </div>
          <Scale label="Quit Therapy" value={urgesQuitTherapy} onChange={setUrgesQuitTherapy} max={5} tone="error" />
        </div>

        <div className="space-y-2 pt-2">
          <h4 className="text-sm font-semibold text-text-primary dark:text-night-text border-b border-base-border dark:border-night-border pb-2 mb-3">Emotions (0-5)</h4>
          <Scale label="Sadness" value={emotionsSadness} onChange={setEmotionsSadness} max={5} tone="warning" />
          <Scale label="Fear / Anxiety" value={emotionsFear} onChange={setEmotionsFear} max={5} tone="warning" />
        </div>
        
        <label className="block pt-2">
          <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Skills Used</span>
          <input
            className="field"
            placeholder="e.g. TIPP, Radical Acceptance, Distraction"
            value={skills}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSkills(e.target.value)}
          />
        </label>
        
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Notes</span>
          <textarea
            className="field min-h-[80px] py-3 resize-none"
            placeholder="Any context or thoughts on today's urges?"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </label>

        {createMutation.isError && <InlineError>Ample could not save this card. Review the fields and try again.</InlineError>}

        <div className="flex justify-end gap-3 pt-4 pb-2">
          <button className="btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button className="btn-primary" onClick={submit} disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Saving...' : 'Save Card'}
          </button>
        </div>
      </div>
    </Modal>
  );
}
