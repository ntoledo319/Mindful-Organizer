# Audit 06 — Medication & Adherence

**Surface:** `src/gui/widgets/medication_widget.py`
**Screenshot read:** `/tmp/hearth_ui/medication.png`
**Auditor stance:** ruthless, specific, first-principles. The founder called the current UI "dogshit beta bare-bones." This document explains why that is the correct read, then rebuilds it.

---

## 1. What this surface is

**Purpose.** A place to record which psychiatric (and other) medications a person takes, when they take them, and whether they actually took today's doses — then turn that history into something a prescriber can read. For this audience the stakes are not cosmetic. Sertraline, lamotrigine, lithium, an SSRI taper, a stimulant on a controlled schedule — missing or doubling these has real consequences, and the app's own crisis heuristic (`_sync_status_to_db` -> `MEDICATION_LOGS` -> "medication-miss" detection) treats a gap here as a possible warning sign.

**The user's state when they reach it.** Almost never neutral. Three dominant arrivals:
- **The morning autopilot.** Half-awake, pre-coffee, pill in hand, wants to tap one thing and leave. Cognitive budget: near zero.
- **The shame spiral.** It's 4pm, they realize they forgot this morning's dose (again), and they open this screen already braced to be judged. This is the single most important emotional moment on the surface and the current design actively makes it worse.
- **The before-appointment scramble.** Psychiatrist in 20 minutes, needs to honestly answer "how's the medication going?" without lying or guessing.

**The job it must do.** (1) Make logging today's dose a one-gesture, zero-friction act. (2) Hold a missed dose **without shame** — record it as information, never as failure. (3) Quietly accumulate an honest picture over time. (4) Hand that picture to a clinician in their language. (5) Never, ever feel like surveillance or a compliance scoreboard.

It currently does roughly none of these well.

---

## 2. Why it fails — forensically

### 2.1 Information architecture — backwards and hostile

The screen leads, top to bottom, with: **title -> legal disclaimer -> an empty list box -> three CRUD buttons -> today's schedule -> export**. The *first substantive thing the user sees is a liability waiver in bold italic.* The literal first message Hearth gives a person about their psych meds is "This is not medical advice." That is the emotional posture of a pill bottle's fine print, not of "the warm corner of the computer."

The thing the user came to do — **take today's dose** — is buried *below* the management UI. "Today's Schedule" sits under the medication list and its three buttons, and in the screenshot its header ("Today's Schedule") is **clipped and overlapping the card above it** (`Today's S​chedule` is sliced by the card's top edge). The job-to-be-done is third in the reading order, visually truncated, and currently empty.

**Principle violated:** information hierarchy must follow emotional/task hierarchy (the project's own aesthetic profile, rule in §Layout). Here the hierarchy is inverted — admin first, disclaimer louder than the task, the actual task demoted and clipped.

### 2.2 The widgets — a catalogue of native-Qt tells

This is the core of "bare-bones beta." The screen is raw Qt with a dark recolor:

- **`QGroupBox` for every section** ("My Medications", "Adherence Summary", "Today's Schedule"). The QSS tries to dress these up with a floated uppercase title (`top: -12px`), but in the render the floated titles **collide with the card edges and clip** — "My Medications", "Adherence Summary", and "Today's Schedule" are all sliced across the top. A floated-legend group box is a 1995 desktop-forms idiom. It says "settings dialog," not Hearth.
- **`QListWidget` as the medication list** — a bare bordered box, empty in the screenshot, that will render meds as a single run-on string: `f"{name} -- {dosage} -- {freq} @ {time_str}"` (line 335). That double-dash-delimited string is a **debug `print()` masquerading as UI**: `Sertraline -- 50mg -- Daily @ 08:00`. No human designed that; it's `str.join` leaking onto the screen.
- **Three generic CRUD buttons — Add / Edit / Remove** — equal weight, equal size, spanning the full width under the list. This is the canonical "I wrapped a database table in three buttons" pattern. It is the most generic arrangement of controls that exists. Swap test: these three buttons could sit under *any* list in *any* CRUD app on earth.
- **`QCheckBox` rows as the dose log** (line 371) with the label baked into the box: `08:00 -- Sertraline (50mg)`. Taking your medication should not feel like ticking a to-do item in a forms grid. (This is exactly the "wall of checkboxes" the brief calls hostile to this audience.)
- **A green text `"Taken"` label** appended next to checked rows, styled `color: green; font-weight: bold;` (line 383) — a raw CSS color name, not even a theme token. It will clash with Onyx's warm sage `success` (#5E9A68) and is invisible-adjacent in the high-contrast Quiet theme.
- **`QTimeEdit`, `QComboBox`, `QLineEdit` in the dialog** — stock native spinners and dropdowns. The "Add" flow is a four-field vertical form with a native `Save | Cancel` button box. It is indistinguishable from adding a calendar entry in any 2010-era desktop app.

**Principle violated:** Hard Rule #2 ("Why does THIS project need THIS to look/work THIS way?") and the banned "raw unstyled native OS widgets." Every widget here is the Qt default, lightly painted. Nothing on this surface could *only* exist in Hearth — it lands squarely at **GENERIC**.

### 2.3 The adherence panel — surveillance framed as a stat block

Top-right card reads:
```
Taken: 0
Missed: 0
Late: 0
Adherence rate: --
```
This is the single most tone-deaf element on the surface. Consider what it is for *this* audience:

- It is a **lifetime running tally of failure**. "Missed: 0" today becomes "Missed: 47" in three months. You are putting a permanent, ever-growing **failure counter** in front of people whose conditions are characterized by shame, executive dysfunction, and self-criticism. For someone with depression or OCD, "Missed: 47, Adherence rate: 61%" is not neutral data — it's ammunition for the inner critic.
- "**Adherence rate**" is *clinical-compliance language*. It frames the user as a patient being measured for obedience. Hearth is supposed to be a companion, not a parole officer.
- The math is cruel and wrong: `total` counts every recorded status across all time, so a single early miss permanently drags the percentage and it never "heals." There is no concept of *recent* adherence, no concept of "you've taken it 6 days running."
- And right now it's all `0` and `--` — the empty state shows the failure scaffolding with nothing in it, which reads as broken.

**Principle violated:** "Must NEVER feel like surveillance"; the brief's mandate to *reduce shame around missed doses*. This panel does the literal opposite — it is a shame-accumulation device.

### 2.4 Visual hierarchy, typography, color

- **Hierarchy is flat.** Title (26px), disclaimer (bold italic body), and section content are nearly the same visual weight. The disclaimer is *bolder* than the task. There's no focal point; the eye has nowhere to land first, which is exactly wrong for a low-cognitive-budget moment.
- **Typography ignores the project's own contract.** The aesthetic profile demands a **serious serif** for anything the user reads and warm humanist sans for UI. This surface is 100% system sans (`Segoe UI`, hardcoded at lines 52/373, which isn't even in the QSS font stack — it'll fall back unpredictably across platforms). A drug name — the most human, most personal datum here — is rendered in the same flat sans as a button label.
- **Color does no work.** The whole screen is `#0F0F11`/`#18181A`/`#222225` greys with zero accent presence. The warm Onyx accent (`#D9A05B`, the literal *hearthlight*) appears **nowhere** except, faintly, on the selected nav item. A screen about warmth and care has no warmth in it. It's monochrome charcoal — competent dark mode, zero identity.
- **Contrast traps.** `text_muted` (#8E8E93) on `surface` (#18181A) is borderline for the group-box titles; the clipped uppercase legends are both low-contrast *and* sliced.

### 2.5 Spacing & density

Two stacked cards on the left, one floating stat card on the right, then a full-width export bar — but the right column is **mostly empty void** (the adherence card is tiny, the rest of that column is dead charcoal). Meanwhile the left cards have inconsistent internal rhythm (group-box padding `24px 16px 16px 16px` fighting layout spacing of 12/16px). It reads as *under-designed negative space* — the bad kind the profile explicitly warns against ("intentional rather than under-designed") — not calm restraint. The export button is a lonely full-width bar stranded at the bottom with nothing anchoring it.

### 2.6 Interaction & feedback, motion

- **Toggling a checkbox = "missed."** Look at `_mark_taken` (line 389): unchecking sets status to **"missed"** — not "pending," *missed*. So if a user taps a dose by accident and unticks it, Hearth silently records a missed dose and feeds it to the **crisis heuristic**. A misclick can trigger a false "medication-miss" signal. This is a correctness-and-trust bug, not just polish.
- **"Late" is dead.** The summary counts "Late," the schedule never produces it. There is no late path, no "I took it, just not on time" — the most common real-world case for this audience — so honest late-logging is impossible and the "Late" stat is permanently 0.
- **No motion at all.** Checking a dose does nothing but flip a box and append green text. No acknowledgment, no warmth, no page-turn. The profile asks for motion "like turning a page"; there is none. The act of caring for yourself gets zero felt response.
- **No "as needed" handling.** Frequency offers "As needed," but the schedule logic blindly lists every med daily, so a PRN benzo shows up as a checkbox you're implicitly expected to take every day — actively bad guidance for an anxiety/panic user.

### 2.7 Empty / loading / error states

- **Empty state is a void plus a waiver.** First run: an empty `QListWidget` box, three buttons, "No medications scheduled.", and the legal disclaimer. No invitation, no warmth, no first action. Compare the brief's "chair test" — does the room feel prepared for them? No; it feels like an unconfigured admin panel.
- **Error states are `QMessageBox` popups** ("Select a medication first.", "Export failed: ...") — jarring native OS modal alerts, the most generic possible feedback.

### 2.8 Copy — run the swap test

- **"Medication Tracker"** — title. Swap "Hearth" for "PillReminder Pro": still works perfectly. **Dead copy.**
- **"This is not medical advice. Consult your healthcare provider for all medication decisions. This tool is for personal tracking only."** — generic legalese, and it's the *loudest* thing on screen. Reads like terms-of-service, not a companion.
- **"Adherence rate"** — clinical compliance vocabulary; the *opposite* of Hearth's voice. (Profile voice rule: "could a thoughtful adult say this to another in a quiet room?" No one says "your adherence rate is 61%" to a friend.)
- **"Export for Healthcare Provider"** — functional, soulless, and over-formal ("Healthcare Provider" instead of "your doctor / your psychiatrist").
- **"No medications scheduled."** — a system status, not a sentence a person would say.
- **`-- ` and `@`** as visible UI delimiters — copy that is literally code formatting.

Not one string on this surface has a point of view. Every line passes the swap test, which per Hard Rule #3 means the copy is **dead**.

### 2.9 Emotional tone for THIS audience

This is the deepest failure. The surface treats medication as **data entry with a compliance score and a liability waiver.** For someone managing bipolar disorder or depression, their relationship to medication is freighted — with side effects, with stigma, with the daily small defeat of forgetting, with the larger fear of relapse. The screen meets all of that with a checkbox grid and a running miss-counter. It performs *bureaucracy* at a person who needs *scaffolding*. There is no warmth, no permission to be imperfect, no acknowledgment that taking your meds is sometimes genuinely hard. It is the journal-with-ads / wellness-clipboard energy the brand swore never to have.

### 2.10 Accessibility

- Hardcoded `Segoe UI` (lines 52, 373) bypasses the theme's font stack and the dyslexia-font accessibility toggle entirely.
- `color: green` (line 383) is a raw name, not a token — breaks color-blind overrides and the Quiet high-contrast theme; status is communicated by **color alone** (no icon/text differentiation between taken/late states).
- Checkbox label crams time + name + dose into one string — long for screen-reader users and impossible to restyle hierarchically.
- No keyboard affordance beyond default tab order; the primary action (log a dose) has no obvious large hit target.

### 2.11 Where it lands: **GENERIC**

Every test fails the specificity check. Strip the dark recolor and this is a stock PyQt CRUD + checklist that could ship in a dental-office intake tool. **GENERIC, bordering on broken** (clipped headers, misclick-records-miss bug, dead "Late" path, PRN-as-daily).

---

## 3. The reimagination — *The Shelf*

> First principle: Hearth doesn't *track* medication. It **keeps a small shelf for you and gently notices.** The metaphor is a windowsill or a bedside shelf where your bottles live — warm, personal, low-stakes. You're not filing a compliance report; you're tending a small routine, and a quiet companion is keeping you company while you do it.

### 3.1 New information architecture (emotional order, not admin order)

1. **Today's doses** — *the only thing that matters on arrival.* Top of screen, large, unmissable.
2. **The steadiness ribbon** — a warm, recent, shame-free reflection of the rhythm (replaces "Adherence rate").
3. **The shelf** — your medications, as objects, with add/edit living *in context* (not a CRUD button bar).
4. **For your doctor** — the export, reframed, tucked at the foot.

The disclaimer is **demoted to a single quiet line at the very bottom**, in `text_muted`, normal weight — present for liability, invisible to emotion.

### 3.2 Layout & the signature element — the **Dose Card**

Replace the checkbox grid entirely. Each of today's doses is a **wide, low Dose Card** — a custom `QFrame` painted to feel like a pill bottle's label resting on a shelf:

- Left: a small **custom-painted lozenge/capsule glyph** (`QPainter`, tinted with the med's own assigned warm hue from a small natural-material palette — sage, clay, slate, dried-ink — *not* one universal accent). This gives each medication a stable visual identity over time; you learn "the clay one is my morning SSRI" by shape and color, not by reading.
- Center: the **drug name in the serious serif** (the human datum, finally rendered like it matters), with dose + time tucked beneath in muted sans — "the numbers tucked into the background" the profile demands.
- Right: **one large primary action** — a single warm "tap to take" target that fills the whole right third of the card (generous hit area; one gesture).

**Taking a dose (the signature moment #1 — "the warming"):** Tapping the action runs a slow `QPropertyAnimation` (≈400ms, eased, *page-turn* not bounce): the card's left edge **warms** — the capsule glyph and a thin left border bloom from neutral to hearthlight (`accent` #D9A05B), and the card settles a half-step calmer. A single soft line appears: *"Logged — 8:02am."* No checkmark, no green, no confetti. It feels like the lamp on your shelf catching the pill. That glow is the only celebratory motion in the app, and it's deliberately quiet. **This could exist nowhere else** — it's Hearth's "dims the lights / catches the warmth" identity made literal at the dose level.

**Logging honestly when life happened:** Long-press / a small secondary affordance on the card opens three calm options, *not* a binary:
- **"Took it"** (warms now)
- **"Took it late"** (warms, but the time note reads the actual time, no penalty, no red) — this finally makes the dead "Late" path real and honest.
- **"Skipped today"** — and critically, the copy for a skip is *"Noted. Tomorrow's a fresh one."* A skip warms the card to a **dim, resting tone** (not alarm red) — acknowledged, held, not punished. This directly answers the brief's "reduce shame around missed doses."

Fixes the misclick bug by design: there is no "untick = missed." State changes are explicit, intentional choices, never accidental toggles.

### 3.3 The behavioral-token adaptation (the differentiator)

The Dose surface **reads the user's state and adapts**, which is the whole Hearth thesis:

- **Drained / low-energy state** (from theme/mood signal): density drops, the card list collapses to *only the next undone dose* — literally one chair, one action — with everything else folded behind "the rest of today." Cognitive load minimized when the budget is lowest.
- **Anxious / crisis-adjacent state:** if a PRN/as-needed anxiety med is on the shelf, it surfaces it gently and contextually ("If you need it, it's here") instead of nagging it as a daily checkbox — and the steadiness ribbon hides entirely so no stat can be read as pressure in that moment.
- **Steady / neutral state:** the full shelf + ribbon shows, calm and complete.

Mechanism: the widget already receives `main_window`; subscribe to the theme/state token (`layout_density`, plus a state signal) and switch which children are visible + the spacing scale. This is achievable today with show/hide + a `QVBoxLayout` density multiplier and `QPropertyAnimation` on opacity.

### 3.4 The **steadiness ribbon** (replaces "Adherence rate")

Kill the failure tally. Replace it with **signature moment #2 — a warm, recent, forgiving rhythm strip:**

- A horizontal row of the **last ~14 days** as small custom-painted marks (`QPainter`): a *warm filled dot* for a day you took your doses, a *soft hollow ring* for a skip, a *half-warm* for late. Recent-weighted, self-healing (old misses fade), capped to a window so the number can never become "Missed: 47."
- One plainspoken line above it, in serif, in Hearth's voice: e.g. *"Six steady days. Yesterday slipped by — it happens."* Never a percentage. Never the word "adherence." Never "rate."
- The ribbon **celebrates rhythm, not perfection** — a single skip in a warm row reads as a small gap in a fire's glow, not a red mark on a report card.

This is the inverse of surveillance: it shows you the warmth of your routine and treats a miss as a fading ember, not a permanent strike.

### 3.5 The shelf (medication management, de-CRUD'd)

The `QListWidget` + Add/Edit/Remove bar dies. Medications live as **small shelf tiles** below the day's doses; **"+ Add a medication"** is a single warm ghost affordance at the end of the shelf (not three equal buttons). Edit/remove live on each tile (hover/long-press -> a quiet menu), *in context*, so the global button bar disappears entirely (Elimination before addition — Hard Rule #5). The add/edit flow becomes a **calm sheet** that slides up (page-turn motion), serif labels, the time picker reframed as "When do you usually take it?" — a question a thoughtful person would ask, not an intake field.

### 3.6 Copy rewrite (point of view, swap-test-proof)

| Current (dead) | Hearth voice |
|---|---|
| "Medication Tracker" | *"Your shelf"* / *"Today's doses"* (no "tracker" — Hearth tends, it doesn't track) |
| "Adherence rate: 61%" | *"Six steady days. Yesterday slipped by — it happens."* |
| "Missed: 0 / Late: 0" | (deleted — replaced by the steadiness ribbon) |
| "No medications scheduled." | *"Nothing on the shelf yet. Add the first one when you're ready."* |
| "Export for Healthcare Provider" | *"Put together a note for your doctor"* |
| disclaimer (bold, top) | quiet bottom line: *"Hearth keeps the record. Your doctor makes the calls."* |
| skip confirmation | *"Noted. Tomorrow's a fresh one."* |
| taken confirmation | *"Logged — 8:02am."* |

Run the swap test on *"Hearth keeps the record. Your doctor makes the calls."* — replace Hearth with a competitor and it goes limp; it only works because Hearth has a specific relationship to the user. That's a living line.

### 3.7 Qt build notes (so an engineer can ship it)

- **DoseCard:** custom `QFrame` subclass; `paintEvent` with `QPainter` for the capsule glyph + warm left-edge bloom; the take action is a `QPushButton[class="accent"]` sized to fill the right third. Warm animation = `QPropertyAnimation` on a custom `warmth` `pyqtProperty` driving the border/glyph color (interpolate neutral -> `accent`), ~400ms `OutCubic`, gated by `ThemeManager.reduced_motion`.
- **Steadiness ribbon:** single custom-painted `QWidget`, `paintEvent` draws N day-marks from a recent-window slice of `self._adherence`; pure `QPainter`, no native widget.
- **Shelf tiles & add-sheet:** `QFrame` tiles in a flow/`QVBoxLayout`; add/edit as a slide-up panel (`QPropertyAnimation` on `geometry`/`maximumHeight`) rather than a `QDialog` modal where possible.
- **Tokens:** route every color through `ThemeManager.get_colors()` — kill the hardcoded `Segoe UI` and `color: green`. Add a small per-med hue assignment from the natural-material palette.
- **State adaptation:** read `current_theme.layout_density` + a state signal from `main_window`; show/hide children and scale spacing accordingly.
- **Correctness fixes (carry into rebuild):** explicit Took/Late/Skipped state (no toggle-implies-missed); honor "As needed" so PRN meds don't appear as daily obligations; make the recent-window the basis for the ribbon so the count can't grow unbounded.

---

## 4. Quick wins vs. deep rebuilds

**Quick wins (hours, high relief, low risk):**
1. **Demote the disclaimer** to a single muted line at the very bottom; strip the bold-italic. Instantly changes the screen's emotional posture.
2. **Reorder IA:** move "Today's doses" to the **top**, above the shelf and management. Fixes the inverted hierarchy and the clipped-header overlap.
3. **Fix the misclick = "missed" bug** (`_mark_taken`): unchecking should return to "pending," never silently log "missed" into the crisis heuristic. (Correctness + trust.)
4. **Kill "Adherence rate" and the lifetime Missed/Late tally**; even before the ribbon exists, replace with a recent-window count and a plainspoken line. Remove the permanent failure counter.
5. **Replace `color: green` + `Segoe UI`** with theme tokens; remove the `--`/`@` delimiters from the list/checkbox strings.
6. **Rewrite the five strings** per the table above (zero engineering cost, large tone shift).

**Deep rebuilds (the real work):**
1. **The Dose Card** + the "warming" take animation — the signature interaction; replaces the checkbox grid.
2. **The steadiness ribbon** — custom-painted recent-rhythm strip replacing the stat block.
3. **Three-state honest logging** (Took / Late / Skipped) with forgiving copy, including a real "late" path and PRN handling.
4. **Behavioral-token adaptation** — collapse to one dose when drained, surface PRN when anxious, hide stats in crisis.
5. **De-CRUD the shelf** — in-context add/edit tiles + slide-up sheet, retiring `QGroupBox`/`QListWidget`/the three-button bar entirely.

---

## 5. Verdict

Today this surface is a **GENERIC native-Qt CRUD form with a compliance scoreboard and a liability waiver bolted on top** — the exact opposite of what a person reaching for it (often in a shame spiral) needs. The single deepest failure is **tone**: it treats medication as data entry to be scored, leading with "This is not medical advice" and tracking a permanent, ever-growing "Missed / Adherence rate" tally that weaponizes the user's own self-criticism. Rebuild it as **The Shelf**: lead with one warm, one-gesture Dose Card whose signature "warming" animation acknowledges the act of caring for yourself, replace the failure tally with a forgiving recent-rhythm steadiness ribbon, and make missing a dose feel *held* ("Noted. Tomorrow's a fresh one.") instead of *counted*.
