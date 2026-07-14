import { type ReactNode, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { transitionGentle } from '../lib/motion';

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="mb-8 flex items-end justify-between gap-4">
      <div>
        <h1 className="font-display text-4xl font-normal tracking-tight text-text-primary dark:text-night-text">
          {title}
        </h1>
        {subtitle && <p className="mt-2 max-w-xl text-base text-text-muted dark:text-night-text/80 leading-relaxed">{subtitle}</p>}
      </div>
      {action && <div className="app-no-drag shrink-0 pb-1">{action}</div>}
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
      transition={transitionGentle}
      className="surface-card flex flex-col items-center gap-5 px-8 py-20 text-center"
    >
      <div className="text-brand/80 dark:text-night-brand/80">{illustration}</div>
      <div className="max-w-sm space-y-2">
        <h3 className="font-display text-2xl font-medium text-text-primary dark:text-night-text">{title}</h3>
        <p className="text-base leading-relaxed text-text-muted dark:text-night-text/80">{body}</p>
      </div>
      {action && <div className="mt-2">{action}</div>}
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
  const modalRef = useRef<HTMLDivElement>(null);

  // Focus trap and Escape key handling
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      
      if (e.key === 'Tab' && modalRef.current) {
        const focusableElements = modalRef.current.querySelectorAll<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement.focus();
            e.preventDefault();
          }
        }
      }
    };

    if (open) {
      window.addEventListener('keydown', onKeyDown);
      // Prevent body scrolling
      document.body.style.overflow = 'hidden';
      // Auto-focus first element slightly after mount
      setTimeout(() => {
        const firstFocusable = modalRef.current?.querySelector<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        firstFocusable?.focus();
      }, 50);
    }
    
    return () => {
      window.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = '';
    };
  }, [open, onClose]);

  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
        >
          {/* Backdrop */}
          <div className="absolute inset-0 bg-base-bg/80 dark:bg-night-bg/90 backdrop-blur-sm transition-opacity" onClick={onClose} aria-hidden="true" />
          
          <motion.div
            ref={modalRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
            className="surface-card relative z-10 w-full max-w-lg p-7 shadow-2xl"
            initial={{ scale: 0.98, y: 15 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.98, opacity: 0 }}
            transition={transitionGentle}
          >
            <h2 id="modal-title" className="mb-5 font-display text-2xl font-medium text-text-primary dark:text-night-text">
              {title}
            </h2>
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
  tone = 'brand',
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  tone?: 'brand' | 'success' | 'warning' | 'error';
}) {
  const toneClass =
    tone === 'error' ? 'accent-semantic-error' : tone === 'warning' ? 'accent-semantic-warning' : tone === 'success' ? 'accent-semantic-success' : 'accent-brand';
  
  return (
    <label className="block">
      <div className="mb-2 flex items-center justify-between text-sm">
        <span className="font-medium text-text-primary dark:text-night-text">{label}</span>
        <span className="tabular-nums font-display text-xl font-medium text-brand dark:text-night-brand">{value}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        aria-valuemin={min}
        aria-valuemax={max}
        aria-valuenow={value}
        className={`h-2 w-full cursor-pointer appearance-none rounded-full bg-black/10 dark:bg-white/10 focus-visible:ring-2 focus-visible:ring-offset-2 focus:outline-none ${toneClass}`}
      />
    </label>
  );
}

export function Spinner() {
  return (
    <div className="flex h-full items-center justify-center py-20" role="status" aria-label="Loading">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-brand/20 border-t-brand dark:border-night-brand/20 dark:border-t-night-brand" />
      <span className="sr-only">Loading...</span>
    </div>
  );
}
