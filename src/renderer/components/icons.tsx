import type { SVGProps } from 'react';

// A small, hand-picked stroke-icon set. Hearth uses thin 1.6px strokes and
// round caps everywhere — softer than the usual sharp UI iconography, to match
// the "quiet companion" feel rather than a productivity dashboard.
type P = SVGProps<SVGSVGElement>;
const base = (props: P) => ({
  width: 20,
  height: 20,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.6,
  strokeLinecap: 'round' as const,
  strokeLinejoin: 'round' as const,
  ...props,
});

export const HearthMark = (props: P) => (
  <svg {...base(props)}>
    <path d="M4 11.5 12 4l8 7.5" />
    <path d="M6 10.5V20h12v-9.5" />
    <path d="M10 20v-4.5a2 2 0 0 1 4 0V20" />
    <circle cx="12" cy="12.5" r="0.6" fill="currentColor" stroke="none" />
  </svg>
);
export const HomeIcon = (props: P) => (
  <svg {...base(props)}><path d="M4 11.5 12 4l8 7.5" /><path d="M6 10.5V20h12v-9.5" /></svg>
);
export const TaskIcon = (props: P) => (
  <svg {...base(props)}><path d="M4 7h11M4 12h11M4 17h7" /><path d="m18 6 1.5 1.5L22 5" /></svg>
);
export const MoodIcon = (props: P) => (
  <svg {...base(props)}><circle cx="12" cy="12" r="8.5" /><path d="M8.5 14a4 4 0 0 0 7 0" /><circle cx="9" cy="10" r=".6" fill="currentColor" stroke="none" /><circle cx="15" cy="10" r=".6" fill="currentColor" stroke="none" /></svg>
);
export const MoonIcon = (props: P) => (
  <svg {...base(props)}><path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5Z" /></svg>
);
export const LeafIcon = (props: P) => (
  <svg {...base(props)}><path d="M5 19c0-7 5-13 14-13 0 9-6 14-14 13Z" /><path d="M5 19c3-3 6-5 9-6.5" /></svg>
);
export const BookIcon = (props: P) => (
  <svg {...base(props)}><path d="M5 5.5A2 2 0 0 1 7 4h12v15H7a2 2 0 0 0-2 2Z" /><path d="M5 5.5V19" /></svg>
);
export const ShieldIcon = (props: P) => (
  <svg {...base(props)}><path d="M12 3.5 19 6v5.5c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6Z" /><path d="m9 12 2 2 4-4" /></svg>
);
export const ChartIcon = (props: P) => (
  <svg {...base(props)}><path d="M4 20V4" /><path d="M4 20h16" /><path d="M8 16l3.5-4 3 2.5L20 8" /></svg>
);
export const PlusIcon = (props: P) => (
  <svg {...base(props)}><path d="M12 5v14M5 12h14" /></svg>
);
export const SunIcon = (props: P) => (
  <svg {...base(props)}><circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" /></svg>
);
export const CheckIcon = (props: P) => (
  <svg {...base(props)}><path d="m5 12 4.5 4.5L19 7" /></svg>
);
export const TrashIcon = (props: P) => (
  <svg {...base(props)}><path d="M4 7h16M9 7V5h6v2M6 7l1 13h10l1-13" /></svg>
);
export const GearIcon = (props: P) => (
  <svg {...base(props)}><circle cx="12" cy="12" r="3" /><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8" /></svg>
);
