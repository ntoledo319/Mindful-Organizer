# Audit 01 — Onboarding / First Run

**Surface cluster:** `onboarding-firstrun`
**Screenshots:** `onboarding.png`, `onboarding_1.png`, `onboarding_2.png`, `onboarding_3.png` (note: all four files are byte-identical — only the welcome page was ever captured)
**Source:** `src/gui/widgets/onboarding.py`, invoked from `src/gui/main_window.py::_show_onboarding` (line 507)

---

## What this surface is

This is the first thing a human sees. Before any task, any theme, any feature — this six-page `QDialog` wizard is the entire relationship. It collects: name, conditions (ADHD / Anxiety / Depression / OCD / PTSD / Bipolar), therapy approaches (CBT / DBT / ACT / Mindfulness / ERP), and a theme, then writes a `Profile`.

**The user's state when they reach it:** They just installed a desktop app *because* their current tools track but don't act. They are, by definition, someone managing a mental-health condition — possibly drained, possibly anxious, possibly opening this at 2am because nothing else has worked. They are deciding, in the first ten seconds, whether to trust this thing with the most sensitive disclosure a person can make to software: "I have PTSD. I have bipolar."

**The job it must do:** Earn that disclosure. Make the act of telling Hearth your conditions feel like the *first time the computer adapts to you* — not like filling out a clipboard at a clinic. The IA promise on the welcome screen ("a desktop organiser that adapts to your needs") must be demonstrated *during onboarding itself*, not merely described.

It fails this job comprehensively, and the failure begins before a single word is read.

---

## Why it fails — forensically

### 0. The fatal one: the theme is never applied to the dialog

This is not a taste nitpick; it is a broken contract. In `main_window.py::_show_onboarding`, the wizard runs `wizard.exec()` **before** `_initialize_ui()`. The theme QSS (`ThemeManager.generate_stylesheet`) is applied during UI initialization, which happens *after* onboarding returns. And `OnboardingWizard.__init__` never calls `setStyleSheet` on itself.

**Result:** the entire wizard renders in the raw OS palette. On macOS that is the light-gray `#ECECEC` window you see in the screenshot, with the system-blue, aqua-rounded native **Next** button bottom-right. The progress dots are hard-coded to `#4a90d9` blue (line 215) and `#27ae60` green (line 217) — colors that exist *nowhere* in `themes.py`. The accent color of every Hearth theme is warm amber (`#D9A05B` Onyx, `#426B52` Alabaster). The very first pixels a user sees are a different brand than the app they downloaded.

**Principle violated:** *The first impression is the product's only chance to set the emotional contract* (CLAUDE.md: "breaks the promise before the app even starts"). An app whose entire thesis is "your computer adapts to you" opens with a screen that adapts to *no one* — it's the macOS default. This lands at pure **GENERIC**: this exact dialog could front any Qt app on earth.

### 1. Information architecture — a medical intake form wearing a wizard's coat

Six linear pages, each holding one decontextualized question: Welcome → Name → Conditions → Therapy → Theme → Summary. This is the structure of a *signup funnel*, not a *meeting*. Problems:

- **Conditions and Therapy are split across two pages** (lines 390, 419) even though for this user they are one thought ("here's what I'm dealing with and how I work on it"). Splitting them doubles the screens of self-disclosure and makes the intake feel longer and more clinical.
- **Theme selection (page 5) is buried after the medical questions** and presented as an abstract dropdown — yet `ThemeManager.get_recommended_themes(conditions)` (themes.py line 218) *already exists* and can recommend a theme from the conditions just collected. The data to make onboarding adaptive is sitting right there, unused. The app could say "Because you mentioned anxiety, I've set a calmer, lower-contrast room for you" — instead it shows a generic combobox.
- **The Summary page (page 6) is a receipt**, not a moment. It reprints `Name: … Conditions: … Therapy types: … Theme: …` as plain text lines (line 534). It confirms data entry; it does not confirm a relationship.

**Principle violated:** IA should mirror the user's mental model and minimize disclosure friction. This IA mirrors a database schema (`name`, `conditions[]`, `therapy_types[]`, `theme`) — you can literally read the four `self._data` keys (line 147) off the screen flow.

### 2. Visual hierarchy — a centered void

The welcome page is one centered column floating in a sea of dead gray, vertically centered between two `addStretch()` calls (lines 348, 369). There is no anchor, no warmth, no object for the eye to rest on. The title "Hearth" is 20px bold (line 49) — barely larger than the 14px tagline beneath it. For a *brand reveal*, the wordmark has almost no presence. The three text blocks (title, italic tagline, two-paragraph description) have nearly equal weight, so the eye doesn't know what matters. **Principle violated:** hierarchy must rank importance; here everything whispers at the same volume into an empty room.

### 3. Typography — `Segoe UI`, hard-coded, on macOS

Every label hard-codes `QFont("Segoe UI", …)` (lines 42, 49, 383, 459). Segoe UI is the *Windows* system font and **does not exist on macOS** — so the OS silently falls back to Helvetica/.AppleSystemUIFont. The app's own stylesheet declares a proper stack (`"SF Pro Text", "Inter", "Segoe UI"…`, themes.py line 247), but the wizard ignores it and pins a single Windows font. Result: inconsistent rendering across platforms and zero typographic personality. There is one weight relationship (bold title / regular body) and one italic flourish on the tagline (line 357) — the exact "sans-serif heading + slightly lighter sans-serif body with zero personality" pattern the CLAUDE.md Anti-Pattern Registry explicitly bans.

### 4. Color & contrast — borrowed, off-brand, and accidentally cold

The palette here is: OS light gray (unstyled), `#4a90d9` blue dots, `#27ae60` green dots, `#ccc` inactive dots, system-blue Next button. **None of these are Hearth colors.** This is the single biggest tell that nobody owns this screen. The amber-and-paper warmth that defines Hearth (the literal *hearthlight*) is completely absent. The screen reads cold, corporate, and generic — the precise three adjectives the brand says it must never be ("a wellness app, corporate mindfulness software").

### 5. Spacing & density — fine here, hostile two screens later

The welcome page is *too* sparse (a tiny paragraph adrift in gray). But the real density crime is the Conditions page (line 390): six `QGroupBox` widgets stacked vertically, each with a checkable title and a multi-line clinical paragraph ("Attention Deficit Hyperactivity Disorder — difficulty with focus, impulse control, and executive function…"). On a 750×650 dialog this overflows; the user faces a wall of six dense diagnostic blurbs they must read and toggle. For a drained or anxious user this is exactly the "wall of checkboxes" the mental-health UX lens flags as hostile.

### 6. The actual widgets — native-Qt tells everywhere

This screen is a catalog of raw Qt:

- **`QGroupBox.setCheckable(True)`** (lines 405, 433) abused as a selection card. The clickable checkbox is then *hidden* (`cb.setVisible(False)`, line 412) and a shadow `QCheckBox` is kept in sync purely so `_collect_page_data` has something to read. This is a hack — the selectable surface is a framed group box with a tiny native checkbox in its title, which is unintuitive and looks like a settings panel, not a choice.
- **`QComboBox` for theme** (line 458): a native dropdown for what should be the most sensory, emotional choice in the whole flow ("what should this room feel like?"). A combobox is how you pick a timezone.
- **The native Next button**: because no QSS reaches the dialog, the `_accent_button` helper (line 54) produces a bare `QPushButton` that the OS renders in full aqua. It isn't even accent-colored — the helper is named "accent" but applies no accent (no `setProperty("class","accent")`, no stylesheet).
- **`QFrame` theme preview** (line 478): a 100px rectangle that just shows a background color with an accent border. It "previews" a theme by showing two colors out of sixteen tokens — it tells the user almost nothing about how the app will actually feel.

**Principle violated:** "raw unstyled native OS widgets" is a banned anti-pattern. This screen is *built entirely from them.*

### 7. Interaction & feedback — a Skip button that lies, and silent failure

- **The Skip button calls `_go_next` (line 199), not a real skip.** It advances one page; it is identical in behavior to Next. A user who clicks "Skip" expecting to bypass disclosure just… goes to the next disclosure. That is a small betrayal on the most trust-sensitive screen in the app.
- **The progress dots turn green for "completed"** (line 217) — gamified validation styling on a flow where there are no right answers. Marking "I disclosed my PTSD" with a green check treats self-disclosure like a completed task. Wrong emotional register.
- **Profile creation can fail silently.** `_finish` (line 256) wraps profile creation in a broad `try/except` that only `logger.error`s on failure (line 318), then falls back, then *still* emits `onboarding_completed`. If the import path is wrong (and it imports from `profiles.…` and `gui.themes` with bare module paths that have bitten this repo before per the commit log), the user sails to the main app with a broken/empty profile and no idea anything failed. There is no validation, no "are you sure", no confirmation that their disclosure landed.

### 8. Motion — none

`QStackedWidget.setCurrentIndex` (line 210) is an instantaneous hard cut between pages. No transition, no easing, no breath. For an audience the brand promises to treat like "a quiet, attentive companion," the navigation is abrupt and mechanical. The themes define `animation_speed_ms` tokens (themes.py line 34) that go entirely unused here. **Principle violated:** motion is tone; the absence of motion reads as indifference.

### 9. Empty / loading / error states — undesigned

- **Empty:** If a user selects no conditions, the Summary prints "Conditions: None selected" (line 537) — a flat, slightly judgmental null. No graceful path for "I'd rather not say."
- **Error:** As above, swallowed into a log.
- **Loading:** N/A, but the abrupt theme-swap when the real app appears *after* the dialog closes will be a jarring flash from light-gray dialog → dark Onyx app. The user's first transition in Hearth is a color whiplash.

### 10. Copy — run the swap test

> "A quieter system for daily care and practical focus"
> "A desktop organiser that adapts to your needs based on your mental health conditions, therapy approach, and personal preferences."
> "This short setup will personalise your experience. You can change any of these settings later."

Run the CLAUDE.md swap test — replace "Hearth" with "Notion" or "Headspace":

- *"A quieter system for daily care and practical focus"* — works perfectly for any wellness/productivity app. **Dead copy.**
- *"A desktop organiser that adapts to your needs based on your… preferences"* — this is feature-spec prose. "personalise your experience," "change any of these settings later" is the literal house style of every SaaS onboarding ever shipped. **Dead copy.**

There is **zero point of view.** It does not say what Hearth *believes* ("your computer should adapt to your psychology, not the other way around"). It does not promise to *act* ("when anxiety spikes, I close Discord"). The word "hearth" appears only as the product name; the *idea* of a hearth — warmth, refuge, a fire someone keeps for you — is nowhere in the language. "Organiser," "system," "settings," "personalise" are the vocabulary of a tool, not a companion. (At least it avoids the banned "optimize/unlock/supercharge" words — that's the floor, not a win.)

### 11. Emotional tone for this audience — clinical when it must be tender

The Conditions page hands a person in a fragile state a stack of DSM-flavored definitions of their own diagnoses and asks them to tick boxes. *"Major Depressive Disorder or related conditions — low mood, fatigue, and loss of interest."* Telling a depressed user the textbook definition of depression, then asking them to check it, is the opposite of warmth. It is a form. The MEMORY note for this project is explicit: don't fixate on the user's deficit. This page is *built around* the deficit. The emotional contract Hearth promises — "the warm corner of the computer" — is contradicted on the exact screen where it matters most.

### 12. Accessibility

- Hard-coded font sizes/family ignore the app's `font_scale` and dyslexia-font settings (themes.py lines 238, 244) — onboarding can't honor a user's accessibility needs because it predates and bypasses the theme system.
- Progress conveyed *only* by color dots (blue/green/gray) with no text label or `aria`-equivalent — fails non-color-perception users. `#27ae60` green / `#4a90d9` blue is also not a colorblind-safe pairing, and the app *has* `COLOR_BLIND_OVERRIDES` it isn't using here.
- Selection state lives in a hidden checkbox synced to a group-box toggle — fragile for screen readers and keyboard nav.

### 13. Where it lands: **GENERIC**

The Specificity Test ("Could this element exist in any other app unchanged?") returns **yes** for every single element. The unstyled dialog, the centered welcome column, the combobox theme picker, the checkbox-grid intake, the "personalise your experience" copy — lift the whole wizard into a tax-prep app and nothing would look out of place. This is the worst possible grade for the most important screen.

---

## The reimagination

**First principle:** onboarding is not data collection. It is *the first time the room changes for you.* Every question the user answers should visibly, immediately warm the space around them — so that by the end, the user hasn't *filled out a profile*, they've *watched the computer start adapting.* That is the only onboarding that could exist in Hearth and nowhere else.

### The governing metaphor: lighting the hearth

The screen is dark from the first frame (we open directly in the user's eventual theme — Onyx by default, never the OS gray). At the center, low and warm, is a single ember: a small, softly pulsing amber glow (custom-painted `QWidget`, `QRadialGradient`, animated via `QPropertyAnimation` on a `glow` property). **As the user makes each disclosure, the fire grows.** Pick conditions → the light steadies into the hue best suited to you. Name yourself → the fire is "yours." By the final screen the dark room is warmly lit. The progress indicator *is* the fire, not a row of dots.

This is the signature: **the behavioral-token system runs live during onboarding.** Hearth's whole thesis (UI adapts to state) is *demonstrated*, not described.

### New IA — three acts, not six pages

1. **Arrival ("Sit down")** — the ember, the wordmark, one sentence with a point of view, one warm button. ~10 seconds.
2. **Tending ("Tell the fire what it's keeping")** — name + conditions + therapy as *one* continuous, low-pressure scene (merging the current pages 1–4). Conditions are warm word-chips, not clinical group boxes. Selecting one quietly shifts the room's temperature in real time.
3. **Settling ("Your corner")** — not a receipt. A one-line, human reflection of what Hearth now knows and what it will *do* about it, with the theme already chosen *for* the user (overridable). The fire is fully lit. One button: **"Take me in."**

### Layout & hierarchy

- Full-bleed dark canvas. The ember is the lowest, warmest, brightest object — the natural eye anchor (fixes the centered-void problem by giving the eye a literal hearth to look at).
- Wordmark large and confident (a real display weight, e.g. a warm serif or a custom-letterspaced mark), set against the dark — a brand *reveal*, not a 20px label.
- Conditions as a soft-wrapped cluster of **chips** (custom `QWidget`, rounded, amber-tinted when selected, low-contrast outline when not), not a vertical stack of framed paragraphs. Selected chips drift toward the fire. The clinical definitions move into an optional, quiet "what's this?" affordance — *available*, never *forced in your face.*

### Signature interactions

1. **The room warms as you choose.** Selecting "Anxiety" triggers a sub-second `QPropertyAnimation` that nudges the background and accent toward the calmer Slate/Onyx end and lowers contrast a touch; selecting "ADHD" steadies the ember and tightens spacing slightly. Driven by the *existing* `get_recommended_themes(conditions)` and `layout_density`/`chrome_visibility` tokens already in `themes.py` (lines 33, 36, 218). The user *sees* the adaptation happen.
2. **The fire is the progress bar.** A custom-painted ember that grows in radius/brightness per act (`QPropertyAnimation` on a float property, repainted in `paintEvent` with `QRadialGradient`). Replaces the off-brand colored dots entirely. Accessible: paired with a quiet text label ("Tending — 2 of 3").
3. **Page transitions = a slow cross-dissolve**, not a hard cut. Wrap `QStackedWidget` swaps in a `QGraphicsOpacityEffect` + `QPropertyAnimation` (~250ms, honoring `animation_speed_ms`, set to 0 under reduced-motion). Tone of a companion, not a slideshow.

### Adaptive ("behavioral token") behavior — concrete

- On condition selection, call `ThemeManager.get_recommended_themes(conditions)`; set `current_theme_name` to the top match and *re-apply the stylesheet live* so the wizard itself shifts. (This also fixes Failure #0 for free: the dialog is now always themed, because the wizard is the first consumer of `generate_stylesheet()`.)
- Settle screen pre-selects that theme with copy that *names the reasoning*: "You mentioned anxiety, so I've set us up in **Slate** — cooler, calmer, less to look at. You can change the room anytime."
- Density and chrome follow the same tokens, so a user who selects ADHD lands in a slightly tighter, higher-signal layout and an anxiety user lands in a softer, sparser one — *from the very first screen.*

### Copy voice — beliefs, not features

Rewrite to pass the swap test (none of these survive being moved to a competitor):

- Arrival headline: **"Pull up a chair."** Sub: **"Most apps watch how you're doing. Hearth does something about it — it dims the screen when you're spent, guards your focus, and quiets the noise when things get loud. Let's set up your corner."**
- Tending prompt (replacing "Select any conditions that apply"): **"What is Hearth keeping watch over?"** — followed by the chips. Optional reveal copy stays plain-language and non-diagnostic ("On hard days, Hearth leans toward fewer choices and a gentler pace.").
- Therapy prompt: **"Working with anything in particular?"** (chips: CBT, DBT, ACT, ERP, Mindfulness — "or none, that's fine").
- A genuine skip: **"I'll tell you later"** — and it must actually skip the act, landing in a sensible default room, not advance one page.
- Settle: **"Your corner's lit."** + the adaptive-theme sentence above + **"Take me in."**

Never the words: "personalise," "experience," "settings," "organiser," "optimize." Always present that Hearth will *act*.

### Specific Qt mechanisms (buildable today)

- **Ember widget:** subclass `QWidget`, override `paintEvent`, draw a `QRadialGradient`; expose `glow`/`size` as `pyqtProperty(float)` and animate via `QPropertyAnimation` + a looping `QSequentialAnimationGroup` for the idle pulse.
- **Condition chips:** custom `QAbstractButton` (checkable), painted rounded rect with amber fill on `isChecked()`; lay out in a `QHBoxLayout` that wraps (or a small flow-layout helper).
- **Live theming:** on selection, mutate `ThemeManager`, call `app.setStyleSheet(theme_manager.generate_stylesheet())`, animate the background `QColor` via `QVariantAnimation` for a smooth temperature shift rather than a flash.
- **Transitions:** `QGraphicsOpacityEffect` on each page + `QPropertyAnimation(b"opacity")`, gated by `reduced_motion`.
- **Fix the invocation order:** in `_show_onboarding`, apply the theme stylesheet to the wizard before `exec()` (or let the wizard apply it in `__init__`) so the OS gray *never* shows for even one frame.

### Two signature moments that could ONLY exist in Hearth

1. **"The room warms."** The instant the user taps their first condition chip, the entire window breathes into a new temperature tuned to *them* — measurably, visibly. No other onboarding adapts its own appearance to your disclosure *as you make it.* This is the product's thesis, performed in the first 30 seconds.
2. **The lit hearth handoff.** When the user taps "Take me in," the ember doesn't just disappear into a hard cut to the app. It expands and resolves into the main window's warm header glow — a continuous light, so the transition from onboarding into Hearth feels like *carrying a flame into the next room*, not closing a dialog. (Animate the ember's radius/position to map onto the app header, then fade in the main UI underneath.) This single move erases the current "light-gray dialog → dark app whiplash" and replaces it with the most on-brand transition imaginable.

---

## Quick wins vs. deep rebuilds

### Quick wins (hours, high impact)
- **Apply the theme stylesheet to the wizard before `exec()`.** Kills the #1 failure (OS-gray first impression) immediately. One-line fix in `_show_onboarding` plus a `setStyleSheet` in `__init__`.
- **Delete the hard-coded `#4a90d9` / `#27ae60` / `#ccc` dot colors**; drive them from theme tokens (amber accent for current, muted for done/upcoming). Stop using green-check "completed" styling on disclosure.
- **Remove the `Segoe UI` hard-codes**; let labels inherit the QSS font stack (or set the proper SF Pro/Inter stack).
- **Rewrite the copy** (welcome, condition/therapy prompts, summary) to the belief-driven voice above. Pure text change, zero engineering risk.
- **Make Skip actually skip**, and surface profile-creation failure instead of swallowing it (`_finish`).
- **Merge Conditions + Therapy** onto one screen and demote the clinical definitions into an optional "what's this?" reveal.

### Deep rebuilds (the real work)
- **The ember**: custom-painted, animated hearthlight as the through-line and progress indicator.
- **Condition chips** replacing the `QGroupBox`/hidden-checkbox hack.
- **Live behavioral-token theming**: room warms/adapts on selection via `get_recommended_themes`, density and chrome tokens applied from the first screen.
- **Motion system**: cross-dissolve page transitions and the "carry the flame into the next room" handoff into the main window.
- **Three-act restructure** of the IA (Arrival → Tending → Settling) replacing the six-page funnel.

---

## Summary

The onboarding wizard fails before its first word: it runs `exec()` before the theme is ever applied (`_show_onboarding`) and hard-codes its own off-brand colors and Windows-only `Segoe UI`, so a person who downloaded "the warm corner of the computer" is greeted by a flat macOS-gray dialog with a system-blue Next button — a different brand than the app, scoring pure **GENERIC** on the most trust-critical screen there is. Beneath that, it's a clinical intake form in disguise: six linear pages, conditions presented as DSM-style paragraphs with checkboxes, a combobox for the one emotional choice (theme), and feature-spec copy ("personalise your experience," "desktop organiser") that survives a swap with any competitor and therefore says nothing. The single most important redesign move is to **make onboarding the first live demonstration of Hearth's thesis: the room must visibly warm and adapt to the user as they disclose** — open directly in a dark, themed canvas around a single animated ember (the hearthlight, doubling as the progress indicator), and the instant the user taps their first condition chip, re-theme the window live via the already-existing `get_recommended_themes`/density/chrome tokens so they *watch the computer adapt to them* in the first 30 seconds. Do that and onboarding stops being a form and becomes the moment the user decides to trust Hearth.
