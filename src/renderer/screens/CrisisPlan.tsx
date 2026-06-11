import { useEffect, useState } from 'react';
import { api } from '../lib/api';
import type { CrisisPlan, CrisisContact } from '@shared/types';
import { PageHeader, Spinner } from '../components/ui';

// The crisis plan is the one screen that must never feel like a form. It opens
// with the lifeline already visible — help first, editing second.

export function CrisisPlanScreen() {
  const [plan, setPlan] = useState<CrisisPlan | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    void api.getCrisisPlan().then(setPlan);
  }, []);

  if (!plan) return <Spinner />;

  const update = (patch: Partial<CrisisPlan>) => setPlan({ ...plan, ...patch });

  const save = () => {
    void api.saveCrisisPlan(plan).then(() => {
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    });
  };

  const setList = (key: 'warningSigns' | 'copingStrategies', text: string) =>
    update({ [key]: text.split('\n').map((s) => s.trim()).filter(Boolean) } as Partial<CrisisPlan>);

  const updateContact = (i: number, patch: Partial<CrisisContact>) => {
    const contacts = plan.contacts.map((c, idx) => (idx === i ? { ...c, ...patch } : c));
    update({ contacts });
  };

  return (
    <div>
      <PageHeader title="Crisis plan" subtitle="Built in the calm, for the storm. Yours alone, stored only here." />

      <div className="mb-6 rounded-glass border border-ember/30 bg-ember/10 px-5 py-4">
        <p className="text-sm font-semibold text-ember">If you're in danger right now</p>
        <p className="mt-1 text-sm text-charcoal-soft dark:text-cream/70">
          Call or text <span className="font-semibold">988</span> (Suicide & Crisis Lifeline, US), or your local
          emergency number. You don't have to carry this alone.
        </p>
        <a
          href="tel:988"
          className="mt-3 inline-flex rounded-full bg-ember px-4 py-1.5 text-xs font-medium text-cream"
        >
          Call 988
        </a>
      </div>

      <div className="space-y-4">
        <div className="glass-card p-5">
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-charcoal-soft dark:text-cream/70">
              My early warning signs <span className="font-normal text-charcoal-mute">(one per line)</span>
            </span>
            <textarea
              className="field min-h-[90px] resize-none"
              placeholder={'Skipping meals\nCanceling plans\nNot sleeping'}
              value={plan.warningSigns.join('\n')}
              onChange={(e) => setList('warningSigns', e.target.value)}
            />
          </label>
        </div>

        <div className="glass-card p-5">
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-charcoal-soft dark:text-cream/70">
              What helps me <span className="font-normal text-charcoal-mute">(one per line)</span>
            </span>
            <textarea
              className="field min-h-[90px] resize-none"
              placeholder={'Step outside\nText my sister\nCold water on my face'}
              value={plan.copingStrategies.join('\n')}
              onChange={(e) => setList('copingStrategies', e.target.value)}
            />
          </label>
        </div>

        <div className="glass-card p-5">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-sm font-medium text-charcoal-soft dark:text-cream/70">People I can reach</span>
            <button
              className="btn-ghost"
              onClick={() => update({ contacts: [...plan.contacts, { name: '', relationship: '', phone: '' }] })}
            >
              Add person
            </button>
          </div>
          <div className="space-y-2">
            {plan.contacts.length === 0 && (
              <p className="text-sm text-charcoal-mute dark:text-cream/50">No one added yet.</p>
            )}
            {plan.contacts.map((c, i) => (
              <div key={i} className="grid grid-cols-1 gap-2 sm:grid-cols-3">
                <input
                  className="field"
                  placeholder="Name"
                  value={c.name}
                  onChange={(e) => updateContact(i, { name: e.target.value })}
                />
                <input
                  className="field"
                  placeholder="Relationship"
                  value={c.relationship}
                  onChange={(e) => updateContact(i, { relationship: e.target.value })}
                />
                <input
                  className="field"
                  placeholder="Phone"
                  value={c.phone}
                  onChange={(e) => updateContact(i, { phone: e.target.value })}
                />
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card p-5">
          <label className="block">
            <span className="mb-1.5 block text-sm font-medium text-charcoal-soft dark:text-cream/70">
              A note to my future self
            </span>
            <textarea
              className="field min-h-[80px] resize-none"
              placeholder="Something you'd want to hear on a hard day."
              value={plan.safeNote}
              onChange={(e) => update({ safeNote: e.target.value })}
            />
          </label>
        </div>

        <div className="flex items-center gap-3">
          <button className="btn-primary" onClick={save}>
            Save plan
          </button>
          {saved && <span className="text-sm text-sage dark:text-eucalyptus">Saved.</span>}
        </div>
      </div>
    </div>
  );
}
