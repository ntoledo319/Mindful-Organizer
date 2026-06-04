# Audit 09 — The Design System

**Surface:** the systemic visual language underneath *every* screen — the token model, the type scale, the color/theme engine, spacing rhythm, the component library, iconography, and motion.
**Source read:** `src/gui/themes.py` (the `Theme` dataclass + `ThemeManager.generate_stylesheet`), `src/gui/components/` (`buttons.py`, `card.py`, `containers.py`, `progress.py`, `typography.py`, `__init__.py`).
**Screenshots read:** `/tmp/hearth_ui/dashboard.png`, `mood_tracker.png`, `settings.png`, `crisis.png`.
**Verdict on the GENERIC → DISTINCTIVE scale:** the system sits at **GENERIC**, and worse, it is *misnamed* as distinctive. The file header calls these themes "highly polished, distinctive, condition-aware" and the dataclass docstring promises "behavioral tokens for premium UI." Neither claim is true in the rendered product. This is the layer that makes all eight other surfaces feel "bare-bones beta," because a design system is a force multiplier in *both* directions: a strong one lifts every screen, and this one flattens every screen into the same gray box.

---

## What this surface is

A design system is the genetic code of the product. Every screen the founder called "dogshit" is dogshit *for the same reasons*, and those reasons live here: in `themes.py` (the 600-line QSS generator that paints the entire app) and in `src/gui/components/` (the six tiny widgets that are supposed to be the shared vocabulary).

The job this layer must do:

1. **Encode Hearth's identity once, so every surface inherits it for free.** Type, color, spacing, elevation, motion, and iconography should be defined in one place with a point of view, and every widget should pull from it. Get this right and the dashboard, the mood tracker, and crisis all *feel like the same hand made them*.
2. **Carry the central product thesis — "your computer adapts to your psychology" — into the visual layer.** This is the "behavioral tokens" promise. The UI is supposed to change density, brightness, and tone with the user's state. That mechanism, if it existed, would be the single most distinctive thing about Hearth. No competitor has it.
3. **Replace native OS widgets with a custom Hearth vocabulary.** A mental-health refuge cannot be assembled from the same `QCalendarWidget` and `QCheckBox` grid that ships in every accounting tool.

The user's state when they "reach" this surface is *every* state, on *every* screen, because the system is omnipresent. That is exactly why its failures compound: a 0.5px contrast miss in one token fails AA on twenty screens at once.

---

## Why it fails — forensically

### Information architecture of the system — tokens that lie

The `Theme` dataclass (`themes.py:9-36`) advertises four "behavioral" tokens: `layout_density`, `animation_speed_ms`, `border_radius`, and `chrome_visibility`. I traced every one of them through the codebase:

- `chrome_visibility` (`themes.py:36`) — set to `"reduced"` only on the Quiet theme (`themes.py:168`). **Consumed nowhere.** `grep` finds exactly one definition and zero readers outside the dataclass. It is a string that does nothing.
- `condition_suitability` (`themes.py:32`) — feeds `get_recommended_themes()` (`themes.py:218`), which is called by the onboarding/settings theme picker. This one is real but trivial: it sorts a dropdown. It does not change a single pixel of how a screen behaves for an anxious vs. hypomanic user.
- `animation_speed_ms` (`themes.py:34`) — defined per theme (250ms, 0ms for Quiet). **Consumed nowhere.** There is no animation system to read it. The only motion in the entire app is the breathing circle's `QTimer` (`breathing_widget.py:119`), which ignores this token entirely.
- `layout_density` and `border_radius` — these *are* read, but only inside `generate_stylesheet()` (`themes.py:249`), where they are **baked into a static QSS string at generation time**. That means they're frozen the moment the theme is applied. They are theme constants, not behavioral tokens. Nothing recomputes them when the user's state changes.

**Principle violated:** a token must do something, and a "behavioral token" must respond to behavior. These respond to nothing. The system *claims* the product's entire differentiator in its own docstrings and then never builds it. This is the worst possible failure for a taste audit, because the gap between the promise ("condition-aware, behavioral") and the delivery (a static stylesheet keyed off a theme name) is precisely the gap the founder feels as "beta." The architecture is honest in only one place: `to_dict()` (`themes.py:56-65`) literally ships "Compatibility aliases used by older widgets while they migrate." The system is documenting its own half-finished migration in production.

### The two parallel styling systems — the deepest structural rot

There are **two completely independent styling engines** fighting each other, and the result is that no two widgets are guaranteed to look alike.

1. **The global QSS engine** (`generate_stylesheet`, `themes.py:230-599`) styles bare Qt selectors: `QPushButton`, `QFrame[class="card"]`, `QCheckBox`, `QCalendarWidget`, etc. Apply this and a generic `QFrame` with `class="card"` gets `border-radius: radius*1.5` and `padding: 24px` (`themes.py:508-513`).

2. **The component library** in `src/gui/components/` styles widgets with **per-instance inline `setStyleSheet` calls** that re-implement the same primitives with *different* values. `CardFrame` (`card.py:34-42`) sets `border-radius: 6px` and `padding: 16px` by default — **a different radius and padding than the QSS `card` class.** So a `CardFrame` and a `QFrame[class="card"]` on the same screen are visibly different shapes. The dashboard uses `CardFrame` (6px radius); a `QGroupBox` next to it uses `radius` from the theme (12px). They cannot agree on what a "container" looks like.

It gets worse. The component library reads tokens by **legacy alias names that the main engine only provides through a compatibility shim**:
- `buttons.py:36` reads `bg_key` defaulting to `"accent"` but `_ThemedButton` defaults `hover_key="secondary"` (`buttons.py:18`) — `"secondary"` is not a real token; it's an alias for `text_muted` (`themes.py:58`). So a button's *hover state defaults to muted-gray text-color as a background.* That's a bug encoded into the base class.
- `card.py:35` reads `"card_bg"` (an alias, `themes.py:59`), not `surface`.
- `containers.py:46` falls back to `"#f5f5f5"` — a **light-gray hardcode** — if no theme is passed. On the Onyx dark theme, any unthemed `ScrollContainer` flashes light gray.
- `progress.py:27` and `typography.py:57` read `"secondary"` (alias). `typography.py`'s `BodyLabel` hardcodes `font-size: 13px` (`typography.py:58`) and `Caption` hardcodes 11px (`typography.py:74`) — **completely bypassing `font_scale`** from `themes.py:238`. A user who drags the accessibility font slider to 1.5x (visible in `settings.png`) gets larger headers from the QSS engine and **unchanged 13px body text** from the components, because the components never heard about the slider.

**Principle violated:** single source of truth. There are at least three competing sources — the QSS string, the inline component styles, and hardcoded fallbacks — and they disagree on radius, padding, font-size, and which token name is canonical. *This is the mechanical reason the app looks inconsistent screen to screen.* It is not a taste problem first; it is an architecture problem that produces a taste problem.

### Typography — there is no type system, and the serif promised in the brief never ships

The entire app renders in one font stack: `"SF Pro Text", "Inter", "Segoe UI", "Helvetica Neue", sans-serif` (`themes.py:247`). That is the literal Tailwind/Linear/Vercel default sans, which `CLAUDE.md` bans by name ("the Tailwind default look (Inter…)"). The aesthetic profile calls for a serif with warmth for anything the user reads; **the type stack contains no serif at all.** Every word in Hearth — the greeting, the journal, the crisis hotline — is set in the same neutral UI sans that ships in every SaaS dashboard.

The "scale" is five raw pixel values computed inline in `generate_stylesheet` (`themes.py:238-242`): `small=12`, `base=14`, `large=16`, `xlarge=20`, `header=26`. Problems:

- **It is not a scale, it is five magic numbers.** 12 → 14 → 16 → 20 → 26 has no ratio, no rhythm. There is no defined line-height anywhere in the QSS (Qt defaults are used), so vertical rhythm is accidental.
- **The component library ignores the scale entirely** and hardcodes its own sizes (13px body, 11px caption, 13px section title in `typography.py`). So the app has *two* type scales that don't share a single value — 14/16/20/26 in QSS, 11/13 in components.
- **`letter-spacing: -0.5px` on headers** (`themes.py:322`) is the generic "tighten the big text" move every modern UI kit does. It is SAFE-GOOD at best and says nothing about Hearth.

**Principle violated:** typography is voice. A refuge that wants to feel like "a quiet, attentive companion" speaks here in the exact font of a project-management tool. Swap test passes trivially: paste this type system into Notion, Linear, or any Qt admin panel and nobody would notice.

### Color / contrast — warm names, cold delivery, failing AA

The palette has genuinely nice *intentions*. `onyx` accent `#D9A05B` is a warm hearthlight amber; `alabaster` accent `#426B52` is a calm forest green. But:

- **`text_muted` (`#8E8E93`) on `surface` (`#18181A`) measures ~4.0:1** — under the WCAG AA 4.5:1 floor. And `text_muted` is where almost all *content* lives, because `BodyLabel` and `Caption` default to the `"secondary"` alias (`typography.py:57`, `83`), which maps to `text_muted` (`themes.py:58`). **The system's default body-text color fails AA across the whole app.** For an audience reading at 2am with brightness down, this is not a rounding error.
- **The `quiet` "accessibility" theme uses `success="#00FF00"` and `accent="#FFD400"` on pure black** (`themes.py:153-155`). Pure `#00FF00` green is the canonical "I have no design system" color; it is eye-searing and, for an anxiety/PTSD audience, the opposite of calming. A high-contrast theme can be built from desaturated, calm high-contrast pairs; this one reaches for traffic-light primaries.
- **The `shadow` token is defined on every theme (`themes.py:91`, etc.) and used by nothing.** `grep` confirms zero `QGraphicsDropShadowEffect` and zero reads of `shadow` in any widget. So every "card" is a flat 1px-border box with no elevation. The depth language of the system is: there is no depth.
- **Color-blind overrides exist** (`themes.py:172-191`) and are genuinely thoughtful — but they only swap four semantic colors; they don't fix the 4.0:1 muted-text problem, which affects color-blind and fully-sighted users alike.

**Principle violated:** "every visual choice serves meaning" and "make crisis access instant/legible." The warmest, most meaningful color (`accent`) is spent almost entirely on upsell CTAs and the active nav pill (visible in all four screenshots), while the content that the fragile user actually needs to read is rendered in sub-AA gray.

### Spacing / density — a `layout_density` knob that touches almost nothing

`layout_density` is multiplied into ~10 padding values in the QSS (`themes.py:287, 334, 380`, etc.). But:

- **It is applied unevenly.** Button padding scales with density; card padding (`24px`, `themes.py:512`) does not. List-item padding scales; `QGroupBox` padding (`24px 16px 16px 16px`, `themes.py:520`) does not. So "compact mode" would shrink buttons while leaving cards full-size — an incoherent density model.
- **The component library's padding is hardcoded** (`CardFrame` 16px, `card.py:18`) and never sees `layout_density` at all.
- There is no spacing *scale* (4/8/12/16/24…). Margins and paddings are scattered literals: `padding: 4px 6px 12px 6px` (`themes.py:274`), `margin: 16px 8px` (`themes.py:280`), `margin-bottom: 4px` (`themes.py:429`). No rhythm, so screens feel arbitrarily loose in some places and cramped in others — the exact "dense forms" complaint, encoded in the tokens.

### The actual widgets — native-Qt tells are the *default*, not the exception

The system's core failure of taste is that **it styles native Qt widgets instead of replacing them.** The QSS lovingly themes `QCalendarWidget` (`themes.py:555-581`), `QSpinBox` (`themes.py:500`), `QCheckBox` (`themes.py:484`), `QSlider` (`themes.py:466`), `QListWidget` (`themes.py:418`). Painting a dark coat on an OS calendar does not make it a Hearth calendar — it makes it a *dark OS calendar*. The mood tracker proves it (`mood_tracker.py`): a raw `QCalendarWidget` (line 136), a raw `QTimeEdit` (line 155), a raw `QSlider` (line 171), a **28-checkbox `QCheckBox` grid** (lines 257, 313), a raw `QListWidget` (line 325), and — the smoking gun — a `QLabel("Mood Chart (matplotlib integration)")` placeholder shipped to users (`mood_tracker.py:368`, visible in `mood_tracker.png`). The system provides no charting primitive, no custom selector, no calm calendar, so every screen falls back to OS chrome.

The six "components" that *do* exist are not a system; they are six thin `setStyleSheet` wrappers (`buttons.py`, `card.py`, `progress.py`, `typography.py` are ~40-90 lines each). There is:
- **No icon system** — zero icons anywhere in the app (every screenshot is text-only; nav items are bare words).
- **No custom-painted component** except the breathing circle, which lives off in `breathing_widget.py` and shares no paint code with anything.
- **No elevation/shadow component**, no chip/tag, no segmented control, no toast, no skeleton/loading state, no empty-state component.

**Specificity test, applied to the whole library:** could `CardFrame`, `AccentButton`, `ThemedProgressBar`, `SectionTitle` exist unchanged in any Qt CRUD app? **Yes, all of them.** → The entire component library is wrong by the project's own standard.

### Interaction & feedback — states defined, depth absent

Hover/pressed/checked/disabled states *are* defined in the QSS (e.g. `themes.py:340-351`), which is more than nothing. But:

- **Feedback is purely color-swap.** No scale, no shadow lift, no transition — because Qt QSS has no transition property and the app has no `QPropertyAnimation` layer to fake it. Every state change is an instantaneous color jump. For an anxious user, instant hard cuts read as "snappy/jittery"; gentle eases read as "calm." The system has no mechanism for the latter.
- **The component buttons (`buttons.py`) re-declare hover styles that conflict with the QSS** (two sources again), so a `GhostButton` (`buttons.py:91-98`) and a QSS-styled `QPushButton` animate-feel differently on the same screen.

### Motion — the token exists; the system does not

`animation_speed_ms` is defined per theme and `reduced_motion` is a real setting wired through `main_window.py:197`. But **there is no motion system to honor either.** No `QPropertyAnimation`, no `QGraphicsOpacityEffect` transitions, no eased state changes anywhere in `src/gui/` except the standalone breathing timer. So the most calming tool a fragile-state UI has — soft, slow motion — is entirely absent from the system. The product that promises to "dim the lights when you're drained" cannot fade anything.

### Empty / loading / error states — not modeled at all

The system provides **no empty-state, loading, or error primitive.** The consequence is visible everywhere: the mood analytics panel shows `7-day average: --`, `30-day trend: --`, `Mood volatility: --` (`mood_tracker.png`) and the literal `(matplotlib integration)` placeholder. Crisis shows raw "No personal contacts added yet. Use Edit to add." (`crisis.png`). These are dev placeholders leaking to users because the design system never defined what *absence* looks like in Hearth. **Principle violated:** every state is a designed state. The system designed exactly one (the happy path) and let the OS/dev-stub handle the rest.

### Accessibility — partial credit, systemic gaps

Credit where due: `font_scale`, `dyslexia_font` (OpenDyslexic, `themes.py:245`), `color_blind_mode`, and `reduced_motion` are all real, wired tokens. That is genuinely above-average intent. But the execution undercuts it:
- `font_scale` is read by the QSS engine but **ignored by the entire component library** (hardcoded px), so dragging the font slider scales headings and not body text.
- `reduced_motion` is plumbed to a setting that controls nothing (no motion exists to reduce).
- Default body contrast fails AA, as shown above — the most basic a11y obligation, missed in the most-used token pairing.

### Where it lands: GENERIC

Run the specificity test on the system as a whole: *every* token name, the type stack, the flat-card language, the native-widget reliance, and the component API could be lifted into any PyQt6 app without modification. The only things with a Hearth fingerprint are (a) the *names* of the accent colors and (b) the *aspiration* in the docstrings. Aspiration is not taste. **GENERIC.**

---

## The reimagination

If Hearth designed its system from first principles — for a person in a fragile state, around its one true differentiator — here is what it becomes.

### 1. Make "behavioral tokens" *real*: the State Engine

This is the whole ballgame. Today `layout_density`/`animation_speed`/`chrome_visibility` are dead strings. Promote them to a live **`HearthState`** that sits *above* the theme and modulates it at runtime.

- Introduce a `HearthState` object with a small set of axes the product already senses or can infer: `arousal` (calm ↔ activated), `energy` (drained ↔ wired), and `clarity` (foggy ↔ sharp). Source it from mood entries, time of day, panic logs, and focus sessions.
- The system exposes a single function `resolve_tokens(theme, state) -> ResolvedTokens`. This is where density, brightness, motion-speed, and chrome actually get computed *per render*, not baked once. High arousal → fewer elements shown (`chrome_visibility="minimal"` finally does something: it hides secondary cards), warmer/dimmer background, slower eases (longer `animation_speed_ms`), larger touch targets, shorter copy. Drained energy → lower brightness, bigger type, single-action layouts.
- **Qt mechanism:** keep `generate_stylesheet()` but make it take `(theme, resolved_tokens)`. Re-run it on a state change and call `app.setStyleSheet(...)`, OR — better for smoothness — drive the continuous parts (background luminance, accent warmth, surface elevation) through `QPropertyAnimation` on a custom `QObject` holding `pyqtProperty` color/float values, with widgets binding to them. Discrete structure changes (show/hide secondary cards) toggle widget visibility.

**This single move converts the product's central lie into its signature truth.** It is the one thing no competitor (Headspace, Notion, any tracker) can copy, because they don't live in the OS layer sensing your state.

### 2. One token source, one component vocabulary

- **Kill the dual styling system.** Delete the inline `setStyleSheet` bodies in `card.py`, `buttons.py`, `progress.py`, `typography.py`. Every component should set an `objectName`/dynamic property and inherit from the single QSS engine, so there is exactly one definition of "what a card is."
- **Kill the alias shim** (`themes.py:56-65`). Migrate widgets to canonical token names (`surface`, `text_muted`) and remove `secondary`/`card_bg`/`hover`. The shim is the seam where the two systems leak into each other.
- **Define a real spacing scale** (`space-1=4 … space-6=32`) and a **typographic scale with a ratio** (e.g. 1.25 minor-third: 13/16/20/25/31) *with explicit line-heights*, exposed as tokens, consumed by both QSS and any remaining component code. `font_scale` multiplies the scale in *one* place.

### 3. A Hearth type voice (the serif finally arrives)

Adopt a two-font system the brief already asked for: a **warm, slightly literary serif** for everything the *user reads as language* (greetings, journal, suggestions, crisis copy) and a **quiet humanist sans** for *controls and labels* (buttons, nav, field labels, numbers). Bundle the fonts (don't rely on `SF Pro`/`Inter` being present). The contrast of serif-content against sans-chrome is instantly un-SaaS and instantly Hearth: it reads as "a letter someone wrote you," not "a dashboard."

- **Qt mechanism:** `QFontDatabase.addApplicationFont()` at startup for the bundled `.otf`s; set the serif on a `[role="reading"]` dynamic property in QSS, sans on `[role="control"]`.

### 4. Custom components that replace OS chrome

Build the small set of painted primitives that let every screen stop falling back to native Qt:

- **`HearthCard`** — a `QFrame` subclass with a real `paintEvent` (`QPainter`) drawing a soft inner-warmth gradient toward the accent at very low opacity and a true soft shadow via `QGraphicsDropShadowEffect` (the `shadow` token finally lives). Elevation = importance. The one true next action sits on the most-elevated, warmest card; everything else recedes.
- **`HearthCalendar`** — a custom month grid that replaces `QCalendarWidget`, drawn with `QPainter`, where each day is a small *warmth dot* whose color encodes that day's mood/energy at a glance (a personal heat-map, not an OS date-picker). This is also the **mood "chart"** — kill the matplotlib placeholder entirely; the calendar *is* the visualization.
- **`StateSlider`** — replaces the raw `QSlider`; a custom-painted track whose fill color shifts along the warmth ramp as you drag (drained-blue → settled-amber), with the value label rendered as a *word* ("Okay," "Bad") not a number, eased on change.
- **`Pill` / `SymptomToken`** — replaces the 28-checkbox grid with tappable, painted pills that fill with a calm tint when selected, grouped and progressively disclosed (show 6, "more…"), so the wall of checkboxes becomes a calm, low-count surface.
- **An icon set** — a single line-weight, soft-cornered custom icon family (SVG → `QIcon`), warm-toned, used sparingly in nav and section headers. The absence of any iconography is part of why everything reads as "bare."

### 5. A motion layer

Introduce `hearth.motion`: a thin wrapper over `QPropertyAnimation` with named eases (`settle`, `breathe`, `lift`) and durations driven by `resolved_tokens.animation_speed_ms` (so `reduced_motion` and the State Engine both finally do something). Every state change — card appear, value change, nav switch, brightness shift — routes through it. Default ease is slow and soft; nothing in Hearth should *snap*.

### 6. Empty / loading / error as first-class system states

Define three primitives — `HearthEmpty`, `HearthLoading` (a slow breathing pulse, not a spinner), `HearthError` (warm, non-alarming) — with a single calm copy voice. No screen is allowed to ship `--` or `(matplotlib integration)` again, because the system now *owns* what absence looks like.

### Signature moments (could only exist in Hearth)

1. **The room dims as you do.** When mood/panic data indicates the user is drained or activated, the *entire system* responds: background luminance drops a few percent, the accent warms toward ember, secondary cards fade out, type grows, motion slows — all animated over ~1.2s via the State Engine + motion layer. The user *feels* the computer lean toward them. No tracker can do this; it requires the system to own the whole surface and sense state. This is the literal "dims the lights when you're drained" promise, delivered by the design system itself.
2. **The hearthlight, not a progress bar.** Replace `ThemedProgressBar` (a generic chunk-fill) with a single custom-painted **ember** that glows warmer and brighter as a streak/goal/breath fills — the same warmth motif reused for breathing, focus sessions, and adherence. One unmistakable Hearth signal of "you're doing well," painted once, reused everywhere.

---

## Quick wins vs. deep rebuilds

**Quick wins (hours, high impact, no new architecture):**
- Fix the AA failure: stop defaulting body text to `text_muted`; make `BodyLabel`/`Caption` use `text` (or raise `text_muted` to ≥4.5:1). One change, fixes contrast app-wide.
- Make `font_scale` reach the components: remove hardcoded `13px`/`11px` in `typography.py`; pull from the scale. Fixes the broken accessibility slider everywhere at once.
- Replace the `quiet` theme's `#00FF00`/`#FFD400` with calm high-contrast pairs.
- Wire the `shadow` token to a `QGraphicsDropShadowEffect` on `CardFrame` — instant depth on every card, zero new components.
- Unify radius/padding: make `CardFrame` read the theme's `border_radius` and the QSS `card` class agree on one value. Kills the "two shapes of card" inconsistency.
- Delete the `(matplotlib integration)` and `--` placeholders; replace with a one-line calm empty state.

**Deep rebuilds (the real work, in order):**
1. **Collapse to one styling source** (kill inline component styles + the alias shim). Everything else depends on this.
2. **Define real scales** (spacing + type-with-line-height) and the **two-font serif/sans voice**.
3. **Build the custom painted primitives** (`HearthCard`, `HearthCalendar`, `StateSlider`, `Pill`, icon set) to evict native Qt chrome.
4. **Build the motion layer** over `QPropertyAnimation`.
5. **Build the State Engine** (`HearthState` → `resolve_tokens` → animated re-style) — the differentiator. This is last only because it stands on 1-4; it is *first* in importance.
