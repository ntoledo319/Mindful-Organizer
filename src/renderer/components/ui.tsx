import { type ReactNode, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="mb-7 flex items-end justify-between gap-4">
      <div>
        <h1 className="font-display text-3xl font-semibold tracking-tight text-charcoal dark:text-cream">
          {title}
        </h1>
        {subtitle && <p className="mt-1 max-w-xl text-sm text-charcoal-mute dark:text-cream/50">{subtitle}</p>}
      </div>
      {action && <div className="app-no-drag shrink-0">{action}</div>}
    </div>
  );
}

export function EmptyState({
  illustration,
  title,
  body,
  action,
}: {
  illustration: ReactNode;
  title: string;
  body: string;
  action?: ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card flex flex-col items-center gap-4 px-8 py-16 text-center"
    >
      <div className="text-sage/70 dark:text-eucalyptus/70">{illustration}</div>
      <div className="max-w-sm space-y-1.5">
        <h3 className="font-display text-xl font-semibold text-charcoal dark:text-cream">{title}</h3>
        <p className="text-sm leading-relaxed text-charcoal-mute dark:text-cream/50">{body}</p>
      </div>
      {action}
    </motion.div>
  );
}

export function Modal({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    if (open) window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div className="absolute inset-0 bg-charcoal/30 backdrop-blur-sm" onClick={onClose} />
          <motion.div
            className="glass-card relative z-10 w-full max-w-lg p-6"
            initial={{ scale: 0.96, y: 10 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.97, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 280, damping: 26 }}
          >
            <h2 className="mb-4 font-display text-xl font-semibold text-charcoal dark:text-cream">{title}</h2>
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export function Scale({
  label,
  value,
  onChange,
  min = 1,
  max = 10,
  tone = 'sage',
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  tone?: 'sage' | 'lavender' | 'ember';
}) {
  const toneClass =
    tone === 'lavender' ? 'accent-lavender-deep' : tone === 'ember' ? 'accent-ember' : 'accent-sage';
  return (
    <label className="block">
      <div className="mb-1.5 flex items-center justify-between text-sm">
        <span className="font-medium text-charcoal-soft dark:text-cream/70">{label}</span>
        <span className="tabular-nums font-display text-lg font-semibold text-sage dark:text-eucalyptus">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className={`h-1.5 w-full cursor-pointer appearance-none rounded-full bg-charcoal/10 dark:bg-white/10 ${toneClass}`}
      />
    </label>
  );
}

export function Spinner() {
  return (
    <div className="flex h-full items-center justify-center py-20">
      <div className="h-7 w-7 animate-spin rounded-full border-2 border-sage/20 border-t-sage" />
    </div>
  );
}
