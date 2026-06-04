# Audit 02 — Dashboard / "Today"

**Surface:** the home / daily anchor tab
**Source:** `src/gui/widgets/dashboard.py`
**Screenshot read:** `/tmp/hearth_ui/dashboard.png`
**Verdict on the GENERIC → DISTINCTIVE scale:** sits at **GENERIC**, leaking toward SAFE-GOOD only because the copy occasionally has a pulse. This is the single most important screen in the product and it is currently a status board, not a hearth.

---

## What this surface is

"Today" is the first thing the user sees every time they open Hearth. It is the **daily anchor** — the room they walk into. The product's entire thesis lives or dies here: *your computer adapts to your psychology.* If this screen does not visibly adapt, the thesis is a lie and everything downstream is just another tracker.

**The user's state when they arrive is the whole design problem.** They are not a "user with a session goal." They are a person who is drained, anxious, dissociating, hypomanic, or in the early minutes of a bad morning. They opened a desktop app *instead of* doing the thing they're avoiding. Some non-trivial fraction opened it because something is wrong and they don't have words for it yet.

**The job this screen must do, in priority order:**
1. Lower the user's heart rate. Make the room feel prepared for them (the "chair test" from `00-aesthetic-profile.md`).
2. Surface exactly **one** next action — never a menu of judgments.
3. Reflect their state back to them honestly and warmly, so they feel *seen* without being *diagnosed*.
4. Keep crisis access one motion away, always, without shouting it.

The current screen does the opposite of all four. It raises arousal, presents a five-way decision, reports status like a CI dashboard, and buries crisis in the left rail under "Library."

---

## Why it fails — forensically

### Information architecture — a status board pretending to be a companion

The screen is, top to bottom: **upsell banner → greeting → "Right now" → "Next action" → 5 quick-action buttons → "Briefing" → "Context" (4 lines) → "Suggestions" (3 bullets)**. That's **eight stacked sections** before the user has done anything. The class even names its own method `_build_sections()` and calls nine builders in a row (`dashboard.py:110-122`). Nine.

- **The first thing the user sees is a sales pitch.** `_build_tier_banner()` (`dashboard.py:126`) renders *above* the greeting (`_build_sections` order, line 112 before 114). A person who opened a mental-health app is greeted by "Free plan. Start a 14-day trial." This is the "journal with ads" failure mode named explicitly as forbidden in `CLAUDE.md`. **Principle violated:** the first pixel sets the emotional contract. Hearth's contract is *refuge*; an upsell makes the contract *commerce*.
- **"Right now," "Next action," "Context," and "Suggestions" are four cards that all answer the same question** ("what should I do?") in four different registers. "Right now" says *"Energy forecast is available. 2 open tasks need a decision."* "Next action" says *"Add one task or record how you feel."* "Context" says *"Tasks: 0 due today; 0 overdue; 1/3 completed."* "Suggestions" says *"Start with a small, low-energy task."* The user has to **read and reconcile four overlapping summaries** to extract one instruction. **Principle violated:** cognitive load minimization. For a drained or anxious person this is not information — it's homework.
- **There is no single focal point.** Every card has identical weight: same `CardFrame`, same 16px padding (`card.py:18`), same border, same radius, same internal `SectionTitle` + `BodyLabel`. The eye has nowhere to land. **Principle violated:** "information hierarchy follows emotional hierarchy" (`00-aesthetic-profile.md` line 29). Here hierarchy is *flat*, so emotional hierarchy is *flat*, so the screen feels like a busy office, not a chair.

### Visual hierarchy — everything is a gray rectangle

Look at the screenshot. It is a vertical stack of **five near-identical dark rectangles** of slightly different heights, each with a small bold white title and gray body text. The accent color (`#D9A05B`, the warm hearthlight amber) appears in exactly **three throwaway places**: the active nav pill, the "Add task" button, and the "Start trial" button. The one color that carries the brand's entire warmth is spent on *a CTA for a paid tier.*

- **No size contrast in the body.** "Right now" body is 16px (`dashboard.py:260`), "Next action" is 15px (line 270), everything else is the default 13px from `BodyLabel` (`typography.py:58`). These differences are invisible at a glance — they read as one uniform gray paragraph spread across five boxes.
- **The most important sentence on the screen — the one true next action — is visually indistinguishable from the tier badge text.** Both are gray, both are ~13-16px, both sit on the same surface. **Principle violated:** the thing that matters most must look like it matters most. Nothing here does.

### Typography — the serif never shows up

The aesthetic profile is unambiguous (`00-aesthetic-profile.md` line 24-25): **a serious serif with warmth for anything the user reads.** This screen renders 100% in the system humanist sans (`"SF Pro Text", "Inter"…` per `themes.py:247`). The greeting "Today, Alex" — the one line that should feel like someone speaking to you — is a 28px DemiBold sans (`dashboard.py:214-217`), identical in feel to a Linear page header. **Principle violated:** the reference test and the anti-reference test. A Headspace user could mistake the type for Headspace; a Notion user could mistake it for Notion. There is no Hearth in this typography.

The greeting also uses **a hardcoded `QFont` with raw px in inline stylesheet** (`dashboard.py:214-217`), bypassing the `[class="header"]` token in `themes.py:319`. So the one heading is both off-brand *and* off-system.

### Color / contrast — the warmth is locked in a drawer

- Body text is `text_muted` (`#8E8E93`) on `surface` (`#18181A`). That's a measured contrast of roughly **4.0:1** — under the WCAG AA 4.5:1 floor for normal text. The *entire* informational payload of this screen (every Context line, every Suggestion, the "Right now" sentence) is set in `BodyLabel`, which defaults to `secondary`/`text_muted` (`typography.py:57`). **The screen's content fails AA for the exact population most likely to be using it at 2am with the brightness down.**
- The accent (`#D9A05B`) — described in tokens as the warm hearthlight — touches *nothing emotional.* It touches a sell button and a task button. **Principle violated:** "no decoration-driven design; every visual choice serves meaning" (`CLAUDE.md`). The single most meaningful color is doing the least meaningful job.

### Spacing / density — calm on the surface, dense underneath

The 18px section spacing and 920px column (`dashboard.py:102-105`) read as restrained at first. But the *Context* card crams four facts into four stacked lines ("Mood has not been recorded today. / Energy: forecasting is available with Pro. / Tasks: 0 due today; 0 overdue; 1/3 completed. / Values report unavailable."), and *Suggestions* stacks three bullets. That's **seven discrete data points in two cards**, every one of them a small judgment. The density isn't in whitespace — it's in *decisions per square inch.* **Principle violated:** "surface ONE next action." This surfaces ten.

### The actual widgets — native-Qt tells everywhere

- **Cards are flat `QFrame` + QSS border** (`CardFrame`, `card.py`). No elevation, no shadow (the `shadow` token in `themes.py:91` is defined and never used), no warmth, no texture. They are literally `border: 1px solid #2C2C2E; border-radius: 6px`. This is the default "draw a box" gesture. **Specificity test: could this card exist in any Qt app unchanged? Yes. → It's wrong.**
- **The radius is inconsistent with the system.** `CardFrame` hardcodes `radius=6` (`card.py:18`), while the theme system specifies `border_radius=12` and `QFrame[class="card"]` uses `radius * 1.5 = 18` (`themes.py:511`). So the dashboard's cards are visibly sharper-cornered than the design system intends — a drift bug that reads as "unfinished."
- **The buttons are off-system too.** `_ThemedButton._refresh_style` hardcodes `border-radius: 5px` (`buttons.py:43`) — a *third* radius value on one screen (5 / 6 / 12/18). And `GhostButton` overrides its own constructor's style inline (`buttons.py:91`), so the quick-action row is five boxes drawn by a different hand than the cards.
- **The "Refresh" button exists at all.** `GhostButton("Refresh")` (`dashboard.py:229`) sits next to the date. A *manual refresh button on a home screen* is a confession that the app doesn't update itself reactively — even though it literally has a `state_bus` that already pushes `mood_logged`, `energy_updated`, `task_changed` (`dashboard.py:639-641`) plus a 5-minute timer. The button is a native-Qt tell for "we didn't trust our own reactivity." **It should not exist.**

### Interaction & feedback — nothing responds to anything

- Clicking a quick action emits a signal (`dashboard.py:250`) that navigates away. There is **no transition, no acknowledgment, no state change on this surface.** You press "Record mood," the screen vanishes, you come back, and *one gray line changed* in the Context card. The user is never shown that their action *did something here.*
- **No hover affordance on the cards** — they aren't interactive, yet they look exactly like the things that are (same surface as inputs per `themes.py:439`). Ambiguous affordance for an audience that needs certainty.
- The crisis banner (`_build_crisis_banner`, line 180) renders as a **flat warning-orange `#F39C12` bar with black bold text** — and it's `setVisible(False)` by default, injected mid-stack between Welcome and "Right now." So in a crisis, an *orange box with `color:#333` bold text* shoves the layout down. **Principle violated:** crisis UX must be calm and instantly legible, not an alarm-colored content shift. Orange-on-black bold is the visual language of a cookie warning, not care.

### Motion — there is none

Zero animation on this surface. The theme defines `animation_speed_ms` (`themes.py:34`) and the brief demands motion that "feels like turning a page" (`00-aesthetic-profile.md` line 33). The dashboard never uses `QPropertyAnimation` once. Cards appear instantly, refresh snaps text in place, navigation is a hard cut. **Principle violated:** the motion test. Nothing here turns a page; everything here blinks.

### Empty / loading / error states — failure is rendered as a status report

This is the most damaging failure for a fragile audience. When the app has no data (the default first-run state, which is *exactly* what the screenshot shows), the screen reports its own emptiness as a series of small absences:

- "Mood has not been recorded today."
- "Energy has not been forecast yet." / "Energy: forecasting is available with Pro."
- "No task pressure is visible yet."
- **"Values report unavailable."** ← (`dashboard.py:281`)

**"Values report unavailable" is a dev placeholder in a mental-health app's home screen.** It reads like a 503. To a depressed user, four lines of "not recorded / unavailable / not yet" is a **checklist of things they've failed to do**, rendered the moment they open the app. **Principle violated:** for this audience, an empty state is not neutral — it is either an invitation or an accusation, and this one accuses. Errors are swallowed silently into `logger.debug` (`dashboard.py:352`, 401, 481, 568, 596) and the stale text just sits there, so a *broken* state and an *empty* state are indistinguishable to the user.

### Copy — swap test results

Run the swap test from `CLAUDE.md` (replace "Hearth" with a competitor; if it still works, the copy is dead):

| Current copy | Swap test | Verdict |
|---|---|---|
| "Free plan. Start a 14-day trial for insights, smart notifications, and reports." | Works verbatim for any SaaS. | **DEAD.** Generic.
| "Energy forecast is available. 2 open tasks need a decision." | "need a decision" → mild pressure language. Works for any to-do app. | **DEAD.**
| "Add one task or record how you feel. That gives Hearth enough context to help." | Only line with the brand name baked in. Survives the swap *only because of the proper noun* — which is cheating. | **WEAK.** The sentiment is generic; the name is load-bearing.
| "Values report unavailable." | A 500-page error. | **HOSTILE.**
| "Suggested skill: …" / "Briefing" | "Briefing" is corporate-ops language (a CMO gets a briefing). | **DEAD + off-tone.**

None of this copy could *only* exist in Hearth. It's competent product-speak. The aesthetic profile demands a voice that "could a thoughtful adult say this to another thoughtful adult in a quiet room" (`00-aesthetic-profile.md` line 57). "2 open tasks need a decision" is not that. It's a Jira notification wearing a sweater.

### Emotional tone — it performs neutrality, which reads as cold

The screen is *trying* to be calm by being gray and quiet. But quiet-gray-with-status-text isn't calm — it's **flat affect.** There is no warmth anywhere: no hearthlight, no soft focal glow, no sense that the room dimmed itself for you. The brand promise is "the warm corner of the computer." This is the *fluorescent* corner. **Principle violated:** the project must NEVER feel like a dashboard (`CLAUDE.md`); this is, structurally and visually, a dashboard.

### Accessibility

- Body content fails AA contrast (above).
- Three competing border radii (5/6/12-18) and inline styles scattered across `dashboard.py`, `buttons.py`, `card.py` mean **font-scale and high-contrast modes won't propagate** — the inline `font-size:13px` in `BodyLabel` (`typography.py:58`) ignores `self.font_scale` entirely. A user who bumped their font scale gets a half-scaled screen.
- The crisis banner uses color (orange) as its only signal and `color:#333` on it — likely failing contrast *and* color-independence (`themes.py` color-blind overrides never touch this hardcoded `#F39C12`).
- No semantic heading structure for screen readers; everything is a `QLabel`.

### Where it lands: **GENERIC.**
Strip the word "Hearth" from two sentences and this screen is indistinguishable from any competent dark-mode productivity app. It fails the specificity test on every component.

---

## The reimagination

**First principle:** the dashboard is not a place that *reports* the user's state. It is a place that *holds* it. The screen should feel like the app already looked at you and arranged the room. One thing in focus. Everything else hushed at the edges. The behavioral tokens already in `themes.py` (`layout_density`, `chrome_visibility`, `animation_speed_ms`) are the mechanism — they are currently defined and **never read on this surface.** That's the whole opportunity.

### New information architecture: one breath, one line, one door

Collapse eight sections into **three zones**, vertically, in one column, no cards:

1. **The Hearthlight** (top, ~40% of viewport). A single calm focal element — see signature moment #1 — that *is* the user's state, rendered as light, not text. Under it, **one sentence** in the warm serif: the greeting fused with the single true reading of right-now. e.g. *"Morning, Alex. You haven't said how today feels yet."* or, with data, *"You're running low this afternoon, Alex. Nothing here is urgent."* This replaces Greeting + Right now + Context + Briefing — **four cards become one sentence and one glow.**

2. **The one door** (center). A single, large, warm primary action — *the* next action, computed exactly as `_refresh_next_action()` already does (`dashboard.py:432`), but rendered as **one obvious thing to touch**, not as button #2 of 5. Its label is the action in plain voice: *"Start with: rename the export file"* or, when empty, *"Tell me how today feels"* (which opens mood, the highest-leverage first signal). The other four actions don't vanish — they recede into a quiet horizontal row of **text-only ghost links** below the door, visually subordinate (smaller, `text_muted`, no borders), so the hierarchy is unmistakable: one door, four side-doors.

3. **The mantel** (bottom, optional, scroll-to-reveal). If — and only if — there is something genuinely worth saying (an overdue task, a 7-day mood dip, a med reminder), one quiet line sits here in serif. Otherwise this zone is **empty and that emptiness is intentional**, the negative space the profile demands. Suggestions, Values, Briefing all collapse into *at most one* surfaced line, chosen by priority, never a list of three.

The tier banner is **deleted from this surface entirely.** Monetization lives in Profile/Settings, never in the doorway. (See audit on settings for where it goes.)

### Visual hierarchy & layout

- **No cards.** Delete `_make_card` (`dashboard.py:306`) for this screen. Replace boxed sections with **rhythm and type scale** — the page is held together by spacing and weight, not borders. This alone moves it out of GENERIC, because "stack of bordered cards" is the single most generic Qt layout that exists.
- **Type does the hierarchy.** The one true sentence is large warm serif (28-32px). The door label is medium serif. The side-doors and mantel line are small humanist sans, muted. Three tiers, instantly legible, no decoration.
- **Single 640px reading column**, narrower than the current 920 (`dashboard.py:102`) — closer to a page than a dashboard.

### The adaptive / behavioral-token behavior (the actual differentiator)

This is where Hearth stops being a tracker. The dashboard **re-composes itself based on the computed state it already has** — energy prediction, mood trend, task pressure, crisis signals — all of which are *already wired in* (`_refresh_energy`, `_refresh_mood`, `_refresh_tasks`, `_refresh_crisis_banner`). Today that data only edits gray strings. Instead, let it drive the *form*:

- **Drained / low energy** → density drops (apply the spacious end of `layout_density`), brightness of the Hearthlight lowers (warmer, dimmer amber), the mantel hides itself, the side-doors fade to almost nothing. The screen literally gets quieter when you're depleted. *"There's less here on purpose."*
- **Anxious / high task pressure** → the door narrows to a single smallest-possible step (Hearth's "break a large task into one visible next step" logic), and a quiet breathing affordance appears *inline under the door* (not buried in nav). The Hearthlight's pulse slows down to a 6-second in/out to pace breathing.
- **Hypomanic / many rapid signals** → the screen does NOT cheer. It steadies. Reduces accent saturation, removes the side-doors, surfaces one grounding line. (The brief: "nothing celebratory.")
- **Crisis signal detected** → the *entire screen* yields. The door becomes the crisis door (Crisis is promoted out of the left rail to here), the rest dims to near-black with a single warm focus. Not an orange alarm bar — a *quieting of everything except the one thing that matters.*

Mechanism: a small `compute_state() -> DashboardState` that maps the existing manager outputs to a dataclass (`{energy_band, mood_trend, pressure, crisis}`), then a `_compose(state)` that selects density, Hearthlight color/animation, which zones render, and the copy register. This is a *contextual* token application — and it's the thing that could only exist in Hearth.

### Signature moment #1 — The Hearthlight

A custom-painted widget (subclass `QWidget`, override `paintEvent` with `QPainter` + `QRadialGradient`) rendering a soft, breathing ember of warm light at the top of the screen. It is **not decoration** — it *is* the state readout:

- Color temperature encodes energy (cooler/dimmer when drained, warmer/fuller when steady).
- A slow `QPropertyAnimation` on a `pulse` property (6-8s ease-in-out, respecting `reduced_motion` from `ThemeManager`) makes it breathe like banked coals.
- On open, it eases up from dark over ~1.2s — the "turning a page" entrance the profile asks for, the room warming as you enter.

This single element does the work of four status cards, replaces the dead accent usage, fulfills "the warm corner," and is impossible to copy-paste into any other app because it's wired to *this product's* psychological state model. **It passes the specificity test on contact.**

### Signature moment #2 — "The room remembers"

When the user records their first signal of the day (mood, usually), the Hearthlight *responds in place* — it warms or cools and the one true sentence rewrites itself in a slow serif crossfade (`QGraphicsOpacityEffect` + `QPropertyAnimation`, ~600ms). No toast, no checkmark, no confetti. The acknowledgment is that **the room changed because you spoke.** This is the antidote to the current "press button → screen disappears → one gray line changes" dead loop. It makes the dashboard the place where your actions visibly land.

### Copy voice (rewrite)

- Greeting+state, empty: **"Morning, Alex. You haven't said how today feels yet — no rush."**
- Greeting+state, data: **"You're running low this afternoon. Nothing here is urgent."**
- The door, with task: **"When you're ready: rename the export file."** (Not "Start with." Not "needs a decision.")
- The door, empty: **"Tell me how today feels."**
- Mantel, overdue: **"One thing slipped past its day. It can wait, or we can shrink it."**
- Crisis door: **"Let's get you to safer ground."** (calm, first-person-plural, never "EMERGENCY")
- Delete forever: "Briefing," "Right now," "Next action," "Context," "Suggestions," "Values report unavailable," "2 open tasks need a decision."

Every one of these fails the swap test *in the competitor's favor* — drop them into Headspace and they'd feel too plain-spoken and adult. That's the target.

### Qt mechanisms summary
- Hearthlight: `QWidget` + `paintEvent`/`QPainter`/`QRadialGradient`, custom `pulse` Qt property, `QPropertyAnimation`.
- Crossfades / entrances: `QGraphicsOpacityEffect` + `QPropertyAnimation`, gated on `ThemeManager.reduced_motion`.
- Adaptive composition: `compute_state()` dataclass + `_compose(state)` reading `layout_density` / `chrome_visibility` from the active `Theme`.
- Serif: register the warm serif via `QFontDatabase`, add a `text_serif` font-family path so `themes.py` can route reading text to it; promote the greeting/door/mantel to that family.
- Reactivity: keep the existing `state_bus` subscriptions (`dashboard.py:639`); **delete the Refresh button and the manual 5-min `QTimer`** — the bus already covers it.

---

## Quick wins vs. deep rebuilds

**Quick wins (hours, no architecture change):**
1. **Delete the tier banner from this surface** and move monetization out of the doorway. (`_build_tier_banner`, line 126) — biggest single tone improvement.
2. **Delete the Refresh button** (`dashboard.py:229`). The bus and timer already refresh.
3. **Fix the contrast floor:** stop defaulting body content to `text_muted`; use `text` for the one true sentence and reserve `text_muted` for the genuinely-secondary mantel only. (`typography.py:57`)
4. **Kill "Values report unavailable" and all "unavailable/not yet" lines** — replace empty state with one warm invitation sentence. (`dashboard.py:281`, 488)
5. **Collapse Right now + Context + Briefing + Suggestions into one priority-picked sentence.** Delete three of the four cards immediately; the logic already computes the inputs.
6. **Make the accent serve meaning:** stop spending `#D9A05B` on "Start trial"; the warm color belongs to the one next action, nothing else.
7. **Unify the radius** to the theme's `border_radius` and route buttons/cards through it (remove hardcoded 5/6 in `buttons.py`/`card.py`).

**Deep rebuilds (the real work):**
1. **The Hearthlight** custom widget and its state→light mapping.
2. **`compute_state()` + `_compose(state)`** adaptive composition — the behavioral-token engine that makes the screen re-form itself per psychological state. This is the product's whole differentiator and currently does not exist.
3. **Serif typography pipeline** (font registration + token routing) so the reading voice has a personality.
4. **The "room remembers" response loop** — in-place Hearthlight + serif crossfade on first signal, replacing the navigate-away dead loop.
5. **Crisis-as-yielding** — promote Crisis out of the left rail, replace the orange alarm bar with the whole screen quieting to one warm door.
