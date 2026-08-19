import { type ReactNode, useEffect, useId, useRef } from 'react';
import { createPortal } from 'react-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { transitionGentle } from '../lib/motion';

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="font-display text-4xl font-normal tracking-tight text-text-primary dark:text-night-text">
          {title}
        </h1>
        {subtitle && <p className="mt-2 max-w-xl text-base text-text-muted dark:text-night-muted leading-relaxed">{subtitle}</p>}
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
        <p className="text-base leading-relaxed text-text-muted dark:text-night-muted">{body}</p>
      </div>
      {action && <div className="mt-2">{action}</div>}
    </motion.div>
  );
}

export function QueryErrorState({
  title = "Ample couldn't load this view",
  body = 'Your local records are still on this device. Try loading the view again.',
  onRetry,
}: {
  title?: string;
  body?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="surface-card px-8 py-12 text-center" role="alert">
      <div className="mx-auto max-w-md space-y-3">
        <h2 className="font-display text-2xl font-medium text-text-primary dark:text-night-text">{title}</h2>
        <p className="text-base leading-relaxed text-text-muted dark:text-night-muted">{body}</p>
        {onRetry && (
          <button type="button" className="btn-primary mt-3" onClick={onRetry}>
            Try again
          </button>
        )}
      </div>
    </div>
  );
}

export function InlineError({ children }: { children: ReactNode }) {
  return (
    <p
      className="rounded-soft border border-semantic-error/30 bg-semantic-error/10 px-4 py-3 text-sm text-semantic-error dark:border-night-error/40 dark:text-night-error"
      role="alert"
    >
      {children}
    </p>
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
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const closeRef = useRef(onClose);
  const titleId = useId();
  closeRef.current = onClose;

  useEffect(() => {
    if (!open) return;

    const appShell = document.querySelector<HTMLElement>('[data-app-shell]');
    const hadInert = appShell?.hasAttribute('inert') ?? false;
    const previousAriaHidden = appShell?.getAttribute('aria-hidden') ?? null;
    const previousOverflow = document.body.style.overflow;
    previousFocusRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;

    appShell?.setAttribute('inert', '');
    appShell?.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = 'hidden';

    const focusableElements = () =>
      Array.from(
        modalRef.current?.querySelectorAll<HTMLElement>(
          'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ) ?? [],
      ).filter((element) => element.getAttribute('aria-hidden') !== 'true');

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        closeRef.current();
        return;
      }

      if (e.key === 'Tab') {
        const elements = focusableElements();
        if (elements.length === 0) {
          e.preventDefault();
          modalRef.current?.focus();
          return;
        }

        const firstElement = elements[0];
        const lastElement = elements[elements.length - 1];

        if (e.shiftKey) {
          if (document.activeElement === firstElement || !modalRef.current?.contains(document.activeElement)) {
            lastElement.focus();
            e.preventDefault();
          }
        } else if (document.activeElement === lastElement || !modalRef.current?.contains(document.activeElement)) {
          firstElement.focus();
          e.preventDefault();
        }
      }
    };

    window.addEventListener('keydown', onKeyDown);
    const focusTimer = window.setTimeout(() => {
      const firstElement = focusableElements()[0];
      if (firstElement) firstElement.focus();
      else modalRef.current?.focus();
    }, 0);

    return () => {
      window.clearTimeout(focusTimer);
      window.removeEventListener('keydown', onKeyDown);
      document.body.style.overflow = previousOverflow;
      if (!hadInert) appShell?.removeAttribute('inert');
      if (previousAriaHidden === null) appShell?.removeAttribute('aria-hidden');
      else appShell?.setAttribute('aria-hidden', previousAriaHidden);
      previousFocusRef.current?.focus();
    };
  }, [open]);

  return createPortal(
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex overflow-y-auto p-6"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.15 }}
        >
          {/* Backdrop */}
          <div className="absolute inset-0 bg-base-bg/80 backdrop-blur-sm transition-opacity dark:bg-night-bg/90" onClick={() => closeRef.current()} aria-hidden="true" />
          
          <motion.div
            ref={modalRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby={titleId}
            tabIndex={-1}
            className="surface-card relative z-10 m-auto w-full max-w-lg p-7 shadow-2xl"
            initial={{ scale: 0.98, y: 15 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.98, opacity: 0 }}
            transition={transitionGentle}
          >
            <h2 id={titleId} className="mb-5 font-display text-2xl font-medium text-text-primary dark:text-night-text">
              {title}
            </h2>
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>,
    document.body,
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
