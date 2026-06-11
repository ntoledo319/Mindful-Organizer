import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../lib/api';
import { useStore } from '../state/store';
import { CONDITIONS, type Condition } from '@shared/types';
import { dailySpoonsFor } from '@shared/spoons';
import { HearthMark, CheckIcon } from '../components/icons';

// Three quiet steps: welcome (hero), who you are, what you carry. No account,
// no email, no "unlock". The copy promises one thing — that the computer will
// adapt to the person, not the other way around.

export function Onboarding() {
  const { saveSettings } = useStore();
  const [step, setStep] = useState(0);
  const [hero, setHero] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [conditions, setConditions] = useState<Condition[]>([]);

  useEffect(() => {
    void api.heroDataUrl().then(setHero);
  }, []);

  const toggle = (c: Condition) =>
    setConditions((prev) => (prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]));

  const finish = () =>
    void saveSettings({
      displayName: name.trim(),
      conditions,
      onboarded: true,
      dailySpoons: dailySpoonsFor(conditions),
    });

  return (
    <div className="flex h-full bg-cream dark:bg-night">
      <div className="app-drag relative hidden w-1/2 flex-col justify-end overflow-hidden md:flex">
        {hero ? (
          <img src={hero} alt="" className="absolute inset-0 h-full w-full object-cover" />
        ) : (
          <div className="absolute inset-0 bg-gradient-to-br from-sage via-sage-light to-eucalyptus" />
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-charcoal/55 via-transparent to-transparent" />
        <div className="relative z-10 p-10 text-cream">
          <p className="font-display text-2xl font-medium leading-snug drop-shadow">
            The warm corner of your computer.
          </p>
          <p className="mt-2 max-w-xs text-sm text-cream/80 drop-shadow">
            A desktop that dims when you're drained and protects your focus like it's yours.
          </p>
        </div>
      </div>

      <div className="flex flex-1 items-center justify-center p-10">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-sage text-cream shadow-hearth">
              <HearthMark width={20} height={20} />
            </span>
            <span className="font-display text-xl font-semibold tracking-tight text-charcoal dark:text-cream">
              Hearth
            </span>
          </div>

          {step === 0 && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
              <h1 className="font-display text-3xl font-semibold leading-tight text-charcoal dark:text-cream">
                Your computer should adapt to your psychology.
              </h1>
              <p className="text-sm leading-relaxed text-charcoal-mute dark:text-cream/55">
                Not another tracker. Hearth reads your state and reshapes the day around it —
                matching tasks to the energy you actually have, and keeping help within reach when
                things get heavy. Everything stays on this machine. No cloud, no telemetry.
              </p>
              <button className="btn-primary" onClick={() => setStep(1)}>
                Begin
              </button>
            </motion.div>
          )}

          {step === 1 && (
            <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
              <h1 className="font-display text-2xl font-semibold text-charcoal dark:text-cream">
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
                <h1 className="font-display text-2xl font-semibold text-charcoal dark:text-cream">
                  What are you carrying?
                </h1>
                <p className="mt-1 text-sm text-charcoal-mute dark:text-cream/55">
                  Pick any that fit. Hearth tunes its rhythm and the signals it watches for. You can
                  change this anytime, and skipping is fine.
                </p>
              </div>
              <div className="grid grid-cols-1 gap-2">
                {CONDITIONS.map((c) => {
                  const on = conditions.includes(c.id);
                  return (
                    <button
                      key={c.id}
                      onClick={() => toggle(c.id)}
                      className={`flex items-center justify-between rounded-2xl border px-4 py-3 text-left transition ${
                        on
                          ? 'border-sage bg-sage/10 dark:bg-sage/20'
                          : 'border-charcoal/10 hover:bg-white/60 dark:border-white/10 dark:hover:bg-white/5'
                      }`}
                    >
                      <span>
                        <span className="block text-sm font-medium text-charcoal dark:text-cream">{c.label}</span>
                        <span className="block text-xs text-charcoal-mute dark:text-cream/50">{c.blurb}</span>
                      </span>
                      {on && (
                        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-sage text-cream">
                          <CheckIcon width={13} height={13} />
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
              <div className="flex gap-2">
                <button className="btn-ghost" onClick={() => setStep(1)}>
                  Back
                </button>
                <button className="btn-primary" onClick={finish}>
                  Light the hearth
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
