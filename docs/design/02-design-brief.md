# Hearth — Design Brief

**Phase 1 · Task 26 · Status: draft 1**
**Depends on:** `01-references.md`
**Feeds into:** `03-information-architecture.md`, `tailwind.config.ts` in `hearth-frontend/`

This document is the *source of truth* for every visual decision in Hearth. If a screen contradicts this brief, the screen is wrong. If the brief contradicts what makes a screen great, the brief gets a versioned amendment — not a quiet exception.

---

## I. The five principles

These are the load-bearing decisions. Everything else is downstream.

### 1. Warm dark by default, never cold

The default theme is **Ember** — a warm, brown-tinted dark surface with cream text. Pure black is rejected (cold, clinical). Bluish dark (Material Design default) is rejected (cold, dated). The reference is the inside of a wooden cabin at night with one lamp on, not a server room.

### 2. Single accent, used as scarce resource

One brand color: a warm coral-orange (`#D97049` in Ember). It appears on at most one element per screen — the current selection, the active button, the next-action affordance. If two accents appear on a screen, one of them is wrong.

Status colors (success, warning, danger, info) are *not* accents; they are signals, used only when conveying state.

### 3. Real typography, not Inter

Inter is the most-used typeface in software in 2026. Using it identifies Hearth as one-of-many. The default UI typeface is **Söhne** (Klim Type Foundry); the editorial typeface for journal and diary card content is **Tiempos Text** (Klim). Combined license: ~$350 one-time, well within scope for a v1 product. Free fallback during development: **Inter** for UI, **Lora** for editorial.

### 4. Density without chrome

Chrome (sidebars, toolbars, status bars) is dense and quiet. Content (journal, diary card, reading views) is generously spaced. The reference: Linear's chrome density + Bear's content density, in the same product.

### 5. Motion is sub-200ms or it's absent

No motion above 200ms in functional UI. The one exception: the "magic paper" transform when expanding a task or mood entry into its detail view, which earns ~400ms because it's *spatially functional* (shows the user where the detail came from). Idle decorative animations are banned.

---

## II. Color system

### Ember — warm dark (default)

| Token | Hex | Use |
|---|---|---|
| `bg.base` | `#18130F` | Window background |
| `bg.raised` | `#221C16` | Sidebar, cards, panels |
| `bg.floating` | `#2B231C` | Modals, command palette, tooltips |
| `bg.hover` | `#2F2620` | Hover state on interactive surfaces |
| `bg.active` | `#382C24` | Pressed/active state |
| `border.subtle` | `#3D3128` | Quiet dividers between content blocks |
| `border.default` | `#4F4135` | Default border on inputs, cards |
| `border.strong` | `#6B5848` | Focused inputs, strong dividers |
| `text.primary` | `#F2E8D9` | Body text, headings |
| `text.secondary` | `#BCAE9C` | Supporting text, captions |
| `text.tertiary` | `#8C7E6C` | Metadata, timestamps, helper text |
| `text.placeholder` | `#5F5347` | Input placeholders |
| `accent` | `#A8845F` | Brand color — aged brass (kettle on the hearth) |
| `accent.hover` | `#B89472` | Hover state on accent surfaces |
| `accent.muted` | `#6B5841` | Subdued accent (selected row left-stripe, etc.) |
| `success` | `#95B776` | Completion, success states |
| `warning` | `#E5B16C` | Caution, draft, pending |
| `danger` | `#C66860` | Destructive actions, errors |
| `info` | `#7C9CB8` | Informational tags, neutral state |

### Linen — warm light

| Token | Hex | Use |
|---|---|---|
| `bg.base` | `#F7F2EA` | Window background — parchment |
| `bg.raised` | `#FFFFFF` | Cards, panels on linen |
| `bg.floating` | `#FAF6EE` | Modals, tooltips |
| `bg.hover` | `#EFE8DC` | Hover state |
| `bg.active` | `#E8DFD0` | Pressed state |
| `border.subtle` | `#E8DFD0` | Quiet dividers |
| `border.default` | `#D4C7B2` | Default borders |
| `border.strong` | `#A8957B` | Focused inputs |
| `text.primary` | `#2D2520` | Body text |
| `text.secondary` | `#6B5E50` | Supporting text |
| `text.tertiary` | `#9C8E7E` | Metadata |
| `text.placeholder` | `#B5A695` | Placeholders |
| `accent` | `#7D5E3F` | Brand color — darker aged brass for contrast on linen |
| `accent.hover` | `#6B4E32` | Hover |
| `accent.muted` | `#D4C5AC` | Subdued accent |
| `success` | `#5F8A47` | Success |
| `warning` | `#B8842E` | Warning |
| `danger` | `#A04A42` | Destructive |
| `info` | `#476E8C` | Informational |

### Quiet — accessibility-tuned high contrast

Used during crisis mode and for users with low vision. Maximum contrast, single accent, no aesthetic flourish.

| Token | Hex | Use |
|---|---|---|
| `bg.base` | `#000000` | Window background |
| `bg.raised` | `#0A0A0A` | Cards |
| `border.default` | `#FFFFFF` | All borders |
| `text.primary` | `#FFFFFF` | All text |
| `text.secondary` | `#D4D4D4` | Supporting |
| `accent` | `#FFD400` | Single action color — high-contrast amber |
| `danger` | `#FF4040` | Crisis action |

**Theme count at v1.0: three.** The current codebase has eight themes; we are intentionally cutting to three excellent ones rather than shipping eight mediocre ones. Additional themes ship post-launch as Bear-style theme packs.

---

## III. Typography

### Type stack

```css
/* UI surfaces: chrome, buttons, navigation, lists */
font-family-ui: "Söhne", -apple-system, "SF Pro Text", system-ui, sans-serif;

/* Editorial surfaces: journal, diary card, crisis plan, daily briefing */
font-family-editorial: "Tiempos Text", "Lora", Georgia, serif;

/* Monospaced: code, timestamps, numerical data */
font-family-mono: "Söhne Mono", "JetBrains Mono", "SF Mono", Menlo, monospace;
```

**Why two faces:** Söhne for chrome reads as precise and modern. Tiempos for editorial content reads as *thinking*, not *interface*. The transition between the two — when a user clicks into the journal — is a deliberate handoff from "you are navigating an app" to "you are thinking on paper."

**Why not Inter:** every productivity app ships Inter. Using it places Hearth in the visual peer group of every other Notion-clone. Söhne is used by Stripe, Shopify, and others — distinguishing without being obscure.

### Type scale

**Chrome scale (UI surfaces)** — three sizes only.

| Token | Size | Line height | Weight | Use |
|---|---|---|---|---|
| `text.meta` | 11px | 14px | 400 | Timestamps, metadata, sidebar items |
| `text.body` | 13px | 18px | 400 | Default body text, button labels, list items |
| `text.title` | 17px | 22px | 600 | Page titles, modal headings |

**Editorial scale (content surfaces)** — for journal, diary card, crisis plan, daily briefing.

| Token | Size | Line height | Weight | Use |
|---|---|---|---|---|
| `editorial.body` | 16px | 26px | 400 | Default reading/writing text |
| `editorial.large` | 18px | 30px | 400 | Crisis plan body, important entries |
| `editorial.title` | 24px | 32px | 500 | Section titles in editorial views |
| `editorial.display` | 32px | 40px | 500 | Day headers in journal, crisis-mode message |

**Numerical scale** — Söhne Mono with tabular-num features enabled.

| Token | Size | Use |
|---|---|---|
| `num.small` | 13px | Counters, badges |
| `num.medium` | 22px | Dashboard metrics |
| `num.large` | 48px | Mood score display, timer countdown |

### Weight rules

- **Regular (400)** — default body
- **Medium (500)** — actionable text (button labels, links, navigation items, table headers)
- **Semibold (600)** — page titles, modal headings
- **Bold (700)** — banned in UI chrome. Allowed only in editorial display for emphasis within long-form text.

**Italic** — allowed only in editorial content (Tiempos Italic). Banned in UI chrome.

---

## IV. Spacing

8pt grid. Spacing tokens are the only values that should appear in margin/padding declarations.

| Token | Pixels |
|---|---|
| `space.0` | 0 |
| `space.0.5` | 2 |
| `space.1` | 4 |
| `space.2` | 8 |
| `space.3` | 12 |
| `space.4` | 16 |
| `space.5` | 20 |
| `space.6` | 24 |
| `space.8` | 32 |
| `space.10` | 40 |
| `space.12` | 48 |
| `space.16` | 64 |
| `space.20` | 80 |
| `space.24` | 96 |

**Density rules:**
- Chrome (sidebar items, list rows): `space.2` to `space.3` vertical padding. Tight, scannable.
- Cards, panels: `space.4` to `space.5` internal padding.
- Editorial views: `space.6` to `space.8` between paragraphs, `space.12` between sections.
- Content column max-width: **640px** for editorial reading/writing flows. Wider columns kill reading rhythm.

**Touch targets:** minimum 36px for any interactive element. Buttons default to 36px height. List rows can be 32px in chrome contexts (the user is hunting with the mouse, not tapping).

---

## V. Motion

### Duration tokens

Per the aesthetic profile: *transitions feel like turning a page, not swiping a tile.* Durations are slower than typical SaaS, and easing is always pure ease-out — never spring, never overshoot, never bounce.

| Token | Duration | Use |
|---|---|---|
| `motion.micro` | 120ms | Hover reveal, focus ring, color change on interactive surface |
| `motion.short` | 220ms | State changes, toggles, button presses, sidebar item highlight |
| `motion.standard` | 320ms | Modal open/close, page transition, command palette appearance |
| `motion.editorial` | 520ms | Page-turn transform — entry expanding into detail view. Used **sparingly** — at most one place per screen. |

### Easing curves

| Token | Bezier | Use |
|---|---|---|
| `ease.out` | `cubic-bezier(0.2, 0, 0, 1)` | Default for everything — element settling into its final state |
| `ease.in-out` | `cubic-bezier(0.4, 0, 0.2, 1)` | When an element transitions through two states (rare) |
| `ease.exit` | `cubic-bezier(0.4, 0, 1, 1)` | Element leaving the screen — accelerates as it goes |

**Removed:** any easing curve with `y > 1.0` (overshoot / bounce). The aesthetic profile explicitly bans bouncy motion.

### Motion rules

- **No idle animation.** If nothing is happening, nothing moves. No looping spinners on the dashboard. No subtle pulse on the brand logo.
- **No skeleton loaders longer than 200ms.** If data fetches faster than 200ms, show nothing. If it might fetch slower, prefetch.
- **No staggered list-item animations.** Lists appear instantly. Animating each row's entrance is a tell of slow apps.
- **`prefers-reduced-motion` cuts all motion to 0ms.** Quiet theme automatically activates reduced motion regardless of OS setting.

---

## VI. Iconography

**Library:** `lucide-react` (consistent stroke weight, MIT licensed, exhaustive coverage).

**Stroke weight:** 1.5px default. Never the default `lucide-react` 2px (heavier than Söhne's letterforms — visual mismatch).

**Icon size:** 16px for inline UI, 20px for primary navigation, 24px for empty states.

**Rules:**
- Icons accompany labels in primary navigation. Icon-only navigation is banned.
- Icons in tertiary positions (sidebar items, list rows) can stand alone.
- Custom illustrations are banned at v1. Lucide only. (The references demonstrate that custom illustrations are mostly a Calm/Headspace tell.)

---

## VII. Voice and copy

These are extracted from `docs/brand-strategy-and-positioning.md` and codified for UI text.

### Voice rules

| Context | Tone | Example |
|---|---|---|
| In-app instructions | Direct, minimal | *"Discord will close in 30 seconds. Cancel to keep it open."* |
| Crisis intervention | Calm, operational | *"Your screen is dimming. Your crisis plan is one click away."* |
| Error states | Non-judgmental, specific | *"Rule didn't fire — Telegram is not running."* |
| Empty states | Quiet, informative | *"No mood entries yet. The first one becomes your baseline."* |
| Onboarding | Plain, respectful | *"Which conditions are you managing? This changes what Hearth watches for."* |

### Banned words and patterns

**From the aesthetic profile** (canonical):
- *"journey"* — anywhere, ever
- *"we"* used as the app (*"we thought you'd like…"*, *"how are we feeling today?"*)
- *"friend"*, *"buddy"*, *"family"* used about the user
- *"let's…"* as a softener
- *"grab"* (*"grab a few minutes"*) and *"quick"* (*"a quick check-in"*) as softeners

**From earlier in the brief:**
- *"Hey there!"*, exclamation points in chrome, em-dash-heavy "playful" copy
- *"Unlock, supercharge, transform, elevate, level up, take to the next level"*
- *"Whether you're a [persona A] or [persona B]..."* construction
- *"Find your..."* headline pattern
- *"Optimize"* (the word; per project identity)
- Streak celebrations: *"🎉 7-day streak!"* and equivalents
- Anthropomorphic UI: *"Hearth thinks you should..."*, *"I'm here for you..."*
- Apologies in chrome: *"Sorry, something went wrong"* → *"Couldn't reach the agent. Retrying."*
- Emoji in any default UI copy

### Permitted patterns

- Direct second-person: *"Your day starts at 7:14am."*
- Imperative: *"Pick a focus duration."*
- Quiet declaratives: *"Sleep was 6h 12m. Below your 7h baseline."*
- Em-dashes for parenthetical clarification (sparingly)

---

## VIII. Layout patterns

### Primary chrome — sidebar, not tabs

The current PyQt6 product uses a horizontal tab bar. The redesign uses a **vertical sidebar** on the left:

- Sidebar width: 220px on desktop, collapsible to 56px (icon-only)
- Top section: app brand mark + global search/Cmd+K trigger
- Middle: primary navigation (Dashboard, Journal, Diary Card, Automation, Sleep, Medication, Focus, Crisis)
- Bottom section: profile switcher + settings gear

Reasoning: tabs across the top scale poorly past 6-8 items. Hearth has 12+ primary surfaces. Sidebar is the Things 3 / Linear / Notion answer.

### Content area — single column with optional inspector

Most screens are a single content column (max 800px wide) flowing down the page. Some screens add a right-side inspector panel (collapsible, 320px wide) for detail/edit views.

**No three-column layouts.** They're an attempt to look "rich" that always reads as Bootstrap admin.

### Command palette — Cmd+K from anywhere

Triggered by Cmd+K on Mac, Ctrl+K on Win/Linux. Floats centered with vibrancy/blur background. Searches across:
- Quick actions ("Start focus session", "Log mood", "Open crisis plan")
- Navigation ("Go to journal", "Go to automation rules")
- Entry search ("Find journal entries about anxiety")
- Settings ("Switch theme to Linen")

This is Hearth's *primary navigation system* for power users.

### Crisis mode — full-screen takeover

Triggered by Cmd+Shift+C or by the system automation detecting crisis signals. Replaces the entire UI with Quiet theme, displays the crisis plan, and presents three large buttons: *Call 988*, *Text Crisis Line*, *Show me what to do right now*. No other navigation visible. Single Escape to return.

This is the *one* place where Hearth UI changes radically based on state — and the change is functional, not stylistic.

---

## IX. Tailwind config (translation)

When `hearth-frontend/tailwind.config.ts` is generated, every token above maps directly to it. Pseudo-config:

```typescript
export default {
  theme: {
    extend: {
      colors: {
        bg: {
          base: "var(--hearth-bg-base)",
          raised: "var(--hearth-bg-raised)",
          floating: "var(--hearth-bg-floating)",
          hover: "var(--hearth-bg-hover)",
          active: "var(--hearth-bg-active)",
        },
        border: {
          subtle: "var(--hearth-border-subtle)",
          DEFAULT: "var(--hearth-border-default)",
          strong: "var(--hearth-border-strong)",
        },
        text: {
          primary: "var(--hearth-text-primary)",
          secondary: "var(--hearth-text-secondary)",
          tertiary: "var(--hearth-text-tertiary)",
          placeholder: "var(--hearth-text-placeholder)",
        },
        accent: {
          DEFAULT: "var(--hearth-accent)",
          hover: "var(--hearth-accent-hover)",
          muted: "var(--hearth-accent-muted)",
        },
        success: "var(--hearth-success)",
        warning: "var(--hearth-warning)",
        danger: "var(--hearth-danger)",
        info: "var(--hearth-info)",
      },
      fontFamily: {
        ui: ["Söhne", "-apple-system", "SF Pro Text", "system-ui", "sans-serif"],
        editorial: ["Tiempos Text", "Lora", "Georgia", "serif"],
        mono: ["Söhne Mono", "JetBrains Mono", "SF Mono", "Menlo", "monospace"],
      },
      fontSize: {
        meta: ["11px", { lineHeight: "14px", fontWeight: "400" }],
        body: ["13px", { lineHeight: "18px", fontWeight: "400" }],
        title: ["17px", { lineHeight: "22px", fontWeight: "600" }],
        "editorial-body": ["16px", { lineHeight: "26px", fontWeight: "400" }],
        "editorial-large": ["18px", { lineHeight: "30px", fontWeight: "400" }],
        "editorial-title": ["24px", { lineHeight: "32px", fontWeight: "500" }],
        "editorial-display": ["32px", { lineHeight: "40px", fontWeight: "500" }],
      },
      spacing: {
        "0.5": "2px",
        "1": "4px",
        "2": "8px",
        "3": "12px",
        "4": "16px",
        "5": "20px",
        "6": "24px",
        "8": "32px",
        "10": "40px",
        "12": "48px",
        "16": "64px",
        "20": "80px",
        "24": "96px",
      },
      transitionDuration: {
        micro: "80ms",
        short: "150ms",
        standard: "200ms",
        expressive: "400ms",
      },
      transitionTimingFunction: {
        exit: "cubic-bezier(0.4, 0, 1, 1)",
        enter: "cubic-bezier(0, 0, 0.2, 1)",
        "in-out": "cubic-bezier(0.4, 0, 0.2, 1)",
        expressive: "cubic-bezier(0.34, 1.56, 0.64, 1)",
      },
    },
  },
};
```

CSS variables flip per theme via a `[data-theme="ember"|"linen"|"quiet"]` attribute on `<html>`.

---

## X. Open decisions to resolve in Phase 1 task 27 (IA)

These are downstream questions that the IA spec answers, not the brief:

1. **Sidebar item order and grouping.** Suggested ordering: `Dashboard / Journal / Diary Card | Focus / Automation | Sleep / Medication | Crisis` with horizontal-rule separators between groups. To confirm in IA.
2. **Default screen on launch.** Currently Dashboard. Alternative: a dedicated "Today" view that's more action-oriented than the metric-tile dashboard. To decide in IA.
3. **Onboarding flow.** Current 6-page wizard is too long. To redesign in IA — likely 3 screens (welcome / conditions / first mood entry).
4. **Profile switcher placement.** Bottom of sidebar vs. command palette only. To decide in IA.
5. **System tray vs. menu bar app.** Tauri supports both; Hearth probably wants both (system tray on Windows, menu bar on Mac, AppIndicator on Linux). To spec in IA.

---

**Next:** `03-information-architecture.md` — every screen, every flow, what's primary vs progressive disclosure, the keyboard map.
