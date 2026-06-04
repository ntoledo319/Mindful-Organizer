# Audit 04 — Reflective & Therapeutic Surfaces (Journal, Breathe, Meditate)

Surfaces: `src/gui/widgets/journaling_widget.py`, `breathing_widget.py`, `meditation_widget.py`
Screenshots read: `journaling.png`, `breathing.png`, `meditation.png`
Theme tokens: `src/gui/themes.py` (Onyx active)
Verdict: **GENERIC, trending toward broken.** Of the three, Breathe is the most catastrophic because it is the one screen that is supposed to be a *signature moment* and instead renders as a half-loaded light-mode form floating inside a dark app.

---

## 1. What this surface is

These three tabs are Hearth's **slow-down surfaces** — the part of the product that isn't tracking or automating, but *holding*. A person reaches them in one of a few states:

- **Journal:** wants to externalize a churning mind. Often anxious, ruminating, or numb. The job: lower the activation energy of writing to near zero, then get out of the way. Secondary job (load-bearing for this audience): silently watch for self-harm language and route to crisis — which the code does (`_check_risk` → `_surface_crisis_resources`), but the *UI* gives no hint this safety net exists.
- **Breathe:** in acute dysregulation — a panic spike, a racing chest, the moment before a meltdown. The job: **entrain the nervous system**. The screen must *become* the pacer. A breathing exercise that the user has to read, parse, and operate is a breathing exercise that fails the person who needs it.
- **Meditate:** wants a contained, timed pause. Calmer than the other two, but still seeking quiet. The job: set an intention, start a timer, and disappear into a still room.

The common thread: **every one of these is a moment that should slow the user's breathing and heart rate.** The current screens do the opposite — they present forms, sliders, dropdowns, and "Cycle: -- / --" placeholders that demand cognition at exactly the moment cognition is scarce.

---

## 2. Why it fails — forensically

### 2.1 The fatal one: Breathe renders off-theme and half-broken

The screenshot of `breathing.png` shows a **light blue-grey panel sitting inside the dark Onyx app**, with several cards rendered as empty pale rectangles, a header ("Breathing Exercises") barely visible as ghost text at top-left, a "Box Breathing" combo floating with no visible label, and the signature circle reduced to a flat tan disc reading "Ready" over an empty "Cycle: -- / --".

Root cause, in source:

```python
# breathing_widget.py
_CALM_BG = "#e8f4f8"     # hard-coded light blue
_CALM_CARD = "#f0f9fc"   # hard-coded near-white
...
scroll.setStyleSheet(f"QScrollArea {{ background-color: {self._CALM_BG}; }}")
container.setStyleSheet(f"background-color: {self._CALM_BG};")
...
card.setStyleSheet(card.styleSheet().replace(self._theme.get("card_bg","#ffffff"), self._CALM_CARD))
```

This is a **theme bypass.** The widget decided, at author-time, that "calm = pastel blue" and hard-coded it — ignoring the four real themes (Onyx, Alabaster, Slate, Quiet) entirely. The consequences:

- **Principle violated: a theme is a contract.** When the app is in Onyx (near-black `#0F0F11`), every other surface is dark; this one is `#e8f4f8`. The result reads as a rendering bug, not a design choice. To a user, "the breathing screen looks broken" is indistinguishable from "the breathing screen *is* broken" — and for an anxious user, a tool that looks broken is a tool that cannot be trusted to hold them.
- The `.styleSheet().replace(...)` hack assumes the card's stylesheet literally contains the string `card_bg` value. `CardFrame` styles itself via an object-name selector with `card_bg` already substituted, so the replace mostly works — but the empty pale rectangles in the screenshot are cards whose `SectionTitle` text color comes from the *dark* theme (`text` ≈ `#F3F3F4`), i.e. **near-white text on a near-white card**. That is why "Select Exercise," "Recommended," and the exercise-info heading are *invisible ghost rectangles*. This is a direct, measurable WCAG failure (contrast ≈ 1.05:1) caused entirely by mixing one widget's hard-coded light palette with the global theme's light text.
- It also means the must-word is betrayed at the most important moment: the *hearth* — the warm dark room — vanishes and is replaced by a clinical hospital-blue. Pastel medical blue is the exact "wellness app" aesthetic CLAUDE.md bans.

This single decision moves Breathe from "needs polish" to "actively erodes trust." It is the highest-priority fix in the entire cluster.

### 2.2 The breathing circle is not a breathing animation

`BreathingCircle.paintEvent` draws **one flat ellipse** whose radius is a linear function of `_ratio`, with alpha bumped slightly. There is:

- **No easing.** Real breath is not linear — inhale eases-out, the top of the breath holds, exhale eases-in. The code sets `ratio = 0.3 + 0.7 * phase_progress` (a straight ramp). Linear motion reads mechanical; the body does not entrain to a metronome that snaps.
- **No glow, no atmosphere, no depth.** A single `drawEllipse` with a solid `QBrush`. No radial gradient, no soft outer halo, no second concentric guide ring. It looks like a loading spinner that forgot to spin.
- **The animation only exists while a 4-cycle session runs**, then the screen says "Session Ended" and the circle freezes at "Done." The resting state is a dead tan disc labeled "Ready." The thing that should be hypnotic and alive is, 95% of the time, a static blob.
- **Driven by a 50ms `QTimer` repainting the whole widget** rather than a `QPropertyAnimation` on a real animated property. That's both jank-prone and the wrong tool — Qt's animation framework gives you eased curves for free.

**Principle violated:** the differentiator (an immersive, motion-driven pacer) is present in *name only*. A static circle is GENERIC; this is the one place the brief explicitly demands DISTINCTIVE.

### 2.3 Information architecture: the form swallows the practice

All three screens lead with **setup chrome** and bury the practice:

- **Journal** opens with "Prompt of the Day," a category `QComboBox` ("General"), and a "Get New Prompt" button — *three controls before the user can write a word.* The writing box, the actual point, is below the fold of attention. Worse, it is sandwiched between a "Mood before" slider (top) and a "Mood after" slider + a tags `QLineEdit` + two buttons (bottom). Writing a journal entry now requires operating **two sliders, one text field, one combo, and reading a prompt** — a 5-instrument cockpit for the act of typing a sentence.
- **Breathe** stacks: selector card + recommendation card (top row) → exercise-info card → the circle → **pre/post mood sliders** → start/pause/stop → history. The pacer is item four of seven, and the pre/post mood sliders sit *between* the circle and the Start button, so the eye-path to "begin" runs straight through a data-entry form.
- **Meditate** is the worst offender for "form-first": `QGroupBox("Meditation Type")` → duration combo → timer → controls → `QGroupBox("Session Mood")` → `QGroupBox("Recommended Based on Mood")` → `QGroupBox("Recent Sessions")`. Five framed boxes. The screenshot shows clipped group-box titles ("Meditation Type" cut at the top edge, "Session Mood," "Recommended Based on Mood," "Recent Sessions" all sheared by their negative-offset titles).

**Principle violated:** *surface ONE next action.* These screens surface 6–8 competing controls. For a dysregulated user this is a wall of decisions before relief. The mental-health UX lens calls this "hostile."

### 2.4 The pre/post mood sliders are the wrong instrument in the wrong place

All three screens carry **two 1–10 horizontal `QSlider`s** ("mood before," "mood after"). Problems compound:

- **Cognitive tax at the worst moment.** Asking someone mid-panic to quantify their mood on a 10-point scale *before* they're allowed to breathe is clinical data-collection masquerading as care. The product is extracting a metric from a person who came for help.
- **Default 5 is a lie.** Every slider initializes to 5 and most users will never touch it, so "mood_before: 5 → mood_after: 5" floods the dataset with noise while the recommendation engine (`_MOOD_RECOMMENDATIONS`) confidently recommends "Body Scan" off a value the user never set.
- **A raw `QSlider` is a native-Qt tell.** It's a thin groove with a circle handle and a tiny "5" label to the right (visible in all three shots). It says "settings panel," not "I'm checking in on you."

### 2.5 Native-Qt tells everywhere (the "thin coat over raw widgets" problem)

- **Meditation bypasses the design system entirely.** It does **not** import `gui.components`; it defines local `_section_title`, `_body_label`, `_accent_button` and wraps everything in raw `QGroupBox`. Those group boxes, per the global QSS, use a 28px top margin with a `top: -12px` floating title — which is exactly the **clipped/sheared headings** in `meditation.png` ("Meditation Type" sliced at the panel's top edge). The buttons (`Start / Pause / Stop`) are default `QPushButton`s — full-width grey slabs with no hierarchy; Pause and Stop are indistinguishable from Start except for disabled-grey.
- **`QComboBox` dropdowns** for exercise type, meditation type, and duration. A native OS combo with a chevron is the canonical "this is a form" signal.
- **`QListWidget`** for journal history, breathing history, meditation history — three identical empty bordered boxes (the big black void in `journaling.png` under "Journal History"). It's a database table UI for what should be a memory.
- **`QMessageBox`** for "Saved," "Empty," "Session Complete," and even the **crisis resource prompt**. A native modal alert is the most generic surface in all of computing — and routing a *suicide-risk* moment through a stock `QMessageBox.Warning` (triangle icon, "Open crisis plan" / "Close" buttons) is tonally indefensible.

### 2.6 Typography & visual hierarchy

- Everything is `"Segoe UI"` hard-coded in the widgets (`QFont("Segoe UI", ...)`), overriding the theme's actual font stack (`SF Pro Text / Inter / Segoe UI`). On macOS this silently falls back, but the intent — one personality-free sans — is the banned "Tailwind default" feeling. Headings and body are the *same family at different weights*, which CLAUDE.md explicitly bans ("personality-free sans heading + lighter sans body").
- **No type scale that means anything.** `SectionTitle` is 13px DemiBold; "Streak: 0 days" is hand-set to 16px Bold; the meditation timer is 54px. There's no system — sizes are chosen ad hoc per widget. The journal "Journal" page title and "Prompt of the Day" card title are nearly the same weight/size, so the hierarchy is flat (visible in `journaling.png`: the H1 "Journal" barely outranks the card headers).
- The journal writing box placeholder is "Start writing here…" in muted grey — generic, and the only typographic invitation to the core action is a default placeholder.

### 2.7 Color & contrast

- Beyond the Breathe contrast catastrophe (2.1): the Onyx accent `#D9A05B` (warm amber) is used as **button fill with `accent_text` = white**, but `AccentButton._refresh_style` sets text color to `theme["background"]` (near-black) on amber — so "Get New Prompt," "Save Entry," "Export Entries" are dark text on amber. That actually passes contrast, but the *three amber buttons clustered together* (`journaling.png`) read as a row of equally-weighted CTAs with no primary. "Save Entry" and "Export Entries" are visually identical; export is a rare, secondary action dressed as a peer of the primary.
- The breathing circle's color comes from `theme["accent"]` with alpha — in the hard-coded light context it renders as a flat tan, neither warm nor calming, just *muddy*.

### 2.8 Spacing & density

- Journal crams the entire writing experience into a single scrolling column-pair with 12–16px gaps; the editor is `minimumHeight(250)` but visually competes with everything stacked around it.
- Meditation's `QGroupBox`es each add ~28px top margin for the floating title, producing uneven, jittery vertical rhythm and the clipped titles.
- None of the three respond to `theme.layout_density` (the behavioral token exists in `themes.py` and is *ignored* by every widget here).

### 2.9 Motion & feedback

- **Journal:** zero motion. Saving fires a blocking `QMessageBox`. Streak updates with no animation. The mood sliders just snap.
- **Breathe:** the only motion is the linear circle, and only during a session (see 2.2).
- **Meditate:** the 54px timer counts down in plain text with no ring, no progress, no breathing of the numerals. Completion is a `QMessageBox`.
- There is no transition *into* any of these calming spaces — you tab in and the form is just *there*, at full brightness, same as the Tasks screen.

### 2.10 Empty / loading / error states

- **Breathe's resting state literally shows `Cycle: -- / --` and "Ready"** — dev-placeholder dashes shipped as UI. `meditation.png` shows the timer at "10:00" with no session, fine, but history is an empty bordered box.
- **Journal history empty state is a black void** (no entries yet) with the heading "Journal History" floating above nothing. No "your first entry will live here" warmth.
- Errors route through `QMessageBox.warning`. Export-failed, empty-entry, all native alerts.

### 2.11 Copy — swap test

Run the test: *replace "Hearth" with a competitor and see if the copy still works.*

- "Prompt of the Day" — works for any journaling app. **Dead.**
- "Track your mood for personalised recommendations." (breathing recommendation default) — works for any wellness app, and uses a *recommendation-engine* voice, not a companion's. **Dead.**
- "Equal-duration inhale, hold, exhale, and hold pattern. **Used by Navy SEALs** for calm focus under pressure. Activates the parasympathetic nervous system." — this is the opposite of Hearth's voice. "Navy SEALs… under pressure" is *performance/optimization* framing for an audience that is often in crisis; "Activates the parasympathetic nervous system" is a textbook. The never-word is "optimize" and this copy is optimize-coded to the bone. **Hostile, not just dead.**
- "Pre-session mood (1-10):" / "Post-session mood (1-10):" — clinical intake form language. **Dead.**
- "Recommended Based on Mood" / "Set your pre-session mood for a recommendation." — engine voice again. **Dead.**
- "Your meditation session is complete. Please rate your post-session mood." — a survey, not a companion. **Dead.**

The one piece of copy with a pulse is the crisis line ("You're not alone") — and it's trapped in a `QMessageBox`.

### 2.12 Emotional tone for this audience

The cluster reads as **clinical instrumentation**: rate yourself, pick from a dropdown, operate the controls, here's your data back. For someone anxious or in crisis it communicates *"prove your state to the machine before it helps you."* Breathe specifically promises a refuge and delivers a light-blue medical form that looks broken. The warm-dark-room "hearth" feeling is present nowhere in these three screens.

### 2.13 Accessibility

- The Breathe near-white-text-on-near-white-card is a hard WCAG 1.4.3 failure (≈1.05:1).
- `reduced_motion` exists in `ThemeManager` and is **not consulted** by the breathing animation — a user who set reduced motion still gets the 50ms repaint loop.
- Mood sliders have value labels but no accessible names tying label→slider; screen-reader users get "horizontal slider, 5."
- Crisis routing depends on a `QMessageBox` that may not announce well and offers no keyboard-first path.

### 2.14 GENERIC → DISTINCTIVE placement

- **Journal:** GENERIC. A competent journaling form that exists in a hundred apps.
- **Meditate:** GENERIC, trending broken (clipped group-box titles, raw widgets, bypassed design system).
- **Breathe:** **below GENERIC — reads as broken.** And it is the one screen the brief names as a should-be signature. The gap between intent and reality is largest here.

---

## 3. The reimagination — first principles

Design rule for the whole cluster: **the practice is the screen; setup is a whisper.** When a person enters Breathe, Journal, or Meditate, the first thing they see is the invitation to *do the thing*, rendered in the warm dark room. Everything else (mood check-ins, history, recommendations) is secondary, deferred, or eliminated.

### 3.1 Shared moves

1. **Kill the theme bypass.** Delete `_CALM_BG` / `_CALM_CARD`. These surfaces honor Onyx/Alabaster/Slate/Quiet like everything else. "Calm" comes from *layout, motion, and restraint*, not a pastel repaint.
2. **Replace pre/post mood sliders with a single, optional, post-only "one-tap" check-in.** Not 1–10. After a session, three soft glyphs: *lighter / same / heavier* (a single tap, dismissible, never blocking). No "before" — you don't interrogate someone before you help them. This kills four sliders and a recommendation engine fed by garbage defaults.
3. **Adopt the design system in Meditate** (it currently doesn't import it) and **eliminate every `QGroupBox`** — replace with `CardFrame` + a real type scale so titles stop clipping.
4. **Replace `QMessageBox` everywhere** with in-surface, non-modal feedback — and especially route crisis through a dedicated, warm, full-bleed panel (see signature moment 2), never a native alert.
5. **Honor the behavioral tokens.** On entry to any of these three tabs, animate a brief *dim* of the surrounding chrome (the side-nav and header drop to `text_muted` opacity over `animation_speed_ms`) so the room visibly quiets around the practice. Respect `reduced_motion`.

### 3.2 Breathe — the signature rebuild

This is the priority. Target: **a person in panic can open Breathe and, without reading or operating anything, start breathing in under two seconds.**

- **IA:** One full-bleed dark canvas. Centered: the pacer. Below it, one line of instruction ("Breathe in"). That's the entire above-the-fold. The exercise picker collapses to a single quiet word at the top ("Box · tap to change") that opens a sheet only on demand. History and "recommendation" move to a separate, scrolled-away section the panicking user never has to see.
- **The pacer (the signature):** a custom `QWidget` painted with `QPainter` but *driven by `QPropertyAnimation`* on a `pyqtProperty(float)` "expansion" value, using `QEasingCurve.Type.InOutSine` for inhale/exhale and a true hold at the top. Render it as:
  - a **soft radial gradient orb** (warm `accent` core fading to transparent) — a hearthlight, not a flat disc;
  - a **second, slower outer halo ring** that lags the core (parallax breathing), giving depth;
  - the orb's *glow radius and warmth* increase on inhale and settle on exhale, so the screen literally **brightens as you fill your lungs and dims as you empty them** — the room breathes with you.
- **Entrainment over instruction:** the instruction word cross-fades ("Breathe in" → "Hold" → "Breathe out" → "Rest") with `QGraphicsOpacityEffect`; no countdown numbers shouting "4s." The *size and brightness* of the orb is the countdown. Optional: a near-silent haptic-style pulse via a subtle 1px luminance throb at each phase boundary.
- **Resting state is alive, not "Ready."** Before Start, the orb breathes slowly on its own (a calm idle loop). There is no `Cycle: -- / --`. The single CTA is "Begin" — and even that can auto-start after a 3-second idle so a non-clicking user is simply carried into the rhythm.
- **Qt mechanisms:** `QPropertyAnimation` + `QEasingCurve` for the breath; `QSequentialAnimationGroup` to chain inhale→hold→exhale→hold→loop; `QRadialGradient` in `paintEvent`; `QGraphicsOpacityEffect` + `QPropertyAnimation` for instruction cross-fade; consult `theme.animation_speed_ms` and `ThemeManager.reduced_motion` (in reduced-motion, swap the orb scaling for a gentle opacity pulse only).

### 3.3 Journal — the rebuild

- **IA:** the writing surface is the hero, immediately. The prompt is *inside* the empty editor as a soft, italic ghost line you can write straight over or dismiss — not a separate card with a combo and a button. Mood-before is gone. Tags collapse to an optional "+ add a thread" affordance below the text, revealed only after you've written something.
- **The editor:** a borderless, generously-leaded `QTextEdit` on `surface`, max-width measure (~66ch) centered like a page — it should feel like writing in a quiet notebook, not a textarea. Word count fades in only after ~20 words and sits as a faint caption, never a "Words: 0" counter that scolds an empty page.
- **History as memory, not a table:** replace `QListWidget` with a vertical stream of `CardFrame` "leaves" — date, first line, and a single warm dot whose color encodes the *after* feeling. Empty state: one warm line, e.g. "Nothing here yet. The first thing you write stays between us."
- **Crisis is the load-bearing redesign:** when `_check_risk` trips, do **not** open a `QMessageBox`. Instead, the journal surface itself softens — the editor recedes and a warm, full-width panel rises from the bottom (`QPropertyAnimation` on geometry) with one sentence and one large, calm "Open your crisis plan" action plus the hotline, in `danger`-adjacent-but-warm tone. It feels like the room turning toward you, not an OS error.

### 3.4 Meditate — the rebuild

- **IA:** intention first, in one breath. A single line: "Sit for ___ · ___" where the two blanks are inline, low-chrome pickers (duration, type) — no `QGroupBox`, no labels stacked above combos. Below: a **breathing-ring timer** (not 54px plain text). One "Begin."
- **The timer ring:** a custom-painted circular progress ring around the time, where the ring's filled arc *is* the elapsed session, painted in warm `accent` on `divider`, with the numerals exhaling (a 2% scale-breathe on a slow loop) so the still screen is gently alive. Reuse the Breathe orb's gradient language so the two surfaces feel like siblings.
- **One quiet recommendation, in companion voice,** shown only if the user lingers without starting: e.g. "Low on yourself today? Try loving-kindness." — not "Recommended Based on Mood."
- **Completion is in-surface and warm:** the ring completes, the screen dims one stop, and a single line fades in ("Ten minutes. You stayed.") with the optional one-tap after-check-in. No `QMessageBox`.

### 3.5 Copy voice — rewrites

| Current (dead/hostile) | Hearth |
|---|---|
| "Equal-duration inhale… **Used by Navy SEALs**… Activates the parasympathetic nervous system." | "In for four, hold for four, out for four. Steady, like a tide. Follow the light." |
| "Track your mood for personalised recommendations." | (removed — no recommendation gate) |
| "Pre-session mood (1-10):" | (removed) |
| "Your meditation session is complete. Please rate your post-session mood." | "Ten minutes. You stayed." |
| "Prompt of the Day" / "Start writing here…" | (prompt becomes the ghost line) "What's loud right now?" |
| "Current streak: 0 days" | "You've sat here 3 evenings running." (and silent/absent at zero — never shame an empty streak) |

Each passes the swap test: drop a competitor's name in and "Follow the light," "You stayed," and "stays between us" stop making sense, because they only fit a warm-dark-room companion.

### 3.6 Two signature moments (could ONLY exist in Hearth)

1. **The room breathes with you.** During a Breathe session, the *entire window* — not just the orb — gently rises and falls in luminance, synced to the breath: the background lifts a few percent on inhale and settles on exhale, side-nav dimmed. The computer itself is inhaling alongside the user. This is the "behavioral token" idea made literal, and it's the most on-brand thing the product could do. (Qt: animate a top-level overlay `QGraphicsOpacityEffect` / background color on the central widget in lockstep with the orb's animation property.)
2. **Crisis as the room turning toward you.** When journal text trips risk detection, the writing surface doesn't alert — it *softens and leans in*: the page recedes, warmth rises from the bottom edge, and one human sentence with a single calm action appears. No triangle icon, no "Warning," no OK/Cancel. The difference between a companion and a dialog box, at the exact moment it matters most.

---

## 4. Quick wins vs. deep rebuilds

### Quick wins (hours, high impact)
- **Delete `_CALM_BG` / `_CALM_CARD` and the `.styleSheet().replace()` hacks in `breathing_widget.py`.** Instantly fixes the off-theme, invisible-text catastrophe — the single biggest visible defect in the cluster.
- **Make Meditate import `gui.components`** (`CardFrame`, `SectionTitle`, `BodyLabel`, `AccentButton`) and drop the four `QGroupBox`es → fixes the clipped/sheared titles.
- **Remove `Cycle: -- / --` and the "Ready"/"Done" dead states**; give the resting orb a slow idle loop.
- **Cut the "before" mood sliders everywhere; default the engine off** instead of off `5`.
- **Rewrite the Navy SEALs / parasympathetic / "Pre-session mood" copy** into companion voice.
- **Replace the three amber buttons in Journal** with one primary ("Save") and demote "Export" to a ghost/secondary so there's a clear primary action.
- **Honor `reduced_motion`** in the breathing timer (guard the animation).

### Deep rebuilds (the real work)
- The **`QPropertyAnimation` + `QRadialGradient` eased breathing orb**, with the "room breathes with you" luminance sync. This is the signature and worth a dedicated sprint.
- The **crisis panel that rises in-surface** to replace the `QMessageBox` risk path (shared between Journal and anywhere risk language appears).
- **Journal-as-notebook editor** (centered measure, prompt-as-ghost, history-as-stream of cards).
- **Meditate breathing-ring timer** sharing the orb's gradient language.
- **The on-entry "room quiets" transition** (dim chrome via animated opacity) wired to the behavioral tokens for all three tabs.
