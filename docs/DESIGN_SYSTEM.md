# Hearth Design System (Earthenware & Vellum)

_Last updated: 2026-07-02_

Hearth is the "warm corner of your computer." The UI must be highly accessible (100% WCAG compliance), legible, tactile, and distinctively physical. It must **not** look like a generic tech dashboard.

This document outlines the core principles defined by the Hearth Design Council.

## Core Philosophy

1. **Physical Materiality:** Interfaces should evoke tangible objects (paper, ledger books, ceramic) rather than digital constructs (glass, floating neon).
2. **Accessible by Default:** High contrast, explicit focus rings, large touch targets, and ARIA-compliant markup.
3. **Restorative over Stimulating:** Animations are critically damped. Colors are warm and grounded.

## Typography

- **Display (Headings & Dates):** `Fraunces` (Serif). Used for establishing a grounded, slightly editorial, book-like feel.
- **Body (UI & Reading):** `Atkinson Hyperlegible` (Sans-serif). Specifically chosen for exceptional readability and distinct character shapes, minimizing cognitive load for users with ADHD or dyslexia.

## The Palette (Semantic Variables)

We do not use raw Tailwind colors in our components. We use our mapped semantic CSS variables defined in `src/renderer/styles/index.css`.

### Backgrounds & Surfaces
- `bg-base-bg`: The deep base canvas.
- `surface-card`: The standard container. Unlike typical cards, this has no drop shadow and uses a subtle 1px inner border (`border-base-border`).
- **Banned:** `glass-card`, frosted glass, or generic bento-box layouts.

### Text
- `text-text-primary`: High contrast, main readability text.
- `text-text-muted`: Accessible muted text. Never so light that it fails WCAG AAA contrast ratios.

### Semantic Actions
- `brand` (Sage/Eucalyptus): The primary interactive color.
- `semantic-error` (Ember): Used exclusively for destructive actions or the 988 Crisis lifeline.
- `semantic-warning` (Lavender): Used for cautionary patterns.
- `semantic-success` (Deep Green): Used to reinforce positive momentum (e.g., anxiety dropping in the ERP tracker).

## Component Standards

### Ledgers over Cards
For lists of items (Tasks, Meds, ER), we prefer the "Continuous Ledger" layout over disjointed cards. Items are separated by a bottom border (`border-b border-base-border`) and highlight subtly on hover. This reduces visual noise and cognitive load.

### Focus Rings
All interactive elements (`button`, `input`, `textarea`, `a`) must have an explicit focus ring for keyboard navigation:
`focus-visible:ring-2 focus-visible:ring-brand focus-visible:ring-offset-2 focus:outline-none`

### Toggle Switches
We use a custom, accessible switch pattern (`role="switch"`, `aria-checked`, `aria-label`). Do not rely on generic checkboxes for immediate-action settings.

## Motion

We use `framer-motion` for transitions, utilizing physics-based springs instead of CSS easings. 
- All springs must be **critically damped** (no bounce) to prevent triggering vestibular sensitivity or motion sickness.
- See `src/renderer/lib/motion.ts` for standard variants.
