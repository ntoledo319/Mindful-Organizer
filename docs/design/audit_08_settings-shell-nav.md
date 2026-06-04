# Audit 08 — Settings, Shell & Navigation

**Surface:** the application *shell* — the persistent left "SPACES" nav rail, the top window chrome (Hearth / Alex / Theme / Onyx), the theme switcher, the Settings/"Profile" tab, and the system tray.
**Source read:** `src/gui/main_window.py` (shell, header, nav rail, theme switcher), `src/gui/widgets/settings_widget.py` (the Profile/Settings tab), `src/gui/system_tray.py` (tray menu), `src/gui/themes.py` (tokens + QSS).
**Screenshots read:** `/tmp/hearth_ui/settings.png`, `/tmp/hearth_ui/dashboard.png`.
**Verdict on the GENERIC → DISTINCTIVE scale:** the shell sits at **GENERIC**. It is a 15-item flat sidebar + a top bar + a long native settings form. Strip the word "Hearth" off the header and this is the chrome of *any* desktop Electron-or-Qt productivity app from the last decade. The one place the product's entire thesis ("your computer adapts to your psychology") should be *structurally* visible — the way you move through the app — is the place that most aggressively denies it.

---

## What this surface is

The shell is not a screen. It is the **room the user lives inside.** Every other surface (Today, Journal, Breathe, Crisis) is furniture; the shell is the walls, the doorways, and the light switch. It is on screen 100% of the time. It is the only part of Hearth the user touches on *every* session, in *every* state. That makes it the single highest-leverage surface for the thesis — and the one most punished by getting it wrong, because a cold, busy frame poisons every warm screen hung inside it.

**The user's state when they reach it.** They reach the *nav rail* constantly, in every state — drained, anxious, dissociating, hypomanic, mid-crisis. They reach *Settings/"Profile"* rarely and usually for a reason that carries weight: to change the theme because the current one is too bright for how they feel, to bump font size because their eyes are tired, to find the crisis/data/export controls, to confirm "is my data actually private," or — the heavy one — to edit which conditions they live with. Nobody opens a settings panel in a mental-health app for fun. They open it because something about the current state of the app doesn't fit their current state of mind.

**The job the shell must do, in priority order:**
1. **Make movement feel like walking between rooms, not clicking between tabs.** The act of navigating should itself be calming and legible.
2. **Surface the *right* doors for *right now* and quiet the rest.** A flat list of 15 equally-loud destinations is hostile to a low-executive-function brain.
3. **Keep Crisis reachable in one motion from everywhere — present, never shouting.**
4. **Make the global controls that change how the app *feels* (theme, brightness, density, font) live where the feeling lives** — not buried at the bottom of a 7-section form behind a label that says "Profile."
5. **Quietly hold the privacy promise** ("all data stored locally") as ambient trust, not fine print.

The current shell does #1–#5 backwards. It makes movement feel like a tab bar, shouts all 15 doors equally, hides Crisis 13 items down between "Library" and "Profile," locks the feel-controls inside a tab mislabeled "Profile," and reduces the privacy promise to a sentence in an "About" box nobody scrolls to.

---

## Why it fails — forensically

### Information architecture — a 15-item flat list is a filing cabinet, not a home

The nav rail (`main_window.py:682-717`, `_add_tabs`) renders, in order: **Today, Tasks, Journal, Mood, Diary, Breathe, Meditate, [ERP], [Panic Log], Sleep, Medication, Focus, Library, Crisis, Profile.** That is up to **fifteen flat, equally-weighted destinations in a single scroll**. The screenshot confirms it — a uniform vertical column of identical text rows, top to bottom, no grouping the eye can hold.

- **There is no hierarchy of *kind*.** "Today" (a daily anchor), "Breathe" (a 90-second intervention you reach for *during* a spike), "Medication" (a logging chore), and "Profile" (a settings dump) are presented as peers, the same size, the same weight, in the same list. **Principle violated:** an information architecture must encode *how often* and *in what state* each door is used. Hearth's rail encodes nothing — it's alphabet soup with the alphabet removed. For an ADHD or anxious brain, fifteen undifferentiated choices is not "everything is available," it's "choose, now, from fifteen things, while drained." That's the wall-of-checkboxes failure mode wearing a sidebar.
- **The grouping that *does* exist is invisible and arbitrary.** The code inserts two hairline dividers — one before the `SECONDARY_TABS` set (`{sleep, medication, automation, file_organizer}`, `main_window.py:66`) and one before Crisis (`main_window.py:733-738`). But the screenshot shows these as 1px lines lost in a 15-row stack; they read as nothing. And the grouping itself is incoherent: "Focus" (the *flagship* system-automation feature, the entire paid thesis) is filed under *secondary* tabs next to "Library" (a file organizer). The product's crown jewel is in the junk drawer.
- **"Library" is a file organizer.** In a mental-health refuge, a left-rail item literally labeled "Library" sitting above "Crisis" reads as content/resources. It's a folder-sorting utility (`file_organizer`). This is dead weight in the primary nav of a tool whose job is to lower arousal — it's a Windows-Explorer feature wearing a calm word.
- **Crisis is the 14th item, between Library and Profile.** The one destination that must be *instantly* reachable in the worst moment is buried two-thirds down a 15-item list, differentiated only by red text (`tone="danger"`, `main_window.py:744`). **Principle violated:** crisis access must be the lowest-latency action in the entire product. Here it is one of the highest-latency — the user has to *scan a list of fifteen* and find the red word while in the exact state where scanning and finding are hardest.
- **"Profile" is a lie of a label.** The tab named "Profile" (`main_window.py:716`) is actually **Profile + Subscription + Theme + Accessibility + Notifications + Data + About** — seven sections (`settings_widget.py:100-108`). The thing a user most often comes here for — *make the app dimmer / bigger / calmer right now* — is labeled with the one word ("Profile") that signals "this is about your account," and it's the **fourth section down**, below a sales pitch. **Principle violated:** the label must name the job. "Profile" names the least-used 1/7th of the panel.

### The top chrome — a generic app header doing brand cosplay

The header (`main_window.py:642-680`) is: **"Hearth"** (left) … stretch … **"Alex"** • **"Theme"** • **[Onyx ▾ combo]** (right). Read the screenshot: it is indistinguishable from a thousand SaaS top bars. Logo left, account + a setting right.

- **"Alex" is inert.** The profile name is a plain `QLabel` (`main_window.py:661-663`) — not a menu, not a click target, not an avatar, not a state. It's decoration that *looks* interactive (top-right, where account menus live) but does nothing. **Principle violated:** affordance honesty. An element placed where a menu lives must *be* a menu.
- **A naked `QComboBox` is the single most important "feel" control in the app, and it's a dropdown in the corner.** Theme is *the* mechanism by which Hearth changes how it feels to a fragile person (brightness, contrast, density). It is rendered as a stock `QComboBox` (`main_window.py:670-678`) labeled "Theme," sitting next to the account name like a font picker. **Specificity test: could this top bar exist in any Qt app unchanged? Yes, verbatim. → It's wrong.** The control that should be the most expressive, mood-aware thing in the product is the most generic widget Qt ships.
- **The header competes with the nav for the brand word.** "Hearth" appears top-left in the header *and* "SPACES" sits as the rail header just below it. Two competing labels, neither doing emotional work — both are just text in the corner.

### Visual hierarchy — fifteen identical rows and one orange pill

In the screenshots the nav rail is a flat column of gray text rows. Exactly **one** element has any weight: the active item, painted as a solid amber pill (`navItem:checked` → `background-color: accent`, `themes.py:298-302`). Everything else is `text_muted` gray (`themes.py:283-285`). So the hierarchy is binary: *the one place you are* (loud orange block) vs. *everywhere else* (uniform gray). There is no sense of *near / far*, *daily / occasional*, *safe / serious*. The eye gets one signal and fourteen non-signals.

- **The active-state treatment is too heavy and the wrong shape.** A full saturated-amber rounded rectangle behind black text (`accent_text = "#FFFFFF"`, but on `#D9A05B` that's a low-contrast, almost-muddy fill — see Color below) is a *button* gesture, not a *you-are-here* gesture. It shouts. In the screenshots the "Today" / "Profile" pill is the single loudest object on the screen — louder than any content. **Principle violated:** the chrome should recede so the content (the person's day) can be the figure. Here the chrome's selection state is the figure.
- **In Settings, every one of the 7 sections is the same gray `QGroupBox`** (`settings_widget.py` — Profile/Subscription/Theme/Accessibility/Notifications/Data/About all built identically). Read the screenshot: a vertical stack of near-identical dark cards with tiny uppercase titles. Resetting *all your data* (destructive, irreversible) and changing *notification frequency* (trivial) have **identical visual weight**. **Principle violated:** visual weight must track consequence. Here a nuke button and a dropdown look the same.

### Typography — the shell speaks in system sans, the same as everything

- The header "Hearth" is `QFont(family, 17, DemiBold)` (`main_window.py:653`) — the system humanist sans (`"SF Pro Text", "Inter"…`, `themes.py:247`). The one wordmark in the product is set in the same typeface as a Linear sidebar. There is **no wordmark, no serif, no warmth, no Hearth** in the brand's own name.
- The rail header "SPACES" is uppercase 12px muted sans with letter-spacing (`sideNavHeader`, `themes.py:269-276`). This is the *exact* Tailwind/SaaS "section eyebrow" cliché — uppercase, tracked, gray. It could be the section header in any dashboard. **Specificity test: yes. → It's wrong.**
- Settings section titles are uppercase tracked muted sans too (`QGroupBox::title`, `themes.py:523-532`) — the same eyebrow gesture repeated seven times. The whole shell's voice is one font, one weight family, one register: *administrative*.
- `settings_widget.py` even hardcodes `QFont("Segoe UI", ...)` in multiple places (`_section_title` line 47, `_name_label` line 128, `_tier_label` line 171) — a Windows font, on a Mac screenshot, bypassing the theme's font stack entirely. So the type is both off-brand *and* off-system *and* platform-wrong.

### Color / contrast — the warmth color is spent on selection states and sell buttons

- The amber accent `#D9A05B` — the literal **hearthlight**, the warmth that justifies the brand name — appears in the shell in exactly two roles: the **active nav pill** and the **theme-combo selection / accent CTA**. It never warms the room; it just marks "you clicked here." **Principle violated:** "every visual choice serves meaning; the most meaningful color must do the most meaningful job" (`CLAUDE.md`). The hearth's fire is being used as a highlighter.
- **The active-pill contrast is a real accessibility defect.** `navItem:checked` paints text in `accent_text` over `accent`. Code sets `accent_text = "#FFFFFF"` for Onyx (`themes.py:251`). White (`#FFFFFF`) on amber (`#D9A05B`) measures roughly **1.9:1** — *far* below the 4.5:1 AA floor, below even the 3:1 large-text floor. The currently-selected destination's label is, by the numbers, **hard to read**. (In the screenshot the "Profile" pill text does look washed.) The one item the user most needs to identify — where they are — is the least legible.
- **Settings body text rides `text_muted` (`#8E8E93`) on `surface` (`#18181A`)** via `_body_label` (which inherits the muted `QLabel` default behavior) — ~4.0:1, under AA. Field labels ("Conditions," "Therapy types," "Current plan," "Color blindness mode") are all this muted gray. **The settings panel's own labels fail AA**, in the exact panel where a user goes *because their eyes are struggling.*
- **Quiet (high-contrast) theme makes the chrome worse, not better.** Its accent is `#FFD400` (`themes.py:153`); white text on that is ~1.5:1. The "accessibility" theme has the *least* accessible selection state.

### Spacing / density — the rail is fine; the settings form is a wall

- The rail itself is reasonably spaced (38px min-height rows, `themes.py:288-292`). The problem isn't pixel density — it's *decision* density: 15 choices in one column.
- The Settings panel is the opposite: a **single 860px column** (`settings_widget.py:94`) holding **seven stacked `QGroupBox` sections plus a Save button** in one endless vertical scroll. The screenshot shows the user has to scroll past Profile → Subscription → Theme to even *reach* Accessibility (Font size is the *fifth* thing down, half-clipped at the bottom of the frame). **Principle violated:** "surface ONE next action." This surfaces a tax return. For someone who came to do *one* thing (dim the screen), it's a scavenger hunt through a sales pitch and a license-key field.
- There are also clipped/ghosted section headers visible in the screenshot ("Subscription," "Theme," "Accessibility" appear half-rendered above their cards) — a `QGroupBox::title` with `top: -12px` (`themes.py:526`) colliding with the previous card. It reads as a rendering bug. Dev-grade jank in the one place users go to feel in control.

### The actual widgets — native-Qt tells in every corner

This surface is the densest concentration of raw-Qt tells in the app:

- **`QComboBox` for theme** (`main_window.py:670`) — the most important feel-control is a stock dropdown.
- **`QComboBox` for color-blind mode and notification frequency** (`settings_widget.py:289, 316`) — stock dropdowns.
- **`QSlider` for font size** (`settings_widget.py:273`) — a raw OS slider with tick marks (`TicksBelow`, line 277), the most utilitarian widget Qt has, controlling something deeply personal.
- **`QCheckBox` for "Reduced motion" / "Dyslexia-friendly font"** (`settings_widget.py:299, 303`) — naked native checkboxes.
- **`QGroupBox`** ×7 (`settings_widget.py`) — the boxed-titled-frame is the single most "Windows Control Panel" widget in existence. Seven of them stacked *is* the Windows Control Panel.
- **`QMessageBox` everywhere for feedback** — "Settings saved successfully." (`settings_widget.py:444`), every export/import/reset confirmation (`:502, :522, :567`), trial errors (`:202`). A modal OS alert box for *"settings saved"* is the most jarring, least-Hearth feedback possible — it's an interruption that demands a click to dismiss, in an app whose entire premise is *not* interrupting you.
- **`QInputDialog.getText` for the license key** (`settings_widget.py:207`) — a raw OS text-prompt dialog.
- **System tray** (`system_tray.py`) uses `SP_ComputerIcon` — **the generic OS "computer" icon** (`:49`) — as Hearth's persistent tray presence. The always-on ambient representation of the product is *a stock monitor glyph*. And the menu items use ASCII triangles — `"Log Mood ▲"`, `"Log Mood ▼"`, `"Crisis Mode"` (`:63-75`) — raw text in a default `QMenu`.

**Specificity test, applied to the whole shell: could this nav rail + header + settings form + tray exist, unchanged, in a generic Qt productivity app? Yes — entirely. → The entire shell is wrong.** Not styled-badly. *Generically conceived.* A dark coat of paint (the "Onyx" theme) over stock Qt scaffolding.

### Interaction & feedback — administrative, modal, and silent

- **Theme changes are instant but unconfirmed-as-intentional.** Changing the top-bar combo applies immediately (`_on_theme_changed`, `main_window.py:1001`), but changing it inside Settings only *previews* a swatch and requires a separate **"Save"** click (`settings_widget.py:113, 416-419`) — two different theme-change behaviors in two places, with two different mental models. The user can't predict whether a change "took."
- **Feedback is a modal alert.** Every save, export, import, and reset throws a `QMessageBox` (above). There is no inline, ambient "saved" — the kind a calm app uses. The interaction model is *confront-the-user-with-a-dialog*.
- **Nav has no transition.** Switching destinations is an instant `setCurrentIndex` on a hidden `QTabWidget` (`_switch_to_tab`, `main_window.py:1062-1068`). One frame you're in Journal, next frame Crisis — a hard cut. **Principle violated:** movement between emotional spaces should *feel* like movement. A hard cut between "writing about your day" and "crisis resources" is jarring precisely when gentleness matters most.

### Motion — none, in the one place motion would mean the most

There is **zero motion in the shell.** No transition between spaces, no settling of the active pill, no easing on theme change (the whole stylesheet is swapped in one `setStyleSheet` call, `main_window.py:1013 / 1010`), no ambient life in the tray. The `themes.py` tokens literally define `animation_speed_ms` (`:35`) and the theme dataclass carries `chrome_visibility` ("full"/"reduced"/"minimal", `:36`) — **the design system already imagines an adaptive, animated shell and the shell ignores both fields entirely.** The infrastructure for the distinctive behavior is *defined and unused.*

### Empty / loading / error states — honest, but cold and generic

- The placeholder for a failed widget (`_create_placeholder_tab`, `main_window.py:881-904`) is centered title + "This section couldn't load on your system." in `color: #888` hardcoded gray. Honest (good), but it's a generic error card — no Hearth voice, no warmth, no "the room is still here."
- The upsell tab (`_create_upsell_tab`, `:906-946`) hardcodes the amber hex (`#A8845F`) and renders a centered "Start 14-day trial" — a sell screen *as a navigation destination.*
- There is no first-run / empty state for the *shell* — the rail is fully populated immediately with all 15 items regardless of whether the user has ever used any of them.

### Copy — run the swap test, and most of it dies

- **"SPACES"** (rail header, `main_window.py:636`). Generic sidebar eyebrow. Swap "Hearth"→"Notion": still works. **Dead.**
- **"Theme"** (header label, `:666`). Generic. Works in any app. **Dead.**
- **"Profile"** (the settings tab label, `:716`) — not just dead, *wrong*: it names 1/7th of the panel.
- **"Onyx — Deep, premium dark mode. Low visual noise."** (theme description, `themes.py:74`). **"premium"** is marketing-brain — a word about the *product's positioning*, not the *user's experience*. A person picking a theme at 2am because they're overwhelmed does not care that it's "premium." They care that it's *easier on them right now.* Swap test: "premium dark mode" works for any paid app. **Dead, and slightly off-key** for this audience.
- **"This app is a supplement to professional mental health care, not a replacement."** (`settings_widget.py:365`) — correct, necessary, but buried in an "About" box at the very bottom. Right words, wrong altitude.
- **"Settings saved successfully."** (`:444`) — the blandest possible confirmation, in a modal. Swap test: works anywhere. **Dead.**
- **Tray: "Hearth - Ready"** (`system_tray.py:57`). "Ready" is machine-speak ("server ready," "device ready"). A hearth is not "ready"; a hearth is *lit*, *warm*, *here*. Swap test passes for any app. **Dead.**

The shell's copy has **no point of view.** It is the administrative vocabulary of generic software: Spaces, Theme, Profile, Settings, Ready, Save, premium. None of it could only belong to Hearth.

### Emotional tone for THIS audience — a control panel, not a refuge

The thesis is "the warm corner of the computer." The shell delivers a **dark-themed admin console**: a 15-item sidebar, a top bar with an account name and a dropdown, and a Control-Panel settings form full of group-boxes and OS dialogs. For a person who is drained or anxious, the *feeling* of this shell is *being at work* — the same cognitive posture as a project-management tool. There is no warmth, no sense of being *received*, no acknowledgment that the person moving through these rooms might be having a hard day. The shell is emotionally **neutral at best and corporate at worst** — and neutral is a failure here, because a neutral frame makes every warm screen inside it feel like a sticker on a filing cabinet.

### Accessibility — the "accessibility" controls are themselves inaccessible

- Active-pill text contrast ~1.9:1 (Onyx), ~1.5:1 (Quiet) — **both fail**, the high-contrast theme worst of all.
- Settings labels ride muted gray ~4.0:1 — **fail AA.**
- The font-size slider, color-blind dropdown, reduced-motion and dyslexia-font toggles all live **five-plus sections deep** in a tab labeled "Profile." The accessibility controls require the most navigation and reading to *reach*, which is exactly backwards.
- No visible keyboard-focus styling on nav items in the QSS (`navItem` has hover/checked but no `:focus`). Keyboard/screen-reader users get no focus ring on the primary nav.
- The rail relies on a tiny red text color alone to mark Crisis (`tone="danger"`) — color as the sole differentiator, which fails for color-blind users (and the color-blind overrides in `themes.py:172` don't even touch the nav).

### Where it lands: **GENERIC.**

The shell is competently assembled stock Qt with a dark theme. It works, it doesn't crash, the wiring is clean. But on the project's own scale that's the *floor*, not a pass. Nothing about how you move through Hearth, how the global controls present themselves, or how the frame feels could *only* exist in Hearth. The infrastructure for distinctiveness (behavioral tokens: `layout_density`, `chrome_visibility`, `animation_speed_ms`, `condition_suitability`) is **defined in the theme dataclass and entirely unused by the shell.** The product's whole differentiator is sitting in the codebase as dead fields.

---

## The reimagination — the shell as a *house with rooms that respond*

First principle: **Hearth's shell is the proof of the thesis.** If "your computer adapts to your psychology" is true, the *first* thing that must visibly adapt is the way you move through the app and the way the frame feels. The shell is where we make the promise tangible before the user reads a single word of content. So we stop building a "sidebar + top bar + settings page" and start building **a house: a small set of rooms, a quiet light you can turn warmer or dimmer, and a frame that gently changes shape with your state.**

### New IA — collapse 15 flat tabs into a few rooms + a drawer

Stop treating every feature as a top-level destination. Group by **how the user lives**, not by what engineering built:

**Primary rooms (always in the rail, 4–5 max):**
- **Today** — the daily anchor (already the home).
- **Reflect** — Journal + Mood + Diary, unified (these are one activity: "process how I'm doing"). One room, switched by a quiet segmented control *inside* it.
- **Calm** — Breathe + Meditate + Grounding (the things you reach for *during* a hard moment). One room.
- **Focus** — the system-automation flagship, promoted *out of the junk drawer* to a primary room, because it's the thesis made real.
- **Track** — Sleep + Medication + (condition tools like ERP/Panic) folded behind one "logging" room, surfaced only if the user's profile has the relevant conditions.

**Crisis is not in the list.** It is a **persistent, always-anchored element at the very bottom of the rail (or pinned to the window edge), present in every theme, reachable in one motion**, with a fixed position the muscle memory can find without scanning. Calm warm-red, never the loud alarm-red; *there when you need it, not shouting when you don't.*

**Settings stops being a "Profile" tab.** The controls that change *how the app feels right now* (theme/light, density, font, motion) move to a **"Light" control in the chrome** (see signature moment below). The heavier, rarer settings (account/conditions, subscription, data/export/privacy) live in a **slide-over drawer** invoked from the profile chip — not a 15th tab, not a 7-section scroll.

**Mechanism:** keep the existing `QTabWidget` as the hidden content stack (it already is, `main_window.py:597-601`) — but the rail becomes a custom `QWidget` of ~5 **room buttons**, each a custom-painted control (see below), and rooms that contain sub-spaces (Reflect, Calm, Track) own an internal segmented switcher rather than exposing each sub-space in the global rail.

### New layout & hierarchy — near/far, daily/occasional, calm/serious

The rail encodes *kind* and *frequency*, not just selection:
- **Today** sits slightly apart at top — the front door, given the most weight.
- The **2–3 daily rooms** (Reflect, Calm, Focus) sit together as the "main floor."
- **Track** sits below a soft divider as the "occasional" floor, dimmer by default.
- **Crisis** anchors the bottom edge, fixed, with a faint always-on warm-red presence.

Selection state stops being a loud full-amber button. It becomes a **soft warm glow + a left-edge hearthlight bar** — a "you-are-here" that *recedes* into the frame rather than shouting. (Fixes the 1.9:1 contrast defect by never putting text on top of a saturated amber fill.)

### The signature behavioral move — the shell *breathes* with your state

This is the differentiator and it's already half-built in the tokens. Wire `layout_density`, `chrome_visibility`, and `condition_suitability` (`themes.py:33-36, 92`) into the **shell itself**:

- When the user logs (or the orchestrator infers) a **drained / overwhelmed** state, the shell **softly dims, widens its spacing, and collapses the rail to fewer rooms** — `chrome_visibility = "minimal"`, higher density spacing, brightness eased down. The house literally gets quieter. Fewer doors, softer light.
- When the user is **steady/energized**, the rail expands to show more rooms, chrome returns to "full."
- This is driven by the `WellnessOrchestrator` (`main_window.py:429`) the app already has, and animated via `QPropertyAnimation` on the rail's `maximumWidth` and a brightness overlay, timed by the theme's `animation_speed_ms` (respecting `reduced_motion`).

**That is the product. The room rearranges itself for the person in it.** No other app's shell does this, because no other app is built on the premise that the *environment* should respond. This single behavior moves the shell from GENERIC straight to DISTINCTIVE.

### Signature moment #1 — "The Light" (replaces the theme combo)

Kill the corner `QComboBox`. Replace it with a single warm control in the chrome — a small **hearthlight glyph** that, on click, opens a soft pop-over (`QWidget` popup, not a dropdown) where you don't pick a "theme," you **set the light**:

> *"How's the light right now?"*
> — a horizontal warmth/brightness band you drag along (custom-painted `QWidget`, `QPropertyAnimation` easing the room as you move), from **Bright** → **Easy** → **Dim** → **Dark**, with the actual app brightness/contrast easing *live* underneath your finger.

Theme stops being a setting and becomes **a gesture of self-care**: you're not configuring software, you're turning the lights down because you're tired. Copy is felt, not technical: instead of "Onyx — Deep, premium dark mode" it's *"Dim — for when the screen is too much."* The font-size and motion controls live in the same pop-over, framed as *"easier to read"* and *"less movement,"* not as "Accessibility settings." (Mechanism: custom-painted brightness band widget, live `setStyleSheet` interpolation between theme tokens, `QGraphicsOpacityEffect` overlay for the dim.)

### Signature moment #2 — the tray as a hearth that breathes

Replace `SP_ComputerIcon` with a **custom hearthlight tray icon** whose glow *reflects the app's current sense of the user*: a steady warm ember when things are calm, a slower/softer pulse when the orchestrator has eased the user into a quiet state, a faint cool dim when Focus is protecting them. The persistent, always-there presence in the menu bar becomes *the warm corner of the computer*, literally — a small light that's on for you in the background. Menu copy drops the ASCII triangles and machine-speak: not "Hearth - Ready" but the current state in plain warm language (e.g. *"Hearth — keeping it quiet"* during Focus). (Mechanism: render the tray icon from a `QPixmap` painter, update its glow on orchestrator state changes; it's a tiny amount of `QPainter` code for an enormous amount of brand.)

### Copy voice for the shell

Drop the administrative vocabulary entirely. Rooms are named for *what you do there in plain human words* (Today, Reflect, Calm, Focus, Track) — no "Spaces," no "Profile" mislabel. Feedback is **ambient and warm, never modal**: a save is a quiet inline "kept" that fades, not a `QMessageBox`. The privacy promise stops being About-box fine print and becomes a **quiet, permanent line at the foot of the rail** — *"Everything stays on this computer."* — ambient trust the user passes a hundred times a day. The crisis anchor reads *"I need help now,"* in the user's voice, not "Crisis Mode" in the system's voice.

### Specific Qt mechanisms (so an engineer can build it)

- **Rail:** custom `QFrame#sideNav` holding ~5 custom `RoomButton(QAbstractButton)` widgets, each `paintEvent`-drawn (left-edge hearthlight bar on selection, soft glow, icon + label), replacing the current `QPushButton[class="navItem"]` rows.
- **Adaptive shell:** subscribe the rail + a brightness overlay to `StateBus` (`main_window.py:104`) / `WellnessOrchestrator`; on state change, animate `rail.maximumWidth` and an opacity overlay via `QPropertyAnimation`, gated by `reduced_motion`, durations from `theme.animation_speed_ms`.
- **The Light:** a custom popup `QWidget` (frameless, `Qt.Popup`) with a painted warmth band; dragging interpolates theme tokens and re-applies `setStyleSheet` live; dim via `QGraphicsOpacityEffect`/overlay.
- **Settings drawer:** a slide-over `QWidget` (`QPropertyAnimation` on `pos`) for the rare/heavy settings, invoked from the profile chip — *not* a nav tab.
- **Tray:** `QPixmap` + `QPainter` rendered hearth icon, glow updated on orchestrator state; warm plain-language menu strings.
- **Feedback:** replace `QMessageBox` confirmations with an inline transient toast widget that fades (`QGraphicsOpacityEffect` + timer).

---

## Quick wins vs. deep rebuilds

**Quick wins (hours, no architecture change):**
1. **Fix the contrast defect now.** The active-pill `accent_text` of white-on-amber (~1.9:1, `themes.py:251`) is a measurable AA failure on the *currently-selected* nav item. Change selection to a soft glow + left hearthlight bar (text stays on the dark surface) — fixes legibility *and* tones down the shout.
2. **Rename "Profile" → "Settings," and "SPACES" → drop it** (the rooms don't need an eyebrow). Rename "Library" honestly or remove it from primary nav. Re-key the theme description copy ("premium" → felt language).
3. **Move Crisis to a fixed bottom anchor** with a stable position, instead of floating as item #14 in the scroll. Same widget, pinned.
4. **Promote "Focus" out of `SECONDARY_TABS`** (`main_window.py:66`) — the flagship feature should not sit in the junk-drawer group next to the file organizer.
5. **Replace `QMessageBox` "Settings saved successfully"** with a quiet inline confirmation; kill the modal-alert feedback pattern for routine saves.
6. **Replace the tray `SP_ComputerIcon`** (`system_tray.py:49`) with even a static custom hearth glyph, and de-machine the menu copy ("Ready" → warm plain language).

**Deep rebuilds (the real work):**
1. **Collapse 15 flat tabs into ~5 rooms** with internal sub-space switchers (Reflect, Calm, Track) — the IA change. This is the highest-value structural move.
2. **Build the adaptive shell** that reads `WellnessOrchestrator` state and animates the rail's density/visibility and the app's brightness (wire up the already-defined `layout_density` / `chrome_visibility` / `animation_speed_ms` tokens). This is the thesis made visible.
3. **Replace the theme combo with "The Light"** pop-over — theme as self-care gesture, with live brightness/warmth interpolation.
4. **Replace the 7-section settings form** with a slide-over drawer for heavy settings + the feel-controls promoted into The Light. Retire the `QGroupBox`-stack Control-Panel form entirely.
5. **Custom `RoomButton` paint + tray hearth icon** — the custom-painted components that make the shell stop reading as raw Qt.
