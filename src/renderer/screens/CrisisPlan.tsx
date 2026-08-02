import { useEffect, useRef, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import type { CrisisPlan, CrisisContact } from '@shared/types';
import { InlineError, PageHeader, QueryErrorState, Spinner } from '../components/ui';

// The crisis plan is the one screen that must never feel like a form. It opens
// with the lifeline already visible — help first, editing second. Unsaved edits
// auto-save on navigation: this screen's whole purpose is being reliable.

export function CrisisPlanScreen() {
  const queryClient = useQueryClient();
  const [localPlan, setLocalPlan] = useState<CrisisPlan | null>(null);
  const [saved, setSaved] = useState(false);
  // Tracks unsaved edits so leaving the screen never silently discards them.
  const dirtyPlanRef = useRef<{ dirty: boolean; plan: CrisisPlan | null }>({ dirty: false, plan: null });

  const { data: serverPlan, isLoading, isError, refetch } = useQuery({
    queryKey: ['crisisPlan'],
    queryFn: () => api.getCrisisPlan(),
  });

  // Sync server data to local state for editing
  useEffect(() => {
    if (serverPlan && !localPlan) {
      setLocalPlan(serverPlan);
    }
  }, [serverPlan, localPlan]);

  useEffect(() => {
    if (!localPlan || !serverPlan) return;
    dirtyPlanRef.current = {
      dirty: JSON.stringify(localPlan) !== JSON.stringify(serverPlan),
      plan: localPlan,
    };
  }, [localPlan, serverPlan]);

  // Auto-save unsaved edits when the screen unmounts (route change).
  useEffect(() => {
    return () => {
      const { dirty, plan } = dirtyPlanRef.current;
      if (dirty && plan) {
        void api
          .saveCrisisPlan(plan)
          .then((savedPlan) => queryClient.setQueryData(['crisisPlan'], savedPlan))
          .catch(() => {
            // A failed auto-save loses nothing that wasn't already lost before
            // this guard existed; the explicit Save path still surfaces errors.
          });
      }
    };
  }, [queryClient]);

  const updateMutation = useMutation({
    mutationFn: api.saveCrisisPlan,
    onSuccess: (newPlan) => {
      queryClient.setQueryData(['crisisPlan'], newPlan);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    },
  });

  if (isLoading) return <Spinner />;
  if (isError) {
    return <QueryErrorState title="Your crisis plan didn't load" onRetry={() => void refetch()} />;
  }
  if (!localPlan) return <Spinner />;

  const update = (patch: Partial<CrisisPlan>) => setLocalPlan({ ...localPlan, ...patch });

  const save = () => {
    updateMutation.mutate(localPlan);
  };

  const setList = (key: 'warningSigns' | 'copingStrategies', text: string) =>
    update({ [key]: text.split('\n').map((s) => s.trim()).filter(Boolean) } as Partial<CrisisPlan>);

  const updateContact = (i: number, patch: Partial<CrisisContact>) => {
    const contacts = localPlan.contacts.map((c, idx) => (idx === i ? { ...c, ...patch } : c));
    update({ contacts });
  };

  const removeContact = (i: number) => {
    update({ contacts: localPlan.contacts.filter((_, index) => index !== i) });
  };

  return (
    <div>
      <PageHeader title="Crisis plan" subtitle="Built in the calm, for the storm. Yours alone, stored only here." />

      <div className="mb-8 rounded-soft border border-semantic-error/30 bg-semantic-error/10 px-6 py-5 shadow-sm">
        <p className="text-base font-semibold text-semantic-error dark:text-night-error">If you're in danger right now</p>
        <p className="mt-1 text-base text-text-primary dark:text-night-text">
          Call or text <span className="font-semibold">988</span> (Suicide & Crisis Lifeline, US), or your local
          emergency number. You don't have to carry this alone.
        </p>
        <div className="mt-4 flex flex-wrap gap-3">
          <a
            href="tel:988"
            className="inline-flex rounded-full bg-semantic-error px-5 py-2 text-sm font-medium text-white transition hover:bg-semantic-error/90 focus-visible:ring-2 focus-visible:ring-semantic-error focus-visible:ring-offset-2 focus:outline-none"
          >
            Call 988
          </a>
          <a
            href="sms:988"
            className="inline-flex rounded-full border border-semantic-error/40 px-5 py-2 text-sm font-medium text-semantic-error transition hover:bg-semantic-error/10 focus-visible:ring-2 focus-visible:ring-semantic-error focus-visible:ring-offset-2 focus:outline-none dark:border-night-error/50 dark:text-night-error"
          >
            Text 988
          </a>
        </div>
      </div>

      <div className="space-y-6">
        <div className="surface-card p-6">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">
              My early warning signs <span className="font-normal text-text-muted">(one per line)</span>
            </span>
            <textarea
              className="field min-h-[100px] resize-none"
              placeholder={'Skipping meals\nCanceling plans\nNot sleeping'}
              value={localPlan.warningSigns.join('\n')}
              onChange={(e) => setList('warningSigns', e.target.value)}
            />
          </label>
        </div>

        <div className="surface-card p-6">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">
              What helps me <span className="font-normal text-text-muted">(one per line)</span>
            </span>
            <textarea
              className="field min-h-[100px] resize-none"
              placeholder={'Step outside\nText my sister\nCold water on my face'}
              value={localPlan.copingStrategies.join('\n')}
              onChange={(e) => setList('copingStrategies', e.target.value)}
            />
          </label>
        </div>

        <div className="surface-card p-6">
          <div className="mb-4 flex items-center justify-between">
            <span className="text-sm font-medium text-text-primary dark:text-night-text">People I can reach</span>
            <button
              className="btn-ghost"
              onClick={() => update({ contacts: [...localPlan.contacts, { name: '', relationship: '', phone: '' }] })}
            >
              Add person
            </button>
          </div>
          <div className="space-y-3">
            {localPlan.contacts.length === 0 && (
              <p className="text-sm text-text-muted dark:text-night-muted/80">No one added yet.</p>
            )}
            {localPlan.contacts.map((c, i) => (
              <div key={i} className="grid grid-cols-1 gap-3 rounded-soft border border-base-border bg-black/5 p-3 dark:border-night-border dark:bg-white/5 sm:grid-cols-[1fr_1fr_1fr_auto]">
                <input
                  className="field bg-base-bg dark:bg-night-bg"
                  placeholder="Name"
                  value={c.name}
                  onChange={(e) => updateContact(i, { name: e.target.value })}
                  aria-label={`Contact ${i + 1} Name`}
                />
                <input
                  className="field bg-base-bg dark:bg-night-bg"
                  placeholder="Relationship"
                  value={c.relationship}
                  onChange={(e) => updateContact(i, { relationship: e.target.value })}
                  aria-label={`Contact ${i + 1} Relationship`}
                />
                <input
                  className="field bg-base-bg dark:bg-night-bg"
                  placeholder="Phone"
                  value={c.phone}
                  onChange={(e) => updateContact(i, { phone: e.target.value })}
                  aria-label={`Contact ${i + 1} Phone`}
                />
                <button
                  type="button"
                  className="btn-ghost px-3 text-semantic-error hover:text-semantic-error dark:text-night-error dark:hover:text-night-error"
                  onClick={() => removeContact(i)}
                  aria-label={`Remove contact ${c.name || i + 1}`}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>

        <div className="surface-card p-6">
          <label className="block">
            <span className="mb-2 block text-sm font-medium text-text-primary dark:text-night-text">
              A note to my future self
            </span>
            <textarea
              className="field min-h-[100px] resize-none"
              placeholder="Something you'd want to hear on a hard day."
              value={localPlan.safeNote}
              onChange={(e) => update({ safeNote: e.target.value })}
            />
          </label>
        </div>

        <div className="flex items-center gap-4 pt-2">
          <button className="btn-primary" onClick={save} disabled={updateMutation.isPending}>
            {updateMutation.isPending ? 'Saving...' : 'Save plan'}
          </button>
          {saved && <span className="text-sm font-medium text-semantic-success dark:text-night-success" role="status">Saved.</span>}
          <span className="text-xs text-text-muted dark:text-night-muted">
            Unsaved edits are kept automatically if you leave this screen.
          </span>
        </div>
        {updateMutation.isError && <InlineError>Hearth could not save this plan. Your edits are still on screen; try again.</InlineError>}
      </div>
    </div>
  );
}
