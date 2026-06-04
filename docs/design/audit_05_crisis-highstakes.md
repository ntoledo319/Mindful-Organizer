# Audit 05 — Crisis / High-Stakes Surfaces

**Surfaces:** Crisis resources (`crisis_widget.py`), Panic Attack Tracker (`panic_tracker_widget.py`), ERP / Exposure & Response Prevention (`erp_widget.py`)
**Screenshots read:** `/tmp/hearth_ui/crisis.png`, `/tmp/hearth_ui/panic_tracker.png`, `/tmp/hearth_ui/erp.png`
**Reviewer lens:** *A person in crisis using this at 2 a.m.*

> **Defect found before the critique even starts:** the file named `erp.png` does not render the ERP surface — it renders the **Meditation** screen. So the highest-stakes OCD surface in the app could not be visually verified, and whoever generated the screenshot set clearly believed they were looking at ERP when they were looking at a meditation timer. That is itself a damning signal: these surfaces are so visually undifferentiated that even the people building them can't tell them apart. My ERP critique below is therefore sourced from the **code**, cross-checked against the shared visual language visible in `crisis.png` and `panic_tracker.png`, which `erp_widget.py` provably inherits (same `QGroupBox`, `QListWidget`, `QSpinBox`, `QMessageBox` vocabulary).

---

## What these surfaces are

These three screens are the part of Hearth that someone reaches on the worst night of their month. They are not "features." They are the moment the product either earns its entire reason to exist or becomes one more thing that failed a person when they were least able to fight it.

- **Crisis resources** — opened by someone who is, right now, considering whether to stay alive, or close to it. The job: get them to a human being (988, a text line, a friend, their therapist) in as few cognitive steps as physically possible, while making them feel held rather than processed. Their state: tunnel vision, shaking hands, possibly crying, possibly dissociating, executive function near zero. They can read maybe one sentence. They cannot fill out a form. They cannot make a decision between seven options.
- **Panic Attack Tracker** — has two completely different users wearing the same screen. **User A** is mid-attack: heart at 160, can't breathe, convinced they're dying, looking for *anything* to do. **User B** is calm, two hours later, willing to log what happened so patterns emerge. The current screen is built **only** for User B and abandons User A entirely.
- **ERP** — used by someone with OCD deliberately walking into their own worst fear under a structured protocol, holding a compulsion they're trying not to perform. This is voluntary, clinically supervised distress. The job: be a steady metronome and a witness while they white-knuckle through habituation. It must feel like a therapist's calm hand on the shoulder, not a lab instrument logging a specimen.

The unifying truth: **on every one of these screens the user's cognitive budget is near zero and the emotional stakes are near maximum.** That is the exact opposite of the conditions these screens were designed for.

---

## Why it fails — forensically

### 1. Information architecture — the crisis screen makes a drowning person scroll

`crisis.png` is the cleanest case of the core sin. The screen opens with a header, then **Emergency Resources**, then — before anything else useful — **two empty placeholder cards**: "Personal Contacts — No personal contacts added yet. Use Edit to add." and "Professional Contacts — No professional contacts added yet. Add your therapist or psychiatrist." Then **Warning Signs**, **Coping Strategies**, **Reasons for Living**, **Safe Places**, an **Edit** button, and a disclaimer — a single flat scroll of seven cards (`crisis_widget.py:428-449`).

Why this fails (principle: *one screen, one job, surfaced in one glance*): a person at the edge does not scroll. The most important action — **call a human now** — competes for attention with administrative chrome ("Use Edit to add"), self-diagnostic checklists ("Talking about being a burden"), and configuration. **Warning Signs** is actively dangerous here: showing someone in acute distress a checklist of their own deterioration ("Giving away possessions," "Feeling hopeless or trapped") is a mirror held up at the worst possible moment. That content belongs in a *calm-state* safety-plan editor, never on the live crisis screen. The IA has no notion of *now vs. later*; it dumps the entire crisis-plan data model onto one canvas because that was the easy way to render a dict.

The panic tracker has the inverse failure: it is **all "later," no "now."** `panic_tracker.png` shows "Log New Panic Attack," "Statistics," "No panic attacks logged yet," a giant empty History box, and "Log at least 2 entries to see insights." A person mid-panic opening "Panic Log" gets a **data-entry form and a demand for two prior entries before the app will say anything.** The screen's entire surface area is devoted to retrospective analytics. There is no "I'm having one right now" path at all (`panic_tracker_widget.py:192-248`).

ERP's IA is a clinician's spreadsheet: a two-column `QHBoxLayout` (`erp_widget.py:228-245`) with Hierarchy + History on the left and Active Session + Progress on the right — eight controls visible simultaneously (Add/Edit/Remove/Start, SUDS spinbox, Record SUDS, urge spinbox, Log Urge, RP notes, End). During an actual exposure, when the user is supposed to be *staying with the fear*, the UI presents a dense instrument panel that demands attention the protocol explicitly wants pointed elsewhere.

### 2. Visual hierarchy — everything is the same weight, so nothing leads

Across all three, every card is the identical dark rounded rectangle with a 1px border. In `crisis.png` the three life-saving phone buttons get a thin **danger-red outline** — and that is the *only* hierarchy signal on the entire screen. But that red outline reads as a warning/destructive cue (the universal "danger" idiom), which is precisely the wrong emotion: we are framing the lifeline as a hazard. Meanwhile "Reasons for Living" — arguably the single most important card for a suicidal user — gets the same flat treatment as "Safe Places" and the same visual weight as the empty "Personal Contacts" placeholder.

Why this fails (principle: *visual weight must map to life-or-death importance*): when an interface flattens everything to equal emphasis, the user's depleted attention has to do the triage the designer refused to do. On these screens that triage is a cognitive tax we are imposing on someone who has none to spare.

In the panic tracker, the **primary action and the empty state have nearly equal visual weight** — "Log New Panic Attack" is a standard button, the empty History box is a huge bordered void that dominates the viewport. The eye is pulled to the emptiest, least useful element on screen.

### 3. Typography — three fonts, three philosophies, zero intention

This is a forensic tell of an unfinished codebase:

- `crisis_widget.py` hardcodes **`QFont("Segoe UI", ...)`** everywhere (lines 82, 90, 96, 109, 425) — a Windows font that does not exist on the macOS the screenshots were taken on, so Qt silently substitutes, and the type you see is *not the type that was specified*.
- `panic_tracker_widget.py` uses **`self.font().family()`** (line 209) — i.e., whatever the inherited default is.
- `erp_widget.py` goes back to **`QFont("Segoe UI", ...)`** (lines 59, 290, 295).

Meanwhile `themes.py` defines a real font stack (`"SF Pro Text", "Inter", "Segoe UI"...`, line 247) and a real type scale that **none of these three widgets use.** Three widgets, three different typographic sources of truth, none of them the theme. There is no type *system* here — there are local `QFont(...)` calls scattered by whoever last touched each file. The crisis header is 26px DemiBold; the panic title is 18px Bold; the ERP title is 13px Bold. The *most* important screen in the app and the *least* differentiated typographic treatment.

Why this fails (principle: *type is the primary carrier of voice and calm*): inconsistent, accidentally-substituted type makes the app feel provisional. For an audience deciding in real time whether to trust this thing with their life, "provisional" is disqualifying.

### 4. Color & contrast — the lifeline is painted as a threat

The crisis contacts are `transparent` background with a `1px solid {danger}` border that fills red on hover (`crisis_widget.py:485-498`). Red borders are the OS-wide grammar for *delete / error / stop*. We have dressed "988 Suicide & Crisis Lifeline" — the warmest, most human thing on the screen — in the visual language of a destructive action. The hover state inverts to a solid red fill with background-colored text, which at 2 a.m. on a dark screen reads as alarm, not comfort.

Beyond that single red accent, the palette is **monochrome charcoal**. Hearth's own identity word is *hearth* — warmth, firelight, refuge. The accent token is literally a warm amber (`#D9A05B`, themes.py:80). **None of that warmth appears on the one screen that most needs it.** The crisis screen is the coldest screen in the product.

### 5. Spacing & density — calm is claimed in the docstring, contradicted by the layout

`crisis_widget.py`'s docstring says "large, calm, distress-friendly." The reality: seven stacked cards at 16px spacing (line 418), the warning-signs card alone listing seven items, coping strategies listing eight numbered items — a *wall* of text the moment you scroll past the contacts. The panic dialog (`_PanicLogDialog`) stacks **12 symptom checkboxes + 9 technique checkboxes + a spinbox + a line edit + a spinbox + a text box** in one 450px-wide modal (lines 80-134). That is ~25 interactive targets in a single dialog presented to someone who may be mid-attack. "Calm" is asserted in a comment and refuted by every layout decision.

### 6. The actual widgets — raw native Qt, thinly painted

Every native-Qt tell from the app-wide critique is present and concentrated here:

- **`QGroupBox`** with floating uppercase titles ("STATISTICS," "HISTORY," "INSIGHTS" in `panic_tracker.png`) — these are the clipped, half-cut labels visible at the top of the empty cards. That clipping is the `QGroupBox::title` negative-top-margin (`themes.py:519-526`) fighting the card border. It looks broken because it *is* fighting itself.
- **`QListWidget`** for history (panic + ERP) and **`QListWidget`** for the ERP hierarchy — rendering crisis/clinical data as OS list rows with `[2026-05-30T14:22] Distress: 7/10 — Trigger: ...` (`panic_tracker_widget.py:267`). This is debug output, not a designed timeline.
- **`QSpinBox`** with native up/down steppers for distress, SUDS, urge, duration — asking a panicking person to fiddle a tiny stepper to enter "7."
- **`QMessageBox.information(...)`** for the SUDS check prompt **interrupting an active exposure with a modal OS alert** (`erp_widget.py:489-494`) — a system pop-up, mid-exposure, is the single most jarring possible interruption for an OCD user trying to habituate. And `QMessageBox` for "Select an item first" (lines 410, 429, 449) — native scolding dialogs.
- **`QToolTip`** as the *only* feedback when a crisis contact is tapped (`crisis_widget.py:62-65`). The most important interaction in the app — tapping the suicide lifeline — confirms itself with a **transient OS tooltip that vanishes on mouse-move.** A person in crisis taps 988 and the only acknowledgment is a hover bubble they may never see.

Why this fails (principle: *raw OS widgets carry the OS's emotional tone, which is bureaucratic, not caring*). These are spreadsheet controls wearing a dark coat. On a crisis surface, the medium is the message, and the medium here says "form."

### 7. Interaction & feedback — the lifeline tap has no real confirmation

`_activate_contact` (`crisis_widget.py:48-65`) copies the number to clipboard, fires a best-effort `tel:` URL, and shows a tooltip. On desktop, `tel:` usually does nothing. So the realistic outcome of tapping "988" is: *a tooltip appears and disappears.* No dialer, no big calming "Calling 988…" state, no "Here's the number, large, tap to copy again," no fallback path. For the single highest-stakes tap in the entire product, the feedback is the **weakest** feedback primitive Qt offers.

The panic tracker's only interaction is "open a modal form." The ERP's interactions are a battery of Record/Log buttons that give no visible confirmation that anything was recorded except a new gray list row.

### 8. Motion — none where it would save a life, none where it would soothe

There is zero motion design on any of these surfaces. That is a *missed* opportunity, not just an absence:
- A panicking user needs a **breathing pacer** — a slow, physically entraining expand/contract they can match their breath to. The app has a "Breathe" tab elsewhere, but the panic surface — where breathing is the actual intervention — has none.
- An ERP user needs a **calm passage-of-time** signal so the timer feels like a tide going out (habituation) rather than a stopwatch. Instead there's a hard digital `00:00:00` ticking up (`erp_widget.py:294-296`), which for an anxious user reads as a *countup of suffering*.

### 9. Empty / loading / error states — the empty states are hostile

- Crisis: two empty cards that say "Use Edit to add" — instructing a person in crisis to go configure the app.
- Panic: "No panic attacks logged yet" + "Log at least 2 entries to see insights" — the app's first words to a new, possibly panicking user are a **demand for data it doesn't have.** The empty state gatekeeps usefulness behind homework.
- ERP: `--` placeholders ("Predicted SUDS: --", "Avg SUDS drop per session: --", `erp_widget.py:302, 366`) — literal dev-placeholder dashes shown to the user. Empty `QListWidget`s with no guidance.

Why this fails (principle: *the empty state is the first impression, and it should give, not ask*). Every one of these empty states extracts something from the user (configuration, prior data, patience) before offering anything.

### 10. Copy — run the swap test

- **"Crisis resources"** (header). Swap test: rename the product to "BetterHelp" or "Calm" — the header still works perfectly. **Dead copy.** It's a database category label, not a voice.
- **"Emergency Resources," "Personal Contacts," "Professional Contacts," "Warning Signs Checklist," "Coping Strategies"** — every one is a clinical taxonomy heading. This is the language of an intake form, not a companion. Hearth's identity says *never* feel like "corporate mindfulness software"; these headings are exactly that.
- **"No personal contacts added yet. Use Edit to add."** — software talking about itself, in crisis.
- **"Log panic attacks to identify patterns, triggers, and which techniques help you most."** — swap-test passes for any mood tracker on the App Store. Generic.
- **"Log at least 2 entries to see insights."** — a system constraint stated as a wall.
- ERP disclaimer: *"This tool is for tracking and support, not a substitute for professional support."* — "support... support" repeats; it's boilerplate legal hedging, not reassurance.

There is **not one sentence** on any of these three screens that could only exist in Hearth. The must-word *hearth* appears zero times. The voice is "clinical SaaS," which the project identity explicitly forbids.

### 11. Emotional tone — processing, not holding

Add it up: red-as-threat lifelines, a deterioration checklist shown during crisis, "Use Edit to add," a homework gate, native scolding dialogs, `--` placeholders, tooltip-only confirmation, a stopwatch counting up your suffering. The aggregate emotional message is: *"You are a record to be maintained."* For an audience that is sometimes deciding whether to stay alive, that tone is not just off-brand — it is a small betrayal at the exact moment trust matters most.

### 12. Accessibility — fails the people most likely to be here

- **Hardcoded fonts and font sizes** in all three widgets ignore the theme's `font_scale` (`themes.py:238`), so a user who set larger text in settings gets **default-size crisis text anyway**. The people who most need large text — distressed, possibly crying, possibly older — are the ones this screen serves, and it ignores their setting.
- **Color-only meaning:** the red border is the sole differentiator of the lifeline buttons; under the colorblind overrides (`themes.py:172`) or for a low-vision user, that signal degrades.
- **`QToolTip`-only feedback** is invisible to screen readers and keyboard users.
- **Tiny `QSpinBox` steppers** are a motor-control nightmare for shaking hands.
- The crisis contact text (`"988 Suicide & Crisis Lifeline\n988"`) renders in `crisis.png` as `988 Suicide _Crisis Lifeline` — the ampersand is being eaten as a Qt mnemonic accelerator (`&` → underlined accelerator). **The name of the national suicide lifeline is visually corrupted on screen.** That is the most important string in the product and it is broken.

### 13. Where it lands: GENERIC → DISTINCTIVE

**GENERIC, bordering on broken.** Strip the dark coat and these are stock PyQt examples: `QGroupBox`, `QListWidget`, `QSpinBox`, `QMessageBox`, `QToolTip`. Every screen passes the swap test (works unchanged for any competitor). The must-word never appears. The one attempt at hierarchy (red borders) communicates the wrong emotion. **This is the lowest-scoring cluster in the app precisely because the stakes are highest** — the gap between "what a person in crisis needs" and "what this delivers" is at its maximum here.

---

## The reimagination — Hearth at 2 a.m.

**First principle:** these screens are not databases with a UI. They are a *hand reaching back.* The design north star: **at any moment of these flows, a stranger glancing at the screen for one second should be able to do the single right next thing.** Everything else is hidden until the user is calm enough to want it.

### Crisis — "Stay" (one screen, one breath, one human)

Rename the surface. Not "Crisis resources" (a category) — **"Stay."** One word. A request and a promise. The nav item already lives at the bottom in danger tone; keep it always reachable via a global shortcut (e.g. a persistent footer ember + `Ctrl/Cmd-period`), so it's never more than one keystroke away from anywhere in the app.

**Layout — a single, warm, full-bleed canvas, not a card stack.** Replace the `QScrollArea` of seven cards with a **custom-painted `QWidget`** (`paintEvent` with `QPainter`) that fills the viewport in the theme's warm dark, with a faint, slow **radial ember glow** behind the content — the literal hearthlight. No borders. No cards. Just calm space.

**The hierarchy, top to bottom, is ruthless:**

1. **One sentence, large, human, centered:** *"You don't have to get through this alone right now."* (custom `QLabel`, theme type scale, ~28px, `text_muted` warmth). This is the first and possibly only thing they read.
2. **One primary action, enormous:** a single, full-width, **warm** (amber `accent`, not red) button — **"Call 988 — talk to someone now."** Min height 96px. Tapping it must produce a *real, unmissable, persistent* response (see signature moment). Below it, equally large but secondary: **"Text instead"** (741741) and **"Call a person I trust"** (only if a personal contact exists — otherwise this slot is silent, never an empty "add" placeholder).
3. **A quiet third tier, optional:** *"Or stay here with me for a minute"* → reveals the breathing pacer + the user's own pre-written reasons-for-living, one at a time, gently. Nothing clinical. No warning-signs checklist — **that content is moved entirely into a calm-state "Safety plan" editor reached only from Settings, never shown live.**

**Reasons for Living becomes the emotional core, not a flat list.** When the user opted in (calm state) to add reasons, surface them here **one at a time**, large, fading in slowly (`QPropertyAnimation` on opacity), like someone quietly reminding you. The user's *own words*, in their *own handwriting-weight* type, are the most powerful possible content on this screen — and they cost nothing to render with dignity instead of as `  Add your personal reasons here...` bullet rows.

**Color:** the lifeline is **warm amber, never red.** Reserve red exclusively for genuine "this is an emergency, here is 911"-level escalation, and even then framed as care. The screen should feel lit from within, like the last warm room in a cold house.

**Copy voice** (every line passes the swap test — it could only be Hearth):
- Header: *"Stay."*
- *"You don't have to get through this alone right now."*
- Button: *"Call 988 — talk to someone now"* (not "Emergency Resources").
- After a call attempt: *"The number's on your clipboard too — 988. We're not going anywhere."*
- The disclaimer, rewritten from legalese to a hand on the shoulder: *"Hearth sits with you, but it can't be your doctor. If you're in danger right now, please call 988 — they're awake and they're for exactly this."*

> **SIGNATURE MOMENT #1 — "The line is open."** When the user taps the lifeline, do not flash a tooltip and pray `tel:` works. Transition the *whole screen* into a calm **"reaching out" state**: the ember glow brightens and begins a slow, steady pulse (a heartbeat at ~60bpm, paced *below* the user's panic rate to physiologically pull them down — `QPropertyAnimation` looping a `pulse` property driving `paintEvent`). The number renders **huge and tappable-to-copy**, with *"If the call didn't start, dial 988 — I've copied it for you."* A soft, persistent "We're connecting you to a person" line stays until dismissed. This is feedback proportional to the stakes, and it is *unmistakably Hearth* — warmth as an interface state. No other app turns its entire crisis screen into a slowing heartbeat when you reach for help.

### Panic — split the screen by *state*, not by feature

The fatal flaw is one screen serving two opposite users. Fix it at the IA level: the panic surface **opens in "now" mode** and only reveals "later" mode when the storm has passed.

**"Now" mode (default landing):** the entire viewport is a **breathing pacer** — a custom-painted circle that expands and contracts on the 4-7-8 rhythm (`QPropertyAnimation` driving radius in `paintEvent`), with the gentlest possible guidance fading in and out: *"In… hold… out…"* Underneath, one line: *"This will pass. It always has. Breathe with the light."* A single low-key control: **"It's easing — log what happened"** that *transitions* (not navigates) into "later" mode. **No form, no checkboxes, no spinboxes are visible while someone is panicking.** The act of breathing with the pacer *is* the feature.

> **SIGNATURE MOMENT #2 — the pacer remembers you.** Over time, Hearth learns the user's actual average attack duration from their own logs. The pacer's copy adapts: instead of generic reassurance, it says *"Your panic attacks have lasted about 11 minutes. You're roughly halfway. Keep breathing."* — turning their own data into a lifeline (*"you have survived this exact thing N times"*) instead of a chart they have to assemble. This is the behavioral-token idea applied to crisis: the UI adapts to the *individual's* history. No generic tracker can say this sentence.

**"Later" mode (the log):** *now* you can show the structured capture — but redesigned. Replace the 25-control modal with a **gentle, one-question-at-a-time flow** (a `QStackedWidget` wizard): peak distress as a single large draggable arc (custom widget, not a `QSpinBox`); symptoms as **large toggle chips** in a soft `FlowLayout` (not a checkbox column); "what happened just before?" as one calm text field. Each step is one decision. The history list becomes a **custom-painted timeline** of warm dots sized by distress, not `QListWidget` rows of ISO timestamps. The empty state gives instead of asks: *"Nothing logged yet — and that's fine. When the next wave comes, breathe here first. Logging can wait."*

### ERP — "The session is a tide, and I'm the witness"

ERP's job is to be a *steady, low-key presence* while the user white-knuckles an exposure. Re-architect from "instrument panel" to **two modes: planning (calm) and in-session (minimal).**

**Planning mode:** the hierarchy is a real, custom-painted **ladder** — rungs sorted by SUDS, the user climbing from the bottom. Each rung shows its title, predicted distress as a warm fill bar, and how many times they've faced it. This replaces the `QListWidget` of `SUDS 050 | ... (3 sessions)` debug rows. Adding a rung is a quiet inline flow, not a `QDialog`.

**In-session mode — radical subtraction.** When an exposure starts, **collapse the entire instrument panel.** The screen becomes almost empty: the exposure name, a **soft, breathing timer** (rendered as a slowly filling arc, not `00:00:00` — time should feel like a tide going *out*, not a stopwatch counting *up*), and the gentlest possible prompt. The SUDS check **must never be a `QMessageBox`** — replace it with a non-modal, slow, warm in-canvas prompt that fades in at the edge: *"When you're ready — how high is it right now?"* with a single large draggable arc, so logging never yanks the user out of the exposure. RP notes and urge logging collapse behind a single "I felt an urge" affordance that the user can tap without losing focus, with a quiet confirming glow (*"Resisted. That's the whole point — well done."*).

**The habituation curve is the hero, drawn live.** As SUDS points come in, paint them in real time as a **descending warm line** — so the user *watches their own anxiety fall* during the session. That live, falling curve is the entire emotional payoff of ERP, and right now it's buried in a `QListWidget` and a `--` placeholder. Custom `paintEvent` charting; no matplotlib, no native list.

**Copy voice for ERP** (witness, not instrument):
- *"You chose to face this. That's the brave part — the rest is just staying."*
- Timer/arc label: *"Stay with it. The fear always comes down. Watch."*
- On end: *"You stayed N minutes and the fear fell from 80 to 35. That's habituation. That's you teaching your brain it's safe."*
- Disclaimer, de-lawyered: *"Do this alongside your therapist — they're the map, Hearth is the metronome."*

### Adaptive (behavioral-token) behavior across all three

The theme system already carries `layout_density`, `animation_speed_ms`, and `chrome_visibility`. Use them as *behavioral* tokens on these surfaces:

- **Crisis & panic surfaces force `chrome_visibility="minimal"` and `layout_density` toward spacious regardless of the user's normal setting** — when distress is detected (or simply because it's the crisis tab), the OS-level idea of Hearth ("the computer adapts to your state") becomes literal: nav recedes, density drops, type grows. This is the one place in the app where the product's entire thesis is provable in a single screen.
- Respect `reduced_motion` (`themes.py` flag) — the breathing pacer and heartbeat must have a calm static fallback (a steady glow, a held instruction) for users for whom motion is itself activating (PTSD, vestibular).

### Qt mechanisms (so an engineer can build it)

- **Custom-painted canvases** (`QWidget.paintEvent` + `QPainter`, `QRadialGradient` for ember/hearthlight) replace the card stacks — this is where "warm corner of the computer" actually gets rendered.
- **`QPropertyAnimation` / `QVariantAnimation`** on custom `pyqtProperty` floats drive: the heartbeat pulse, the breathing pacer radius, reason-for-living crossfades, the filling timer arc, the live habituation curve.
- **`QStackedWidget`** for now/later (panic) and planning/in-session (ERP) mode switches — these are *mode changes*, not navigations.
- **In-canvas, non-modal prompts** (a translucent overlay widget animated in/out) replace every `QMessageBox` on these surfaces. **No native modal ever interrupts a panic or an exposure.**
- **A `FlowLayout`** (the standard Qt example layout) for symptom/technique chips replaces checkbox columns.
- Kill `QToolTip` as confirmation; kill hardcoded `QFont("Segoe UI", N)` — pull type from the theme scale and honor `font_scale`. Fix the `&` mnemonic bug now (`QLabel`/`QPushButton` text containing `&` must escape to `&&` or set `setTextFormat`/disable mnemonics) so "988 Suicide & Crisis Lifeline" renders intact.

---

## Quick wins vs. deep rebuilds

**Quick wins (hours, do immediately — these are bordering on bug-fixes on a life-safety screen):**
1. **Fix the `&` mnemonic corruption** so "988 Suicide & Crisis Lifeline" renders correctly. *This is a one-line fix on the single most important string in the app.*
2. **Recolor crisis contacts from red to warm `accent`** — stop painting the lifeline as a threat. Pure QSS change.
3. **Remove "Warning Signs," "Personal/Professional Contacts" empty placeholders, and the Edit button from the live crisis screen.** Move warning-signs and editing into a calm-state safety-plan editor. Elimination-before-addition; instantly calmer.
4. **Replace `QToolTip` call confirmation with a persistent in-screen confirmation panel** ("988 is on your clipboard. Dial it now.").
5. **Rewrite all headers/copy** to Hearth voice ("Stay," "talk to someone now," etc.) — pure string changes, zero engineering risk, and the single highest taste-per-hour move available.
6. **Replace ERP's `QMessageBox` SUDS prompt** with a non-modal in-canvas prompt — stop yanking users out of exposures.
7. **Honor `font_scale`** in all three widgets (delete hardcoded sizes, read theme).

**Deep rebuilds (the real work):**
- The **"Stay" canvas** with ember glow + slowing-heartbeat signature moment (custom paint + animation).
- The **panic "now/later" split** with the breathing pacer and the *"you're roughly halfway"* adaptive copy (`QStackedWidget` + custom pacer + history-derived duration).
- The **ERP planning/in-session split** with the live, falling habituation curve and the radical in-session subtraction.
- Custom-painted **timeline / ladder / curve** widgets replacing every `QListWidget` and `QSpinBox` on these surfaces.
- The **adaptive behavioral-token behavior** (forced minimal chrome + spacious density on distress surfaces) — the proof of Hearth's thesis.
