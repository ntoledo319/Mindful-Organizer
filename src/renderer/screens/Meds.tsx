import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '../lib/api';
import { listItemVariants, hoverTactile } from '../lib/motion';
import type { Medication } from '@shared/types';
import { PageHeader, EmptyState, Modal } from '../components/ui';
import { PlusIcon, LeafIcon, TrashIcon, CheckIcon } from '../components/icons';

export function Medications() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);

  const { data: meds, isLoading } = useQuery({
    queryKey: ['medications'],
    queryFn: () => api.listMedications(),
  });

  const toggleMutation = useMutation({
    mutationFn: (m: Medication) => api.updateMedication(m.id, { active: !m.active }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medications'] });
      queryClient.invalidateQueries({ queryKey: ['snapshot'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: api.deleteMedication,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medications'] });
    },
  });


  return (
    <div>
      <PageHeader
        title="Medications"
        subtitle="Keep track of your active prescriptions and schedules."
        action={
          <button className="btn-primary" onClick={() => setOpen(true)}>
            <PlusIcon width={16} height={16} />
            Add Medication
          </button>
        }
      />

      {!isLoading && meds?.length === 0 ? (
        <EmptyState
          illustration={<LeafIcon width={42} height={42} />}
          title="No medications"
          body="Keep track of your active prescriptions, supplements, and schedules here."
          action={
            <button className="btn-primary" onClick={() => setOpen(true)}>
              Add Medication
            </button>
          }
        />
      ) : (
        <ul className="space-y-1">
          <AnimatePresence initial={false}>
            {meds?.map((m) => (
              <motion.li
                key={m.id}
                layout
                variants={listItemVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                className={`group flex items-center justify-between gap-4 border-b border-base-border px-2 py-4 last:border-0 dark:border-night-border transition-colors hover:bg-black/5 dark:hover:bg-white/5 ${m.active ? '' : 'opacity-60 grayscale'}`}
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <button
                    onClick={() => toggleMutation.mutate(m)}
                    className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border transition focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 focus:outline-none ${
                      m.active
                        ? 'border-brand bg-brand text-white dark:border-night-brand dark:bg-night-brand dark:text-night-bg'
                        : 'border-text-muted hover:border-brand dark:border-night-muted dark:hover:border-night-brand'
                    }`}
                    title={m.active ? 'Mark inactive' : 'Mark active'}
                    aria-label={m.active ? `Deactivate ${m.name}` : `Activate ${m.name}`}
                  >
                    {m.active && <CheckIcon width={14} height={14} />}
                  </button>
                  <div className="min-w-0">
                    <h3 className={`truncate font-medium text-base ${m.active ? 'text-text-primary dark:text-night-text' : 'text-text-muted dark:text-night-muted line-through'}`}>
                      {m.name} <span className="text-sm font-normal text-text-muted ml-2">{m.dosage}</span>
                    </h3>
                    <p className="text-sm text-text-muted dark:text-night-muted/80 mt-1 truncate">
                      {m.frequency} {m.reminderTime ? `· Usual time ${m.reminderTime}` : ''}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity focus-within:opacity-100 shrink-0">
                  <motion.button
                    {...hoverTactile}
                    onClick={() => deleteMutation.mutate(m.id)}
                    className="app-no-drag rounded-soft p-2 text-text-muted transition hover:bg-semantic-error/10 hover:text-semantic-error focus-visible:ring-2 focus-visible:ring-semantic-error focus:outline-none"
                    title="Delete medication"
                    aria-label={`Delete ${m.name}`}
                  >
                    <TrashIcon width={16} height={16} />
                  </motion.button>
                </div>
              </motion.li>
            ))}
          </AnimatePresence>
        </ul>
      )}

      <NewMedModal open={open} onClose={() => setOpen(false)} />
    </div>
  );
}

function NewMedModal({ open, onClose }: { open: boolean; onClose: () => void; }) {
  const queryClient = useQueryClient();
  const createMutation = useMutation({
    mutationFn: api.createMedication,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medications'] });
    },
  });
  const [name, setName] = useState('');
  const [dosage, setDosage] = useState('');
  const [frequency, setFrequency] = useState('Daily');
  const [reminderTime, setReminderTime] = useState('');

  const submit = () => {
    if (!name.trim() || !dosage.trim()) return;
    createMutation.mutate({
      name: name.trim(),
      dosage: dosage.trim(),
      frequency: frequency.trim(),
      reminderTime: reminderTime || null,
      active: true,
    }, {
      onSuccess: () => {
        setName('');
        setDosage('');
        setFrequency('Daily');
        setReminderTime('');
        onClose();
      }
    });
  };

  return (
    <Modal open={open} onClose={onClose} title="Add Medication">
      <div className="space-y-6 pt-2">
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Medication Name</span>
          <input
            autoFocus
            className="field text-lg"
            placeholder="e.g. Sertraline, Adderall, Vitamin D"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </label>
        
        <div className="grid grid-cols-2 gap-4">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Dosage</span>
            <input
              className="field"
              placeholder="e.g. 50mg"
              value={dosage}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDosage(e.target.value)}
            />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Frequency</span>
            <input
              className="field"
              placeholder="e.g. Daily, Twice a day"
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
            />
          </label>
        </div>
        
        <label className="block">
          <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">Usual Time (Optional)</span>
          <input
            type="time"
            className="field"
            value={reminderTime}
            onChange={(e) => setReminderTime(e.target.value)}
          />
        </label>

        <p className="text-xs leading-relaxed text-text-muted dark:text-night-muted">
          Hearth records this time for reference; it does not send medication reminders.
        </p>

        <div className="flex justify-end gap-3 pt-4">
          <button className="btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button className="btn-primary" onClick={submit} disabled={!name.trim() || !dosage.trim() || createMutation.isPending}>
            {createMutation.isPending ? 'Saving...' : 'Save Medication'}
          </button>
        </div>
      </div>
    </Modal>
  );
}
