# Audit 03 — Daily-Tracking Cluster

**Surfaces:** Mood Tracker (`mood_tracker.py`), Diary Card (`diary_card_widget.py`), Sleep (`sleep_widget.py`)
**Screens read:** `/tmp/hearth_ui/mood_tracker.png`, `diary_card.png`, `sleep.png`
**Verdict:** GENERIC, sliding toward HOSTILE. This is the most emotionally dangerous cluster in the app and it is the least designed. The founder's word "dogshit beta bare-bones" is, for once, an understatement — this isn't a styling problem, it's a *stance* problem. The current screens treat a person's worst day as a database import form.

---

## 1. What this surface is

This is the cluster where a person **tells Hearth how they are**. It is the raw input that every adaptive behavior downstream depends on — if the app is going to dim the lights when you're drained or close Discord when anxiety spikes, *this is where it learns you're drained*. Three jobs:

- **Mood Tracker** — log how you feel right now, on a given day, with the symptoms that came with it and the skills you used to cope.
- **Diary Card** — the DBT evening ritual: emotions, urges (including self-harm and suicide), skills, target behaviors, meds, substances. This is the clinical document a therapist actually reads.
- **Sleep** — log bedtime / wake / quality and see whether the debt is piling up.

**The user's state when they arrive.** This is the critical fact the current design ignores entirely. Nobody opens a mood tracker when they feel great and have spare cognitive budget. They open it when they're flat, anxious, dissociating, ashamed, or in the quiet danger-zone after a bad night. The diary card specifically is opened *at the end of the worst days* — that's when "Suicide: [spinbox 0–5]" is on screen. **The job is not data capture. The job is to let a depleted person mark how they are in as few, as gentle, as un-clinical gestures as possible — and to make the dangerous answers route to help, not to a JSON file.**

The current cluster does the literal opposite: it maximizes decisions, surfaces the most frightening item as the 28th checkbox in a grid, and rewards a completed self-harm entry with a gray "Saved" dialog box.

---

## 2. Why it fails — forensically

### 2.1 Information architecture — a clinical intake form wearing a dark coat

**Mood Tracker.** The screen is four boxes fighting for primacy: a full-month **OS calendar**, a "New Mood Entry" form, "Mood History" list, and "Mood Analytics." There is no answer to "what do I do first?" A person who just wants to say *I feel bad today* is confronted with a date-grid, a time spinbox, a 1–10 slider, **28 symptom checkboxes**, a second grid of therapy-skill checkboxes, a notes box, and a save button — before they've expressed a single feeling. The IA is "show every field the data model has." That's a schema, not a screen. **Principle violated: progressive disclosure and one-primary-action.** A fragile user needs ONE next action; this offers ~35.

**The calendar is the loudest, least-useful element.** It occupies the top-left — the strongest position on the page — to do something you need maybe 5% of sessions (back-dating an entry). Today's entry is the 95% case and it's the *quietest* thing on screen. The hierarchy is inverted. (`_build_calendar` is called first in the left column, `mood_tracker.py:113`.)

**Diary Card.** Worse, because the stakes are higher. It's a vertical wall: Mood slider → **27 emotion checkboxes** → **10 urge spinboxes** (Self-harm, Suicide, Substance use, Binge/purge, Aggression, Avoidance, Reassurance seeking, Safety behavior…) → skills grid + effectiveness slider → target-behavior spinboxes → meds radio → substances text field → notes. Every section has equal visual weight. **"Suicide" sits in a two-column grid next to "Binge/purge," styled identically to "Avoidance,"** as a numeric stepper (`_build_urges_card`, `diary_card_widget.py:168`). The most important signal a mental-health app can receive is rendered as the least distinguishable widget on the page. **Principle violated: visual weight must track human stakes.** Here stakes and weight are completely decoupled.

**Sleep.** The IA is fine in intent (log on the left, log + stats on the right) but the execution is broken at the widget level (see 2.6) — headers are physically clipped ("Log Sleep," "Sleep Log," "Statistics," "Condition-Specific Sleep Tips" are all sliced off at the top in the screenshot), so the user can't even tell what the boxes *are*.

### 2.2 Visual hierarchy — flat, equal-weight, no focal point

Across all three, everything is a `CardFrame` (or worse, a raw `QGroupBox`) of roughly equal size and identical border treatment. Onyx's `border: 1px solid #2C2C2E` on `#18181A` surfaces produces cards that are barely distinguishable from the `#0F0F11` background — so the page reads as a uniform gray field of boxes. There is no figure/ground, no "your eye starts HERE." The single accent color (`#D9A05B` amber) is spent on a slider handle, a couple of buttons, and the selected calendar day — i.e., on chrome, not on meaning. **Principle violated: a screen needs a focal point; an even gray gradient of equal cards is the visual equivalent of monotone speech.**

### 2.3 Typography — the brief's "personality-free sans heading + lighter sans body" anti-pattern, verbatim

Section titles are `SectionTitle(...)` and `QGroupBox` titles; body is `BodyLabel(...)`. Both render in the same `"SF Pro Text"/"Inter"/"Segoe UI"` stack from `themes.py:247`. There is **zero typographic voice** — no display face, no weight contrast that means anything, no rhythm. The sleep widget hardcodes `QFont("Segoe UI", 14, QFont.Weight.Bold)` (`sleep_widget.py:91`) — literally the Windows system font, on macOS, ignoring the theme entirely. This is the exact anti-pattern the registry bans ("Sans-serif heading + slightly lighter sans-serif body with zero personality"). **The mood scale labels ("Okay," "Fair," "Good") are doing emotional work and get no typographic care at all.**

### 2.4 Color / contrast — amber wasted, danger invisible, condition-blind

- The amber accent (`#D9A05B`) is Hearth's one warm note — "hearthlight" — and it's squandered on a slider track and an "Export Mood Data" button. It never touches the moments that matter.
- **The `danger` token (`#C85250`) appears nowhere in this cluster.** Self-harm and Suicide — the two answers that should change the app's behavior — are rendered in default text color. The dead code at `mood_tracker.py:457–462` *tries* to color low-mood history entries but sets the foreground to `palette().color(...Text)` — i.e., the default color — a no-op that betrays someone knew it should be different and gave up.
- **Condition tokens are ignored.** `themes.py` ships `condition_suitability`, `layout_density`, `animation_speed_ms`, `chrome_visibility` — the literal "behavioral tokens" the brief calls the differentiator — and **not one daily-tracking widget reads a single one of them.** They receive a flat `theme.to_dict()` and hardcode `self._theme.get('text', '#333')`. The product's whole thesis ("your computer adapts to your psychology") is contradicted on the surfaces where it would matter most.

### 2.5 Spacing / density — a wall, on purpose

28 checkboxes in mood, 27 in diary, all on a fixed `8px` grid spacing (`diary_card_widget.py:158`), 4-up columns. There is no grouping, no breathing room, no chunking. For an ADHD or anxious user this is a textbook overwhelm trigger: undifferentiated density with no entry point. **And the density is hardcoded** — `themes.py` defines `layout_density` (0.8 spacious → 1.2 compact) precisely so the app could *loosen* the UI when someone's drained. It's never consulted. The one place adaptive density would be a genuine clinical feature, it's dead.

### 2.6 The actual widgets — native-Qt tells everywhere

This is where "thin coat over raw Qt" is most literal:

- **`QCalendarWidget`** (mood) — the unmistakable OS month grid with red Sundays/Saturdays, tiny arrow navigation, a month/year dropdown. It is styled with a *one-line* stylesheet (`mood_tracker.py:138`) that sets only the background; everything else is OS default. It screams "stock widget."
- **`QSpinBox` with up/down arrows** (diary urges & targets, `diary_card_widget.py:182`) — the most clerical control in the toolkit, used for "Suicide." Tiny native steppers. Nobody in crisis wants to *click an up-arrow four times* to say "the urge is strong."
- **`QTimeEdit` spinboxes** (mood time, sleep bed/wake, `sleep_widget.py:216`) — native HH:MM steppers.
- **`QGroupBox`** (sleep, mood symptom/skill groups) — the raw framed-box-with-notch-title. In sleep it's completely unstyled, and the QSS rule `QGroupBox { margin-top: 28px }` combined with the title at `top: -12px` (themes.py:514–533) is exactly why every sleep header is **clipped** in the screenshot.
- **`QListWidget`** (history, sleep log) — a plain scrolling text list. The sleep log renders empty boxes.
- **`QCheckBox` grids** — the default square indicators.
- **`QRadioButton` Yes/No** (diary meds).

Sleep is the worst offender: it **never imports `gui.components` at all** and defines its own `_section_title/_body_label/_accent_button` helpers with hardcoded fonts. It is, structurally, a different (worse) app bolted into the same window.

### 2.7 Interaction & feedback — punishing, modal, and absent where it counts

- **Saving anything pops a `QMessageBox.information` modal** ("Mood entry saved successfully." / "Diary card for 2026-06-04 saved." / "Sleep entry saved."). A blocking OS alert with an OK button is the most jarring possible response to a tender act of self-disclosure. You told the app you feel terrible; it threw up a system dialog. (`mood_tracker.py:440`, `diary_card_widget.py:376`, `sleep_widget.py:361`.)
- **No response to dangerous input.** You can set Suicide = 5 and the app's only reaction is "Diary card saved." **There is no path to the Crisis surface, no softening, no acknowledgment.** This is the single most serious failure in the entire cluster — it's not just bad taste, it's a duty-of-care gap. (The Crisis nav item is *right there* in the sidebar, unlinked from the one place that should trigger it.)
- **Slider is the only continuous control and it's mute** — moving it just updates a "5 — Okay" text label. No color shift, no warmth change, no haptic-feeling detents.
- **Sleep "Log" and "Stats" render placeholders** (empty list, "Average duration: --").

### 2.8 Motion — none

`animation_speed_ms` exists in every theme (Onyx 250ms, Quiet 0ms for reduced-motion). **Zero `QPropertyAnimation` in any of the three files.** Checkboxes snap, the save dialog pops, the slider jumps. For an audience that includes people who are dissociating or overstimulated, the *absence* of gentle motion is itself a failure — there's nothing to make the interface feel alive-but-calm, and nothing that respects the reduced-motion token when it should.

### 2.9 Empty / loading / error states — developer placeholders shipped to users

- **"Mood Chart (matplotlib integration)"** — a literal dev to-do, gray text in a gray box, shown to a person in distress (`mood_tracker.py:368`). This is the clearest single signal of "unfinished beta" in the app.
- **Analytics read "7-day average: --", "30-day trend: --", "Mood volatility: --", "Top triggers: --"** — four em-dashes stacked. An empty state should *invite* ("Two more check-ins and I can start showing you patterns"), not display null sentinels.
- **Sleep stats: "Average duration: --", "Average quality: --", "Sleep debt (7 days): --"** — same null wall. The empty sleep log is just a blank bordered box.
- There is no error state worth the name — failures are swallowed into `logger.debug` and the user sees nothing.

### 2.10 Copy — run the swap test; the copy is dead

Every label is a clinical/database noun with no point of view:

- **"New Mood Entry"**, **"Mood Level: 5 — Okay"**, **"Symptoms"**, **"Therapy Skills Used"**, **"Export Mood Data"**, **"Mood History"**, **"Mood Analytics."**
- **"Emotions Felt Today," "Urges (0 = none, 5 = strongest)," "Target Behaviors (count today)," "Medications & Substances."**
- **"Log Sleep," "Sleep Tracker," "Statistics," "Condition-Specific Sleep Tips."**

**Swap test:** replace "Hearth" with "MoodFlow" or "Daylio" or any clinical EHR — *every line still works unchanged.* That is the definition of dead copy per the project's own Hard Rule #3. There is no warmth, no "hearth" voice, nothing that could only be said here. "Export Mood Data" is a spreadsheet verb. "Symptoms" frames the user as a patient/diagnosis, not a person. And the must-word **"hearth"** appears nowhere; the banned register ("data," "tracker," "statistics") is everywhere.

### 2.11 Emotional tone — the opposite of "the warm corner of the computer"

The brief asks for "a quiet, attentive companion." What's on screen is an **intake clerk**. It asks 35 questions, files the answers, and dismisses you with an OK dialog. It surfaces "Suicidal Ideation" as checkbox #28 and "Suicide" as a stepper. **For this specific audience — people who track *because* they're struggling — this tone isn't neutral, it's corrosive.** It tells the user "you are a row of data." That is precisely the "journal with ads / wellness app / corporate mindfulness" feeling the brief says Hearth must NEVER have. It tracks; it does not act; it does not care.

### 2.12 Accessibility

- The `font_scale`, `dyslexia_font`, `reduced_motion`, and `color_blind_mode` machinery exists in `ThemeManager` — but these widgets inline-set `color:` and `font` per-control, so global font scaling and dyslexia-font swaps **won't reach** the hardcoded sleep fonts or the per-widget stylesheets.
- Checkbox-grid as the primary input is a motor-and-cognitive tax: 28 small hit-targets, no keyboard-friendly grouping, no labels-as-clickable-rows in mood.
- Slider 1–10 conveys value by position only — no text alternative beyond a small label, a problem under color-blind/low-vision modes.
- The amber accent on `#0F0F11` is fine for contrast, but danger states (the ones that need to scream) are absent, so there's nothing for an AT user to even perceive as urgent.

### 2.13 Where it lands: GENERIC → DISTINCTIVE

| Surface | Today | Why |
|---|---|---|
| Mood Tracker | **GENERIC** (calendar+form is interchangeable with any tracker) | OS calendar, checkbox wall, "matplotlib" placeholder |
| Diary Card | **GENERIC, trending HOSTILE** | Suicide-as-spinbox, no crisis routing, vertical wall |
| Sleep | **BELOW GENERIC** (off-theme, clipped, broken) | hardcoded Segoe UI, clipped headers, empty placeholders |

Nothing here passes the Specificity Test. Every element could be lifted into Daylio, Bearable, or a hospital EHR with no modification.

---

## 3. The reimagination — Hearth's daily check-in

**First principle:** A check-in is a *conversation with a companion who already knows you*, not a form. It should cost the user the minimum number of gestures, lead with warmth, escalate gently when answers are dangerous, and visibly *adapt* to the state it just learned. Density, brightness, and tone are not fixed — they are the behavioral tokens responding in real time. The whole cluster collapses into one tender flow: **"How are you, right now?"**

### 3.1 New IA — one question at a time, not one form with 35 fields

Replace the three separate walls with **a single adaptive check-in that opens on the most human question and discloses progressively.** The data model stays identical; only the *sequence and surfacing* change.

**Step 0 — The hearth dial (the focal point).** A single large, custom-painted radial control: "How are you right now?" The user drags one warm point around an arc. As it moves toward the low end, the **entire surface dims and warms** (the page background interpolates from `surface` toward a deeper ember, and the chrome reduces) — the app is *already* responding. As it moves high, it brightens and the accent saturates. This is the mood "slider" reborn as a single, beautiful, load-bearing gesture. One control replaces calendar+time+slider+value-label.

**Step 1 — "What came with it?" (symptoms, but humane).** Instead of 28 checkboxes, show **6–10 condition-relevant chips** drawn from the profile (the data already filters by condition — `_populate_symptoms` knows the user's conditions; it just dumps all 28). Chips are large, warm, tappable; tapping one makes it glow, not check a box. A quiet "show more" reveals the long tail only if wanted. **Elimination before addition (Hard Rule #5):** a depressed user sees depression-relevant feelings first, not OCD's "Contamination Fear."

**Step 2 — "Anything you need help carrying?" (the urge / safety check).** This replaces the diary urge-grid. Self-harm and Suicide are **pulled OUT of the grid** and asked separately, last, gently, and **with the danger token doing real work** (see signature moment 3.4). Everything else (substance, avoidance, etc.) stays as soft 0–5 *segmented dials*, never native spinboxes.

**Step 3 — Skills & sleep fold in contextually.** "What helped?" (skill chips, same treatment). Sleep becomes a *single warm question in the morning check-in* ("How'd you rest?" → Poor / Okay / Good as three big warm tiles, which the sleep widget *already* has — it just needs the rest of the screen deleted around it) rather than its own clinical tab with stats placeholders.

**Result:** the calendar is demoted to a small "← yesterday / pick a day" affordance; analytics moves to a separate, opt-in "patterns" view that is *never* shown empty.

### 3.2 Layout & hierarchy

- **One column, centered, generous.** Kill the 2-column body and the equal-weight card grid. The check-in is a vertical *narrative*, max-width ~560px, lots of vertical air (driven by `layout_density`, finally read).
- **The dial is the figure; everything else is ground.** Only the active step is fully lit; completed steps collapse to a single warm summary line ("Feeling: low · 3 things came with it"). This is Qt-trivial with stacked `QWidget`s + opacity.
- **The accent finally lands on meaning** — the dial, the active chip glow, the "I'm here" crisis affordance — not on an Export button.

### 3.3 Signature interactions, adaptive behavior, and the Qt mechanisms

- **The warming dial.** Custom `QWidget` with `paintEvent` using `QPainter` (radial `QConicalGradient`/arc, a single draggable knob). On value change, animate the window's background via `QPropertyAnimation` on a custom `bg_color` `pyqtProperty` (or `QGraphicsColorizeEffect`), duration = `theme.animation_speed_ms` (so Quiet/reduced-motion = instant). **This is the behavioral-token thesis made literal: the screen physically warms or cools with your mood as you set it.**
- **Chips, not checkboxes.** Custom `QAbstractButton` subclasses, `setCheckable(True)`, painted with rounded warm fills, a soft glow on select via `QGraphicsDropShadowEffect` animated in. Touchable, calm, ADHD-legible.
- **Soft confirmation, never a modal.** Replace every `QMessageBox` with an in-surface, non-blocking acknowledgment: the dial settles, a single line fades in ("Logged. I've got it from here."), and the surface eases to its post-check-in resting brightness via `QPropertyAnimation`. No OK button. (Mechanism: a `QLabel` + `QGraphicsOpacityEffect` fade, auto-dismiss `QTimer`.)
- **Density adapts to the answer.** If the dial lands low, the *next* steps render at `layout_density` 0.8 (more air, fewer chips shown at once) and chrome reduces — Hearth literally simplifies itself when you're depleted. When the answer is high/energized, it can show more at once. **This is the one place adaptive density is a clinical feature, not a gimmick — build it here first.**

### 3.4 Signature moments — could ONLY exist in Hearth

1. **The hearthlight that answers you.** As you tell the dial you're sinking, the room around the controls *dims and warms* in real time — the literal "warm corner of the computer" dimming the lights as you go quiet. No other tracker responds to your mood *while you enter it*; everyone else logs and waits. (Conical-gradient dial + animated window `bg_color` property.)

2. **The hand on the shoulder.** When the safety check registers a real urge (self-harm/suicide above a threshold, or mood at the floor), the surface does **not** pop a dialog and does **not** just save. The next-action area softly transforms into a single warm card: *"That's a heavy thing to carry. I'm right here."* with **one** button — *Open the quiet corner* — that routes straight to the Crisis surface, and the breathing/grounding option one tap away. The entry still saves silently in the background. **This closes the duty-of-care gap (2.7) and makes the danger token (`#C85250`, used as a *warm* outline, not an alarm) the most cared-for pixels in the app.** It is the difference between "tracks but doesn't act" and Hearth's entire promise. (Mechanism: `QStackedWidget` swap + `QPropertyAnimation` cross-fade, threshold check on save.)

### 3.5 Copy voice — second person, present tense, a companion who already knows you

| Dead (today) | Hearth |
|---|---|
| "New Mood Entry" | "How are you, right now?" |
| "Mood Level: 5 — Okay" | "Somewhere in the middle." / "Pretty low today." (state-reflective) |
| "Symptoms" | "What came with it?" |
| "Therapy Skills Used" | "What helped you carry it?" |
| "Urges (0=none, 5=strongest)" | "Anything pulling at you?" |
| "Diary card saved." (modal) | "Logged. I've got it from here." (fade-in) |
| "7-day average: --" (empty) | "Two more check-ins and I'll start noticing your patterns." |
| "Export Mood Data" | "Take your record with you" (and demote it — it's not a primary action) |
| "Condition-Specific Sleep Tips" | "For the kind of nights you have" |

Swap test on the new copy: put "MoodFlow" in front of *"Logged. I've got it from here."* — it reads as a lie, because MoodFlow doesn't *do* anything. The copy only works because Hearth actually acts. That's a living point of view.

---

## 4. Quick wins vs. deep rebuilds

### Quick wins (hours — do immediately)
1. **Delete the "matplotlib integration" placeholder** and the four "--" analytics labels; replace the analytics card with a single warm empty-state line until there's real data. (mood)
2. **Pull Self-harm & Suicide out of the urge grid**, ask them last, and route an above-threshold answer to the Crisis tab instead of a "Saved" dialog — even a minimal version closes the duty-of-care gap today. (diary)
3. **Replace all three `QMessageBox.information` save confirmations** with a non-blocking in-surface fade line. (all)
4. **Fix the clipped sleep headers**: make `sleep_widget.py` import and use `gui.components` (`SectionTitle`/`CardFrame`) instead of raw `QGroupBox` + hardcoded `QFont("Segoe UI")`. Removes the clipping and the off-theme font in one move.
5. **Filter the mood symptom list by the active condition** (the profile data is already wired) so a user sees ~8 relevant chips, not 28. Demote the calendar to a small back-date affordance.
6. **Delete the dead low-mood coloring no-op** (`mood_tracker.py:457–462`) and actually color floor-level entries with the `danger` token.

### Deep rebuilds (the real work)
1. **The warming hearth-dial** — custom-painted `QWidget` mood control with animated surface warming tied to `animation_speed_ms`. The new focal point and the signature moment.
2. **Chip-based, condition-filtered, progressively-disclosed check-in flow** replacing all three checkbox/spinbox walls — one adaptive vertical conversation, `QStackedWidget` steps.
3. **Behavioral-token plumbing**: make these widgets actually *read* `layout_density`, `animation_speed_ms`, and `chrome_visibility`, and adapt density/motion to the just-entered state. This is the differentiator; right now it's dead config.
4. **The "hand on the shoulder" crisis hand-off** wired from the safety check into the existing Crisis surface.
5. **Patterns view** (the honest replacement for "Analytics") — built with a real chart, never shown empty, opt-in.

---

*Specificity check: every redesign element above (the warming dial, the hand-on-the-shoulder hand-off, the condition-filtered chips, the "I've got it from here" copy) fails the swap test in the right direction — drop a competitor's name in and it stops making sense, because it depends on Hearth actually acting on what you tell it. That is the line between GENERIC and DISTINCTIVE for this cluster.*
