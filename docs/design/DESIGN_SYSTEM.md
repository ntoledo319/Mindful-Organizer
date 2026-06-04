# Hearth — Design System

**The concrete system that builds the VISION in PyQt6.** Where `VISION.md` says *what* and *why*, this says *how* and *with which Qt mechanism*. It is grounded in the real code: `src/gui/themes.py` (the `Theme` dataclass + `ThemeManager.generate_stylesheet`), `src/gui/components/`, and the failures catalogued in `audit_01`–`audit_09`.

Guiding constraint from `audit_09`: today there are **three competing styling sources** (the QSS string, per-instance `setStyleSheet` in `components/`, and hardcoded fallbacks) that disagree on radius, padding, font-size, and token names. **The system's first job is to collapse to one source of truth.** Everything else stands on that.

---

## 0. Architecture: one token source, one resolve step, one stylesheet

```
HearthState (arousal, energy, clarity)          ← sensed/inferred at runtime
        │
        ▼
resolve_tokens(theme, state) → ResolvedTokens    ← the behavioral-token engine
        │                                          (density, luminance, accent warmth,
        ▼                                           motion_ms, chrome level, type scale)
generate_stylesheet(theme, resolved) → QSS       ← ONE generator, re-run on state change
        │
        ├─→ app.setStyleSheet(...)               ← discrete restyle
        └─→ hearth.motion animates the continuous parts (bg luminance, accent) smoothly
```

**Rules that make this real:**
1. **Kill the alias shim** (`themes.py:56-65`: `secondary`, `card_bg`, `hover`, `input_bg`, `tab_active`…). Migrate every widget to canonical names (`surface`, `text_muted`, `accent`). The shim is the seam where the two styling systems leak.
2. **Kill the inline `setStyleSheet` bodies** in `components/buttons.py`, `card.py`, `progress.py`, `typography.py`, `containers.py`. Components set an `objectName` or a dynamic property (`setProperty("role", …)`) and inherit from the single QSS engine. There is exactly one definition of "what a card is."
3. **`generate_stylesheet` takes `(theme, resolved_tokens)`** instead of reading `self.font_scale`/`layout_density` directly, so density and type scale flow from one place and respond to state.

---

## 1. Type scale + font strategy

### The two-font voice
| Role | Property | Used for | Why |
|---|---|---|---|
| **Reading serif** | `[role="reading"]` | greeting, journal, prompts, the one-true-sentence, crisis copy, suggestions, drug names | "a letter someone wrote you" — the un-SaaS move (`audit_09 §3`) |
| **Control sans** | `[role="control"]` (default) | buttons, nav labels, field labels, numbers, timestamps | quiet humanist sans; "numbers tucked into the background" (`profile §Typography`) |

- **Bundle the fonts** — do not rely on `SF Pro`/`Inter` being installed (the audits show `Segoe UI` hardcodes silently falling back on macOS). Register at startup: `QFontDatabase.addApplicationFont("assets/fonts/<serif>.otf")` and the sans `.otf`. Candidate serif: a warm literary face with personality (e.g. **Source Serif 4**, **Newsreader**, or **Spectral** — open-licensed, ship the `.otf`). Candidate sans: **Inter Tight** or **IBM Plex Sans** — *but never the default Inter+gray-50 Tailwind look the project bans*; the serif contrast is what saves it.
- **OpenDyslexic** stays as the accessibility swap for *both* roles when `dyslexia_font` is on (already wired in `themes.py:245`).

### The scale (a real ratio, with line-heights)
Replace the five magic numbers (`12/14/16/20/26`, `themes.py:238-242`) with a **minor-third (1.25) scale**, exposed as tokens, multiplied by `font_scale` in exactly one place, and consumed by both QSS and any remaining component code (fixes the bug in `audit_09` where the slider scales headings but not body):

| Token | px (×1.0) | line-height | Role | Use |
|---|---|---|---|---|
| `display` | 33 | 1.15 | serif | onboarding wordmark, the one-true-sentence on Today |
| `title` | 26 | 1.2 | serif | screen titles, "Stay" header |
| `heading` | 21 | 1.3 | serif/sans | section leads |
| `body-lg` | 17 | 1.5 | serif | reading body, journal, prompts |
| `body` | 14 | 1.5 | sans | UI body, descriptions |
| `label` | 13 | 1.4 | sans | field labels, nav |
| `caption` | 11 | 1.4 | sans | timestamps, the quiet bottom disclaimer line |

Drop the generic `letter-spacing: -0.5px` on headers (`themes.py:322`) — it's the "tighten the big text" move every UI kit does (`audit_09`). Let the serif carry the personality instead. **No component hardcodes a px size again.**

---

## 2. Color & theme architecture

### The palette, corrected to the profile
The aesthetic profile demands **natural materials at dusk** — paper, unbleached linen, river stone, slate, faded ink, dried sage — and explicitly bans *"calm blue that's actually corporate SaaS blue."* Two existing themes violate this and must be retuned:

- **Slate** currently uses `accent="#62A0EA"` (`themes.py:129`) — the exact banned SaaS blue. Retune its accent to a **cool dried-sage or river-stone** that still reads "lower cognitive load" without being Bootstrap-info-blue.
- **Quiet** (the accessibility theme) uses `success="#00FF00"` and `accent="#FFD400"` on pure black (`themes.py:153-157`) — traffic-light primaries, the opposite of calming for an anxiety/PTSD audience. Rebuild from **desaturated high-contrast pairs** that still clear AA but don't sear.

The four themes keep their roles:
| Theme | Role | Identity |
|---|---|---|
| **Onyx** | default dark | warm charcoal (`#0F0F11`/`#18181A`), hearthlight amber accent `#D9A05B`. *Not pure black* — the profile wants "deep indigo or warm charcoal." |
| **Alabaster** | light | premium paper (`#FAFAFA`/`#FFF`), forest-green accent `#426B52`. Good as-is. |
| **Slate** | low-load dark | cool, focused — retune accent off SaaS-blue to sage/stone. |
| **Quiet** | high-contrast a11y | rebuild off `#00FF00`/`#FFD400` to calm high-contrast pairs. |

### Contrast floor — the app-wide AA failure
`text_muted` (`#8E8E93`) on `surface` (`#18181A`) measures **~4.0:1** — under AA 4.5:1 — and it's where almost all *content* lives because `BodyLabel`/`Caption` default to the `secondary` alias (`audit_02`, `audit_09`). Fix at the system level:
- Reading/body content defaults to `text`, not `text_muted`. `text_muted` is reserved for genuinely secondary chrome (timestamps, the demoted disclaimer).
- Raise every theme's `text_muted` to clear **4.5:1** on its `surface`.
- Add a real **`shadow` → `QGraphicsDropShadowEffect`** binding (the `shadow` token is defined on every theme and used by *nothing*). Elevation = importance: the one true action sits on the most-elevated, warmest card.

### How brightness & density adapt to state (the behavioral layer)
`ResolvedTokens` carries continuous values the State Engine sets per render:
- `luminance_shift` (−8%…0%) — drops when energy is low; animated on the `background`/`surface` colors.
- `accent_warmth` — eases the accent toward ember when arousal/distress rises.
- `density` (0.8 spacious … 1.2 compact) — replaces the static `layout_density`; **applied evenly** to cards *and* buttons *and* lists (today it scales buttons but not cards — `audit_09`).
- `chrome` (`full`/`reduced`/`minimal`) — finally consumed: `minimal` hides secondary cards and collapses the rail.
- `motion_ms` — the eased duration for every transition; `0` under `reduced_motion` or Quiet.

Crisis and panic surfaces **force `chrome="minimal"` and spacious density regardless of the user's normal setting** — the one place the thesis is provable in a single screen (`audit_05`).

---

## 3. Spacing & layout rhythm

Replace the scattered literals (`padding: 4px 6px 12px 6px`, `margin: 16px 8px`, hardcoded `24px` card padding — `audit_09`) with **one spacing scale**, multiplied by `density`:

`space-1=4 · space-2=8 · space-3=12 · space-4=16 · space-5=24 · space-6=32 · space-7=48`

Layout rules:
- **Reading column** max-width ~560–640px, centered — closer to a page than a dashboard (Today's current 920px is too wide; `audit_02`).
- **No card grids where rhythm + type can do the work.** Today, Reflect, Calm, and Crisis hold together with spacing and weight, not borders. "Stack of bordered cards" is the single most generic Qt layout (`audit_02`, `audit_05`).
- **One thing in focus.** Completed steps in a flow collapse to a one-line warm summary; only the active step is fully lit (`audit_03`).
- Vertical rhythm derives from line-heights + the spacing scale, so nothing feels arbitrarily loose or cramped.

---

## 4. The component library — replacing raw native Qt

Each entry: **what it replaces · the Qt mechanism · where the audits demand it.** All custom-painted widgets honor `reduced_motion` and pull every color from `ThemeManager` (no hardcoded hex, ever).

| Component | Replaces (native tell) | Qt mechanism | Demanded by |
|---|---|---|---|
| **Hearthlight** | — (the signature) | `QWidget.paintEvent` + `QRadialGradient`; `pyqtProperty(float)` `glow`/`pulse`; `QPropertyAnimation` + looping `QSequentialAnimationGroup` for the idle breath | `audit_01,02,04,05,07,08,09` |
| **HearthCard** | flat `QFrame`+1px border; the dual radius (5/6/12) bug | `QFrame` subclass, `paintEvent` for soft inner-warmth gradient toward accent at low opacity + true `QGraphicsDropShadowEffect` from the `shadow` token | `audit_02,09` |
| **HearthCalendar** | `QCalendarWidget` (OS month grid, red weekends) | custom `QPainter` month grid; each day a **warmth dot** colored by that day's mood/energy — this *is* the mood chart, killing the matplotlib placeholder | `audit_03,09` |
| **StateDial / hearth-dial** | mood `QSlider` + `QTimeEdit` + value label | `QWidget` + `QPainter` arc (`QConicalGradient`), one draggable knob; on change, animate the window `bg_color` `pyqtProperty` via `QPropertyAnimation` — the room warms/cools as you set your mood | `audit_03` |
| **StateSlider** | raw `QSlider` (font size, urge 0–5, SUDS) | custom track; fill shifts along the warmth ramp as dragged; value rendered as a **word** ("Okay," "Bad"), not a number, eased on change | `audit_03,04,08,09` |
| **Pill / SymptomToken** | 28-checkbox `QCheckBox` grid; `QGroupBox`-as-card hack | `QAbstractButton` (checkable), painted rounded rect, amber fill + soft `QGraphicsDropShadowEffect` glow on select; laid out in a wrapping **FlowLayout** (the standard Qt example); **condition-filtered** to ~6–10 relevant chips with a quiet "more…" | `audit_01,03,05` |
| **CareLedger / timeline** | `QListWidget` debug dumps (`[ISO] Distress: 7/10`, `12 moved, 3 skipped`) | delegate-painted rows or stacked card widgets; reverse-chron, human-voiced; warm dots sized by magnitude | `audit_02,05,07` |
| **SteadinessRibbon** | the "Adherence rate / Missed: N" stat block | single `QWidget` `paintEvent` drawing last ~14 day-marks (filled/hollow/half) from a recent window — self-healing, can't grow unbounded | `audit_06` |
| **DoseCard** | `QCheckBox` rows + green-text "Taken" | `QFrame` + `paintEvent` capsule glyph (per-med warm hue) + warm left-edge bloom on take, `QPropertyAnimation` on a `warmth` property (~400ms `OutCubic`); explicit Took/Late/Skipped (no toggle-implies-missed bug) | `audit_06` |
| **HearthButton** | `QPushButton` (3 radii) + Bootstrap RGB triad | one QSS-driven button; `primary` (amber, the one action), `ghost` (text-only side-doors), `crisis` (calm **outlined** danger, never filled-red — the `#crisisButton` style already in the theme) | `audit_02,05,07` |
| **TrustDial** (segmented) | execution-mode `QComboBox` | three painted segments, `QPropertyAnimation` sliding selection; copy "Just tell me → Ask me first → Go ahead, I trust you" | `audit_07` |
| **RoomButton** (nav) | `QPushButton[class="navItem"]` rows; loud amber pill (1.9:1 contrast fail) | `QAbstractButton` `paintEvent`: left-edge hearthlight bar + soft glow on select (text stays on dark surface — fixes contrast), icon + label | `audit_08` |
| **TheLight** (popup) | corner theme `QComboBox` | frameless `Qt.Popup` `QWidget` with a painted warmth/brightness band; drag interpolates theme tokens + live `setStyleSheet`; holds font-size + reduced-motion | `audit_08` |
| **Toast** (ambient) | every `QMessageBox.information("Saved")` | small inline `QLabel` + `QGraphicsOpacityEffect` fade + auto-dismiss `QTimer`; never blocking | all audits |
| **CrisisPanel** (rising) | `QMessageBox.Warning` risk path | `QStackedWidget` swap or `QPropertyAnimation` on geometry; warmth rises from the bottom edge, one sentence + one action | `audit_03,04,05` |
| **BreathOrb** | flat `drawEllipse` "breathing" circle | `QPropertyAnimation` on `pyqtProperty(float)` `expansion` with `QEasingCurve.InOutSine` + true hold; `QSequentialAnimationGroup` chains inhale→hold→exhale→hold; `QRadialGradient` orb + lagging outer halo; brightens on inhale | `audit_04,05` |
| **DropZone** (organizer) | idle 0% `QProgressBar` + light-mode fallbacks | custom dashed-warm `QFrame`, `setAcceptDrops` + `dragEnterEvent`/`dropEvent`, glows on hover; folder **cards** replace the `QTextEdit` structure dump | `audit_07` |
| **HearthEmpty / HearthLoading / HearthError** | `--`, `(matplotlib integration)`, "Use Edit to add" | system primitives: empty = one warm invitation line; loading = slow breathing pulse (not a spinner); error = warm, non-alarming | `audit_03,05,09` |
| **Icon set** | no iconography anywhere (everything bare text) | single-weight, soft-cornered SVG → `QIcon` family, warm-toned, used sparingly in nav + section heads | `audit_09` |

**Banished entirely from user-facing surfaces:** `QCalendarWidget`, `QSpinBox`, `QGroupBox` (the floating-title source of *every clipped header* in the audits), `QListWidget`-as-data-dump, `QComboBox` for momentous choices, `QToolTip`-as-confirmation, `QMessageBox`-as-feedback, `QInputDialog` for format strings.

---

## 5. Iconography & motion language

### Iconography
One custom line-weight family (soft corners, warm tone), used **sparingly** — nav rooms, section leads, the crisis anchor. Never decorative grids of icons (the banned 3-column icon+heading+body pattern). The absence of *any* icons today is part of why everything reads "bare" (`audit_09`); the answer is restraint, not a clip-art dump.

### Motion — `hearth.motion`
A thin wrapper over `QPropertyAnimation` with named eases and durations from `resolved.motion_ms` (so `reduced_motion` and the State Engine both finally do something):
- `settle` — `OutCubic`, ~250ms — cards appear, values change.
- `breathe` — `InOutSine`, ~6s loop — the orb, the idle hearthlight, the heartbeat pulse.
- `lift` — subtle elevation/opacity on hover.
- `cross-dissolve` — `QGraphicsOpacityEffect` + `QPropertyAnimation`, ~250–600ms — page/nav transitions, the one-true-sentence rewrite.

**Laws:** slow, eased, never bouncy; transitions feel like *turning a page* (`profile §Motion`); nothing celebratory; every emotional-space change is a cross-dissolve, never a hard `setCurrentIndex` cut (`audit_08`); `reduced_motion` swaps motion for a calm static fallback (a steady glow, a held instruction), never nothing-but-jank.

---

## 6. Copy voice rules

The voice test (`profile §3`): *could a thoughtful adult say this to another in a quiet room?* Plus the swap test: drop a competitor's name in; if it still works, the copy is dead.

- **First/second person, present tense, plainspoken adult.** "When you're ready: rename the export file." Not "Start with…", not "needs a decision."
- **Hearth speaks as a companion that acts:** "I quieted your notifications," "I'll wait," "I stepped back," "I've got it from here." The copy only works because Hearth *does* something — that's what makes it un-swappable.
- **Empty states give:** "Two more check-ins and I'll start noticing your patterns." Never `--`, never "Log at least 2 entries."
- **Crisis copy is calm, specific, first-person-plural:** "Let's get you to safer ground." "Stay." "You don't have to get through this alone right now." Never "EMERGENCY," never a deterioration checklist.
- **Forgiveness over scoring:** "Noted. Tomorrow's a fresh one." "Six steady days. Yesterday slipped by — it happens."
- **Must-word:** *hearth* (warmth, refuge, hearthlight, "the warm corner"). **Never-words:** *optimize, supercharge, unlock, journey, aggressively, autonomous mode, adherence rate, premium* (as a feeling), *Navy SEALs*, "how are we feeling today?", "Whether you're a [A] or [B]…", "Spaces," "Profile" (as the settings label), "Ready" (tray; a hearth is *lit*, not *ready*).
- **Fix the bug:** escape `&` in lifeline strings ("988 Suicide & Crisis Lifeline" is corrupted by the Qt mnemonic accelerator — `audit_05`).

---

## 7. Prioritized roadmap

Ordered by **felt-quality leverage** — the single change that most transforms the experience first, through to polish. Each wave names the surfaces and components it touches. Quick wins (low-risk, hours each, flagged ⚡) are folded into the earliest wave that needs them so trust defects on life-safety screens get fixed immediately.

### Wave 0 — Stop the bleeding (correctness + life-safety + theme integrity)
*The highest taste-per-hour, and some are duty-of-care fixes. No new architecture.*
- ⚡ **Fix the `&` mnemonic corruption** on "988 Suicide & Crisis Lifeline" — one-line fix on the most important string in the app. (`crisis`)
- ⚡ **Route dangerous answers to Crisis.** A diary/journal self-harm or suicide answer above threshold opens the crisis surface, not a "Saved" dialog. Closes the one duty-of-care gap. (`diary, journal`)
- ⚡ **Delete the breathing theme bypass** (`_CALM_BG`/`_CALM_CARD`, the `.styleSheet().replace()` hack) — fixes the off-theme, invisible-ghost-text catastrophe, the single worst visible defect. (`breathe`)
- ⚡ **Fix the medication misclick-records-"missed" bug** feeding false signals to the crisis heuristic; kill "Adherence rate" + the lifetime failure tally. (`medication`)
- ⚡ **Recolor the lifeline amber, not red;** remove the live-crisis warning-signs checklist + "Use Edit to add" placeholders. (`crisis`)
- ⚡ **Apply the theme to onboarding before `exec()`;** delete the off-brand `#4a90d9`/`#27ae60` progress dots and `Segoe UI` pins. (`onboarding`)
- ⚡ **Purge every dev placeholder:** `(matplotlib integration)`, `Cycle: -- / --`, `Mode: suggestions_only`, the `--` analytics walls, `{n:03d}`. (`mood, breathe, automation, organizer`)
- ⚡ **Delete the upsell banner from Today** and the Refresh button. (`dashboard`)
**Touches:** crisis, diary, journal, breathe, medication, onboarding, mood, automation, organizer, dashboard. **Components:** none new — string/QSS/logic only.

### Wave 1 — The foundation (one styling source + type + color + motion + state engine)
*Nothing distinctive can be built until the system is coherent. This is the force-multiplier wave (`audit_09 §3.1-3.6`).*
- Collapse to **one styling source**: kill the alias shim and the inline component `setStyleSheet`; route all components through the single `generate_stylesheet`.
- Ship the **two-font voice** (bundle + `QFontDatabase`, `[role]` properties) and the **real type + spacing scales** with `font_scale` applied once.
- Fix the **AA contrast floor** (body defaults to `text`; raise `text_muted`); wire **`shadow` → drop-shadow**; retune **Slate** off SaaS-blue and **Quiet** off `#00FF00`/`#FFD400`.
- Build **`hearth.motion`** and the **`HearthState` → `resolve_tokens` → animated re-style** engine — the differentiator. Build it here so every later wave can *adapt*.
- Build the base primitives every surface reuses: **Hearthlight, HearthCard, HearthButton, Toast, HearthEmpty/Loading/Error.**
**Touches:** `themes.py`, all of `components/`, app-wide. **Components:** Hearthlight, HearthCard, HearthButton, Toast, empty/loading/error, motion layer, State Engine.

### Wave 2 — The doorway + the daily check-in (where the thesis becomes felt)
*The two highest-traffic emotional surfaces, now standing on the foundation.*
- **Today → one breath, one line, one door.** Hearthlight at top encoding energy; one serif true-sentence; one warm door; side-doors recede; the screen re-composes per `HearthState` ("the room remembers" in-place warm response on first signal). (`dashboard`)
- **Daily check-in → the warming hearth-dial.** One adaptive vertical flow replacing the mood/diary/sleep walls; condition-filtered Pills; the room dims/warms as you set the dial; the "hand on the shoulder" crisis hand-off; ambient Toast instead of `QMessageBox`; density adapts to the answer. (`mood, diary, sleep`)
**Touches:** dashboard, mood, diary, sleep. **Components:** StateDial, StateSlider, Pill/FlowLayout, CrisisPanel, HearthCalendar (back-date affordance), Toast.

### Wave 3 — The shell (the frame that proves the thesis on every screen)
- **Collapse 15 flat tabs → ~5 rooms** (Today, Reflect, Calm, Focus, Track) with internal sub-space switchers; **Crisis pinned to a fixed bottom anchor**, one motion from anywhere.
- **The adaptive shell:** wire `WellnessOrchestrator`/`StateBus` to animate rail width, density, and brightness on state change — the house gets quieter when you do.
- **"The Light"** popup replaces the theme combo; **settings drawer** replaces the 7-section `QGroupBox` form; **custom tray hearth icon** replaces `SP_ComputerIcon`; **cross-dissolve nav transitions**.
**Touches:** `main_window.py` (rail/header), `settings_widget.py`, `system_tray.py`. **Components:** RoomButton, TheLight, settings drawer, tray hearth icon, cross-dissolve.

### Wave 4 — The high-stakes surfaces (crisis, panic, ERP)
- **Crisis → "Stay":** full-bleed warm canvas, ember glow, one enormous amber lifeline, the slowing-heartbeat "the line is open" moment; reasons-for-living surfaced one at a time; warning-signs moved to a calm-state safety-plan editor.
- **Panic → now/later split:** opens in a breathing-pacer "now" mode (no form while panicking); the pacer adapts copy from the user's own attack history ("you're roughly halfway"); a gentle one-question-at-a-time log for "later."
- **ERP → planning/in-session split:** a painted hierarchy ladder; radical in-session subtraction; a live, *falling* habituation curve as the emotional payoff; the SUDS prompt is a non-modal in-canvas fade, never a `QMessageBox`.
**Touches:** crisis, panic, ERP. **Components:** Hearthlight (heartbeat/pacer), CrisisPanel, BreathOrb, CareLedger/timeline, painted ladder + habituation curve, in-canvas prompt.

### Wave 5 — The protective surfaces (the differentiator made visible)
- **Automation → "The Hearthroom":** kill the tabs, the engine-status string, the Bootstrap triad. A live Hearthstone whose glow *is* the engine state; one honest sentence; one state-aware protective action; the human-voiced recent-care feed; the segmented TrustDial; the room visibly dims its own chrome when Focus activates ("closes Discord, dims the lights," on Hearth's own surface).
- **File Organizer → "Tidying, gently":** open in the user's condition-language (warm even when Generic); a warm drag-and-drop drop-zone empty state; preview-by-default framed as safety; an animated file-settling; Undo always visible; the "just one drawer" offer for low-energy states.
**Touches:** automation, file organizer. **Components:** Hearthstone (Hearthlight), TrustDial, CareLedger, DropZone, folder cards, file-settle animation.

### Wave 6 — Onboarding + reflective + medication + polish
- **Onboarding → lighting the hearth:** three acts (Arrival → Tending → Settling); the ember as progress; the room warms live on first condition (`get_recommended_themes`); the "carry the flame into the next room" handoff into the main window.
- **Journal → notebook;** **Meditate → breathing-ring timer** (adopt the design system, retire `QGroupBox`); **Medication → The Shelf** (DoseCard warming + SteadinessRibbon + three-state honest logging).
- **HearthCalendar** as the personal heat-map / patterns view; iconography pass; reduced-motion fallbacks audited everywhere; final accessibility sweep.
**Touches:** onboarding, journal, meditate, medication, app-wide. **Components:** ember/handoff, notebook editor, breathing-ring timer, DoseCard, SteadinessRibbon, HearthCalendar, icon set.

---

## The single most transformative change

If only one thing ships: **Wave 1's State Engine + Hearthlight, proven on Wave 2's Today screen** — the moment the user records their first signal and *watches the room warm and quiet itself in response*. That single loop converts Hearth from "a tracker with a dark coat" (what all nine audits found) into the one interface that does something about how you feel. Everything else is in service of making that moment true on every surface.
