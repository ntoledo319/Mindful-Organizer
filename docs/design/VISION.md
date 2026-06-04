# Hearth — Design Vision

**The north star. This document outranks the per-surface audits and the design system; when a build decision is in doubt, it is resolved here.** It inherits directly from `00-aesthetic-profile.md` (the immutable taste contract) and synthesizes the nine forensic audits in this folder (`audit_01`–`audit_09`).

---

## The thesis (one line)

> **Hearth is the only interface that changes shape with the person in front of it — a warm dark room that dims, quiets, and narrows itself the moment you're struggling, so the computer is finally doing something about how you feel instead of asking you to report it.**

Everything below is in service of that sentence. If a screen does not *visibly adapt* to the user's state, or does not *feel warm*, it is not yet Hearth — it is a tracker with a dark coat, which is exactly what the audits found across all nine surfaces.

The swap test for the whole product: replace "Hearth" with Headspace, Daylio, or Notion. If the interface still makes sense, it has failed. The thesis is load-bearing because Hearth lives in the OS layer and senses your state — no browser-tab competitor *can* dim the room when you go quiet. Build the things only Hearth can do.

---

## The emotional arc of using Hearth

A product for people who are sometimes in crisis must be designed as an emotional sequence, not a feature list. This is the arc every surface must serve:

1. **Arrival → being received.** You open Hearth (or it's already lit in the tray). The room is warm and dim, not bright and busy. Nothing demands a decision. The feeling is *the room was prepared for me* — the "chair test" from the aesthetic profile. (Today the dashboard fails this: an upsell banner greets you, then eight gray status cards. See `audit_02`.)

2. **Disclosure → being adapted to.** You tell Hearth something true — how you feel, that you forgot your meds, that the urge is bad tonight. The instant you do, **the room responds**: it warms, it dims, it simplifies. Disclosure is rewarded with adaptation you can *see*, never with a saved-confirmation dialog. This is the single move that makes Hearth itself. (Today disclosure is rewarded with a `QMessageBox.information("Saved")`. See `audit_03`, `audit_04`, `audit_06`.)

3. **Holding → being protected.** When you're depleted or activated, the room gets quieter on its own — fewer doors, softer light, one next action, slower motion. When you ask it to, it acts on the OS: dims the screen, closes the noisy apps, guards a focus block. You feel *held*, then *protected*. (Today this is a tabbed settings panel with Bootstrap traffic-light buttons. See `audit_07`, `audit_08`.)

4. **The worst night → a hand reaching back.** At 2am, a stranger glancing at the screen for one second can do the single right next thing: reach a human. Crisis is not a category in a list — it is the whole room turning toward you and quieting everything else. Dangerous answers route to help, never to a JSON file. (Today the crisis screen is the coldest in the app, paints the lifeline red like a delete button, and corrupts the name of the 988 hotline with a Qt mnemonic bug. See `audit_05`.)

5. **Over time → a fire someone keeps for you.** The warmth accumulates. A skipped dose is a fading ember in a warm row, not a red mark on a report card. The calendar is a personal heat-map of your days, not an OS date-picker. You return because the corner is still lit. (Today this is a permanent, ever-growing "Missed: 47, Adherence rate: 61%" failure counter. See `audit_06`.)

The arc, in five words: **received → adapted-to → held → protected → kept.**

---

## The inviolable principles

Seven principles. Each is phrased to kill a specific, named failure the audits found — so "did we follow the principle?" is a testable question, not a vibe.

### 1. The room adapts to the person; the person never configures the room.
Hearth's behavioral tokens (`layout_density`, `chrome_visibility`, `animation_speed_ms`) must do real work at *runtime*, driven by sensed state — not be baked once into a static stylesheet and forgotten.
**Kills:** the central lie in `audit_09` — three "behavioral tokens" that `grep` proves are consumed *nowhere*, while the docstring claims "condition-aware, behavioral." If a screen's density and brightness can't change in response to a mood entry, the thesis is not built.

### 2. One next action, never a menu of judgments.
Every surface surfaces exactly one obvious thing to do. Secondary actions recede (smaller, muted, no borders); they do not vanish, they subordinate.
**Kills:** the dashboard's eight stacked sections and five equal quick-action buttons (`audit_02`); the mood tracker's ~35 fields before you can express a feeling (`audit_03`); the automation screen's three equal-weight Focus/Grounding/Crisis buttons (`audit_07`).

### 3. Warmth is the work, not the decoration.
The accent — the literal hearthlight (`#D9A05B` Onyx) — touches only what is emotionally meaningful: the one next action, the act of self-care, the lifeline. Never an upsell button, never a slider track, never an "Export" button.
**Kills:** the accent spent on "Start trial" and "Add task" (`audit_02`); spent on "Export Mood Data" (`audit_03`); the crisis screen being the *coldest* screen in a product named for firelight (`audit_05`).

### 4. Disclosure is met with adaptation, never with a dialog box.
The acknowledgment that the user spoke is that *the room changed* — the light warms, the sentence rewrites in a slow crossfade, the card glows. Confirmation is in-surface and ambient. A native `QMessageBox` may never interrupt a tender act.
**Kills:** the `QMessageBox.information("Mood entry saved successfully")` after self-disclosure across mood/diary/sleep/journal/meditation/breathe/settings (`audit_03`, `audit_04`, `audit_08`); the crisis-mode response being a blocking OS alert with an OK button (`audit_07`).

### 5. Visual weight tracks human stakes.
The most important thing on a screen looks the most important. Life-or-death content (the 988 lifeline, "Reasons for Living," a self-harm answer) gets the most weight, warmth, and care. Trivial content recedes.
**Kills:** "Suicide" rendered as the least-distinguishable widget on the diary page — a tiny spinbox next to "Binge/purge" (`audit_03`); a "reset all my data" button with identical weight to a notification dropdown (`audit_08`); the empty "Personal Contacts — Use Edit to add" placeholder dominating the live crisis screen (`audit_05`).

### 6. The empty state gives; it never asks or accuses.
Absence is a designed, warm invitation — never a wall of `--`, never a dev placeholder, never a demand for data the app doesn't have, never a checklist of things the user failed to do.
**Kills:** "Values report unavailable" on the home screen (`audit_02`); "Mood Chart (matplotlib integration)" and four stacked `--` analytics (`audit_03`); "Log at least 2 entries to see insights" as the panic tracker's first words to a possibly-panicking user (`audit_05`); the medication shame-counter showing failure scaffolding with `0`/`--` in it (`audit_06`).

### 7. Crisis is reachable in one motion and arrives as quiet, not alarm.
The lifeline is one fixed gesture from anywhere, warm-amber (never delete-red), calm, and instantly legible. Dangerous answers anywhere in the app route to the crisis surface. No deterioration checklists shown during a crisis; no native modal ever interrupts a panic or an exposure.
**Kills:** Crisis buried as the 14th item in a 15-item flat list (`audit_08`); the lifeline painted with a destructive-red border and confirmed only by a vanishing tooltip (`audit_05`); a diary self-harm entry that routes to a "Saved" dialog and nowhere else — the app's one duty-of-care gap (`audit_03`).

---

## The signature ideas — what makes Hearth unmistakable

These are the elements that pass the specificity test on contact: lift any of them into a competitor and it stops making sense. They are not decoration; each is the thesis made physical. Build these and Hearth cannot be confused with anything else.

### A. Behavioral tokens, made real — the State Engine
**The differentiator. The reason the product exists. Currently a dead string in a dataclass.**

A `HearthState` object sits *above* the active theme and modulates it per render, on three axes the app already senses or can infer:
- **arousal** — calm ↔ activated (from mood entries, panic logs, time of day),
- **energy** — drained ↔ wired,
- **clarity** — foggy ↔ sharp.

A single function `resolve_tokens(theme, state) -> ResolvedTokens` computes density, background luminance, accent warmth, motion duration, and which surfaces render — *every time the state changes*, not once at theme-apply. Concretely, what the user experiences:

- **Drained / low energy →** the whole app dims a few percent, type grows, motion slows, secondary cards fade out, the rail collapses to fewer rooms, the dashboard surfaces *one* door. The screen literally gets quieter because you are. *"There's less here on purpose."*
- **Anxious / high arousal →** density drops, chrome goes minimal, the next action narrows to the single smallest step, an inline breathing affordance appears, the hearthlight's pulse slows to pace your breath.
- **Hypomanic / many rapid signals →** the room does **not** cheer. It steadies: accent desaturates, side-doors vanish, one grounding line surfaces. (The profile: "nothing celebratory.")
- **Crisis signal →** the entire screen yields. Everything except the one warm door dims toward black.

Qt mechanism: drive the continuous parts (luminance, accent warmth, density spacing) through `QPropertyAnimation` on a custom `QObject` of `pyqtProperty` colors/floats over ~1.2s; toggle discrete structure (show/hide secondary cards, rail width) with widget visibility, gated by `reduced_motion`. **No competitor can copy this — it requires owning the whole surface and sensing the user's state, which is Hearth's entire premise.**

### B. The Hearthlight — one warm focal element, reused everywhere
A single custom-painted ember (`QWidget` + `paintEvent` + `QRadialGradient`, breathing via `QPropertyAnimation` on a `glow`/`pulse` property). It is **never decoration** — its color, brightness, and breathing rate *are* a live readout of state. The same motif recurs across the product as one unmistakable Hearth signal:
- **Onboarding:** the ember grows as you disclose; it *is* the progress indicator (no colored dots). On finish it expands and resolves into the main window's header glow — carrying a flame into the next room (`audit_01`).
- **Dashboard:** it sits at the top, encoding your energy as warmth; recording your first signal warms it in place (`audit_02`).
- **Breathe / Panic:** it expands on inhale and dims on exhale — the room breathes *with* you; you can pace your breath without reading a number (`audit_04`, `audit_05`).
- **Automation:** the "Hearthstone" — its glow is the live state of the protective engine; it banks to a dim coal when you pause protection (`audit_07`).
- **Tray:** a custom hearth icon whose glow reflects Hearth's current sense of you — the warm corner of the computer, literally, always on in the background (`audit_08`).
- **Progress:** replaces the generic chunk-fill `QProgressBar` — a streak/goal/session glows warmer as it fills (`audit_09`).

### C. The room turning toward you — crisis as quieting, not alarm
When risk is detected (a self-harm answer, journal language tripping `_check_risk`, a panic spike), Hearth does not pop a triangle-icon `QMessageBox`. The surface *softens and leans in*: the active content recedes, warmth rises from the bottom edge, the rest dims, and one human sentence with one large calm action appears (`QStackedWidget` swap + `QPropertyAnimation` geometry/opacity). On the dedicated crisis screen, tapping 988 turns the whole screen into a slow ~60bpm heartbeat pulse — paced *below* the user's panic rate to physiologically pull them down. **No other app turns its crisis screen into a slowing heartbeat when you reach for help.** (`audit_03`, `audit_04`, `audit_05`.)

### D. Your data as warmth, not surveillance
The same numbers, told as a fire someone tends rather than a compliance report:
- **The steadiness ribbon** (meds): the last ~14 days as warm marks — filled dot for taken, soft hollow ring for a skip, half-warm for late. Recent-weighted and self-healing, so it can never become "Missed: 47." A skip reads as a small gap in a glow, with the line *"Six steady days. Yesterday slipped by — it happens."* (`audit_06`.)
- **The personal heat-map calendar:** each day a warmth dot colored by that day's mood/energy. This *is* the mood visualization — it replaces the matplotlib placeholder entirely (`audit_03`, `audit_09`).
- **The recent-care feed** (automation): a human-voiced ledger — *"2:14pm — Lowered your brightness as the afternoon dipped. 1:50pm — Closed Discord when your focus block started."* — replacing the rules `QTableWidget` and the ASCII analytics dump, turning "I gave an app root access" anxiety into visible, undoable trust (`audit_07`).

### E. The two-font voice — a letter, not a dashboard
A **warm literary serif** for everything the user *reads as language* (greeting, journal, prompts, crisis copy, the one true sentence) against a **quiet humanist sans** for *controls* (buttons, nav, labels, numbers, timestamps). This single contrast is instantly un-SaaS: it reads as "someone wrote this for you," which is the aesthetic profile's whole "Kinfolk / Aesop / library" register. (Today everything renders in the banned Tailwind-default sans, and the serif the profile demands never ships — `audit_09`.)

### F. Theme as a gesture of self-care — "The Light"
The corner `QComboBox` labeled "Theme" dies. In its place, a warm control that asks *"How's the light right now?"* — a brightness/warmth band you drag, with the room easing live underneath your finger, from Bright → Easy → Dim → Dark. Font-size and reduced-motion live here too, framed as *"easier to read"* and *"less movement,"* never as "Accessibility settings." You are not configuring software; you are turning the lights down because you're tired. (`audit_08`.)

---

## What Hearth's UI must NEVER do

A banned list. Each item is a line that, if crossed, means the build has drifted back toward the generic product the audits condemned.

- **Never greet the user with commerce.** No upsell banner, trial pitch, or plan badge in the doorway. Monetization lives in Settings, never on Today, never on a crisis surface, never as a navigation destination. (`audit_02`, `audit_07`, `audit_08`.)
- **Never reward disclosure with a dialog box.** No `QMessageBox` after logging a mood, a dose, a diary card, a journal entry, or a crisis signal. The room responds; it does not pop an alert.
- **Never render a person's worst answer as the least-distinguishable widget.** "Suicide" is never a spinbox in a grid next to "Binge/purge." Stakes get weight.
- **Never paint the lifeline as a threat.** The 988 button is warm amber, never delete-red. Red is reserved for genuine escalation, and even then framed as care.
- **Never ship a dev placeholder.** No `(matplotlib integration)`, no `Cycle: -- / --`, no `Mode: suggestions_only` raw enum, no `--` analytics walls, no `{n:03d}` format strings, no `12 moved, 3 skipped, 0 errors` rsync voice. Every state — empty, loading, error — is a designed, warm state.
- **Never let a screen bypass the theme.** No hardcoded `_CALM_BG = "#e8f4f8"` light-blue, no `color: green`, no Bootstrap `#2ECC71`/`#3498DB`/`#E74C3C` traffic lights, no `Segoe UI` pins, no light-mode `#f5f5f5` fallbacks that flashbang inside a dark app. One token source. (`audit_04`, `audit_06`, `audit_07`, `audit_09`.)
- **Never show a permanent, growing failure counter.** No "Adherence rate," no lifetime "Missed" tally. Recent, self-healing, forgiving rhythm only.
- **Never use the optimization/automation/wellness register.** Banned words: *optimize, supercharge, unlock, journey, aggressively, autonomous mode, adherence rate, premium* (as a feeling-descriptor), *Navy SEALs*, "how are we feeling today?", "Whether you're a [A] or [B]…". The voice is a thoughtful adult speaking to another in a quiet room.
- **Never assemble a refuge from raw native Qt.** No `QCalendarWidget`, `QSpinBox` steppers, `QCheckBox` grids of 28, `QGroupBox` floating-title cards (they clip — every clipped header in the audits is this), `QListWidget` debug dumps, `QComboBox` for momentous choices, or `QToolTip` as confirmation. Custom-painted Hearth primitives replace them.
- **Never snap.** No instant hard cuts between emotional spaces, no bouncy motion, no confetti for logging a hard day. Motion is slow, eased, like turning a page — and honors `reduced_motion` with a calm static fallback.
- **Never make crisis more than one motion away, and never make accessibility the deepest-buried thing.** The controls a struggling person needs most (crisis, dim the light, bigger text) must be the easiest to reach, not five sections down a tab mislabeled "Profile."

---

## The verification gate

Before any surface is called done, it must pass all six tests from `00-aesthetic-profile.md` — **the accent test, the motion test, the voice test, the reference test, the anti-reference test, the chair test** — plus the two thesis tests this vision adds:

- **The adaptation test:** does this surface visibly change when the user's state changes? If it's the same at full-energy and drained, it isn't Hearth yet.
- **The specificity test:** could this element exist in any other app unchanged? If yes, rewrite.

If a surface passes the happy path but fails the empty, loading, error, or crisis state, it fails the gate. Every state is a designed state.
