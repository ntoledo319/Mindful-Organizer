import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../lib/api';
import { useStore } from '../state/store';
import { DEFAULT_DAILY_SPOONS } from '@shared/spoons';
import { HearthMark } from '../components/icons';
import { InlineError } from '../components/ui';

// Three quiet steps: welcome, optional name, and explicit local-data consent.
// No account, diagnosis selector, email, or paywall is involved.

export function Onboarding() {
  const { settings, saveSettings } = useStore();
  const [step, setStep] = useState(() => (settings?.onboarded ? 2 : 0));
  const [hero, setHero] = useState<string | null>(null);
  const [name, setName] = useState(() => settings?.displayName ?? '');
  const [privacyAcknowledged, setPrivacyAcknowledged] = useState(false);
  const [isFinishing, setIsFinishing] = useState(false);
  const [finishError, setFinishError] = useState(false);

  useEffect(() => {
    void api.heroDataUrl().then(setHero).catch(() => setHero(null));
  }, []);

  const finish = async () => {
    setIsFinishing(true);
    setFinishError(false);
    try {
      await saveSettings({
        displayName: name.trim(),
        onboarded: true,
        dailySpoons: settings?.dailySpoons ?? DEFAULT_DAILY_SPOONS,
        privacyConsentAt: new Date().toISOString(),
      });
    } catch {
      setFinishError(true);
      setIsFinishing(false);
    }
  };

  return (
    <div className="flex h-full min-h-0 overflow-hidden bg-base-bg dark:bg-night-bg">
      <div className="app-drag relative hidden h-full w-1/2 flex-col justify-end overflow-hidden md:flex">
        {hero ? (
          <img src={hero} alt="" className="absolute inset-0 h-full w-full object-cover" />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-night-surface via-brand to-semantic-warning" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/20 to-transparent" />
        <div className="relative z-10 p-10 text-white">
          <p className="font-display text-2xl font-medium leading-snug drop-shadow">
            The warm corner of your computer.
          </p>
          <p className="mt-2 max-w-xs text-sm text-white/90 drop-shadow">
            A desktop that dims when you're drained and protects your focus like it's yours.
          </p>
        </div>
      </div>

      <div className="flex min-h-0 flex-1 overflow-y-auto px-6 sm:px-10">
        <div className="my-auto w-full max-w-sm py-8">
          <div className="mb-8 flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-soft bg-brand text-white shadow-hearth dark:bg-night-brand dark:text-night-bg">
              <HearthMark width={20} height={20} />
            </span>
            <span className="font-display text-xl font-semibold tracking-tight text-text-primary dark:text-night-text">
              Hearth
            </span>
          </div>

          {step === 0 && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
              <h1 className="font-display text-3xl font-semibold leading-tight text-text-primary dark:text-night-text">
                Plan around the energy you have today.
              </h1>
              <p className="text-sm leading-relaxed text-text-muted dark:text-night-muted">
                Choose a daily budget, give tasks an energy cost, and see what realistically fits.
                Check-ins add local context without changing the capacity you set. There is no
                account, record sync, analytics, or telemetry.
              </p>
              <button className="btn-primary" onClick={() => setStep(1)}>
                Begin
              </button>
            </motion.div>
          )}

          {step === 1 && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
              <h1 className="font-display text-2xl font-semibold text-text-primary dark:text-night-text">
                What should Hearth call you?
              </h1>
              <input
                autoFocus
                className="field"
                placeholder="A name or nothing at all"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && setStep(2)}
              />
              <div className="flex gap-2">
                <button className="btn-ghost" onClick={() => setStep(0)}>
                  Back
                </button>
                <button className="btn-primary" onClick={() => setStep(2)}>
                  Continue
                </button>
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-brand dark:text-night-brand">Before you add or change personal entries</p>
                <h1 className="font-display text-2xl font-semibold text-text-primary dark:text-night-text">
                  Your entries stay local and encrypted at rest.
                </h1>
                <p className="mt-2 text-sm leading-relaxed text-text-muted dark:text-night-muted">
                  Hearth stores the name, tasks, mood, sleep, journal, practice, ERP, diary,
                  medication-reference, and crisis-plan details you choose to enter. The database is encrypted with
                  AES-256-GCM, and its key is protected by your operating-system sign-in. Hearth has no account,
                  record sync, analytics, or telemetry and does not upload these entries.
                </p>
                <p className="mt-2 text-sm leading-relaxed text-text-muted dark:text-night-muted">
                  Settings lets you export a readable copy or destroy every record, encrypted rollback snapshot,
                  and the key that decrypts them before Hearth creates a fresh empty store. A JSON or PDF you export
                  is not encrypted by Hearth after you choose its location.
                </p>
              </div>
              <label className="flex cursor-pointer items-start gap-3 rounded-soft border border-base-border bg-base-surface p-4 dark:border-night-border dark:bg-night-surface">
                <input
                  type="checkbox"
                  className="mt-1 h-4 w-4 accent-brand focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 dark:accent-night-brand dark:focus-visible:ring-night-brand dark:focus-visible:ring-offset-night-bg"
                  checked={privacyAcknowledged}
                  onChange={(event) => setPrivacyAcknowledged(event.target.checked)}
                />
                <span className="text-sm leading-relaxed text-text-primary dark:text-night-text">
                  I understand these data practices and consent to Hearth storing the information I choose to enter
                  in its encrypted local database.
                </span>
              </label>
              <p className="text-xs leading-relaxed text-text-muted dark:text-night-muted">
                Hearth is a personal reflection tool, not a medical device or a substitute for professional care.
              </p>
              <a
                href="https://github.com/ntoledo319/Mindful-Organizer/blob/main/docs/PRIVACY.md"
                target="_blank"
                rel="noreferrer"
                className="inline-flex rounded-soft text-sm font-medium text-brand underline decoration-brand/40 underline-offset-4 hover:decoration-brand focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 dark:text-night-brand dark:focus-visible:ring-night-brand dark:focus-visible:ring-offset-night-bg"
              >
                Read the full privacy policy (opens in your browser)
              </a>
              {finishError && <InlineError>Hearth could not save these choices. Try again.</InlineError>}
              <div className="flex gap-2">
                {!settings?.onboarded && (
                  <button className="btn-ghost" onClick={() => setStep(1)}>
                    Back
                  </button>
                )}
                <button className="btn-primary" onClick={() => void finish()} disabled={!privacyAcknowledged || isFinishing}>
                  {isFinishing ? 'Saving…' : settings?.onboarded ? 'Continue to Hearth' : 'Light the hearth'}
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
