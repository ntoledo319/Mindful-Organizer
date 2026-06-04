# Audit 07 — Adaptation Surfaces (Automation / Focus + File Organizer)

**Surfaces:** `src/gui/widgets/automation_widget.py`, `src/gui/widgets/file_organizer_widget.py`
**Screenshots read:** `/tmp/hearth_ui/automation.png`, `/tmp/hearth_ui/file_organizer.png`
**Auditor stance:** ruthless, specific, first-principles. The founder called the current UI "dogshit beta bare-bones." These two surfaces carry the **entire core promise of Hearth** — "your computer protects you" — and right now they are the two screens that most violently betray it. This document explains exactly why, then rebuilds them.

---

## 1. What these surfaces are

These two screens are where Hearth's thesis either becomes real or collapses into marketing. Every other screen (mood, journal, meds, sleep) is *tracking* — things any wellness app does. **These are the only two screens where Hearth claims to ACT on the environment.** This is the differentiator. The pitch — "tools that don't just track but ACT," "mental-health tools in the OS layer," "closes Discord when anxiety spikes, dims the lights when you're drained" — lives or dies here. If these two screens feel like a settings panel and a file utility, then Hearth *is* a wellness app with extra steps, and the founder's entire premise is unproven on screen.

### Automation / Focus (`automation.png`)

**Purpose.** This is the cockpit of the protective companion. It should answer one question continuously: *"What is my computer doing to protect me right now, and can I trust it?"* It's where the user grants the app permission to reach into their OS — dim the display, close apps, silence notifications, guard a focus block — and where they confirm it's actually doing those things.

**The user's state when they reach it.** Rarely curious, usually one of:
- **The skeptic.** "You're telling me an app will close my apps and change my screen? Prove it. And prove it won't do something I don't want." Trust is conditional and fragile. One unexplained action and they uninstall.
- **The overwhelmed.** Anxiety or overload is *already* climbing. They came here to hit one button — "make it stop" / "protect me now" — not to read about execution modes.
- **The tinkerer (rare, later).** Wants to wire up custom rules. Real, but a tiny minority and never the first-run state.

**The job it must do.** (1) Make "my computer is watching out for me" *legible and reassuring* in one glance. (2) Surface the one protective action the user needs *now*. (3) Be radically honest about what it can and can't do on this machine/plan (the code already tries — see `_summarize()`). (4) Earn the right to act autonomously by being transparent first. (5) Never feel like a router admin page.

### File Organizer (`file_organizer.png`)

**Purpose.** The screen ships with a genuinely *distinctive* idea buried in its source: it reorganizes a user's files using folder structures and language tuned to their condition (`_CONDITION_CONFIGS` — ADHD gets "🚀 DO NOW," Depression gets "Gentle — Low Effort / Rest — No Action Needed," OCD gets numbered predictable folders). That is a real Hearth idea. For an ADHD or depressed user, a chaotic Downloads folder is not a tidiness problem — it's a daily source of shame and executive paralysis. Organizing it *gently, reversibly, in their language* is exactly "the warm corner of the computer."

**The user's state when they reach it.** Looking at a mess they've been avoiding, low on executive function, braced to be overwhelmed by 4,000 files. The fear is "if I touch this, I'll break it / make it worse / lose something." Reversibility and preview are not features here — they are the entire emotional contract.

**The job it must do.** (1) Make starting feel safe and small. (2) Promise — visibly — that nothing is destroyed and everything is reversible. (3) Show what *will* happen before it happens. (4) Speak in the user's condition-language. (5) Make finishing feel like relief, not like operating a utility.

Both surfaces currently do almost none of this. The screenshots show two of the most generic screens in the entire app.

---

## 2. Why they fail — forensically

### 2.A — AUTOMATION / FOCUS

#### 2.A.1 Information architecture — it's a settings dialog wearing a mission statement

Reading order, top to bottom: **title → one-line promise → a gray "Current plan: FREE" badge → a tab bar (Overview / Rules / Focus / Analytics) → Execution Mode dropdown → an upsell line → three big colored buttons → an Engine Status string with a Pause button.**

The very first interactive thing under the inspiring subtitle ("Your computer adapts to your psychological state automatically") is **a flat gray plan badge and a four-tab `QTabWidget`.** The promise says "this is alive and protecting you"; the IA immediately says "this is a preferences pane with four sub-pages, go hunt." The single most important thing — *is the engine actually doing anything for me right now?* — is shoved to the **bottom** of the Overview tab as a one-line debug string:

> `Engine: Running | Profile: Default | Mode: suggestions_only`

That line (built in `_refresh_status()`, lines 404–411) is the most important sentence on the screen and it's formatted like stderr. `Mode: suggestions_only` is a raw enum value (`.value`) leaking onto the surface. **Principle violated:** IA must follow the user's question priority. The user's #1 question ("is it protecting me?") is last, smallest, and written in machine voice. The user's #99 question ("which of four tabs holds rule cooldowns?") is first and largest.

#### 2.A.2 The tab structure is the wrong primitive entirely

Splitting Overview / Rules / Focus / Analytics into tabs (lines 117–126) shatters one coherent idea — "the engine protecting you" — into four disconnected admin pages. A protective companion is not a tabbed document. Tabs are for parallel, equal-weight content (a spreadsheet's sheets). Here the content is **one system with one state**, and tabs hide that state behind clicks. Worse: on FREE, three of the four tabs are mostly upsell walls (Rules → "🌟 Custom rule builder available with PREMIUM," Focus → "📅 Scheduled focus blocks available with PREMIUM," Analytics → "📊 Automation analytics available with PREMIUM," lines 268, 345, 361). **A new user's first encounter with the core promise is three locked doors and a 60%-empty Overview.**

#### 2.A.3 The widgets — native-Qt tells everywhere

- **`QGroupBox` for Execution Mode / Quick Actions / Engine Status** (lines 136, 162, 195). In the render, the floated uppercase legend titles **clip and collide with the card tops** — "Execution Mode," "Quick Actions," "Engine Status" are all *sliced across the top edge* (visible in the screenshot as `Execution Mode`, `Quick Actions`, `Engine Status` half-cut by the card border). This is the QSS `top: -12px` float (themes.py line 526) failing against tight `QGroupBox` margins. Clipped headers are the single loudest "unfinished beta" tell, and they appear on the flagship screen.
- **`QComboBox` for execution mode** with a 60-character label inside it: "Suggestions Only — Notify but don't change anything" (line 146). A dropdown is the wrong control for a 3-way trust decision that should feel momentous (am I letting this app *touch my computer*?). It's a form field.
- **`QTableWidget` for rules** (line 221) with columns `Rule | Trigger | Enabled | Actions | Cooldown` and cells like `Yes`/`No` and `15 min` (lines 417–422). This is a database table rendered on screen. "Cooldown," "Trigger," "Actions: 2" is engine-internal vocabulary. No human in an anxiety spike reads a 5-column grid.
- **`QTextEdit` (read-only) for analytics** filled with an ASCII report (lines 456–477): `=== Overall Stats ===`, `Total rules fired: 12`. That is **literally a logfile pasted into a text box.** It is the analytics equivalent of the "matplotlib integration" placeholder called out elsewhere in this audit series.
- **`QMessageBox.information` for grounding/crisis feedback** (lines 522, 526). When a user hits "Crisis Mode," the response is a **native OS modal dialog with an OK button**. In a crisis. A blocking system alert is the single most hostile possible response to someone who just signaled distress.

**Principle violated:** the banned "raw unstyled native OS widgets," and Hard Rule #2. Every control here is a Qt default. Swap test: this exact combo-box-plus-table-plus-status-string layout could be the settings page of a torrent client.

#### 2.A.4 The three buttons — RGB primary colors, which is exactly backwards

The Quick Actions row is three full-width buttons: **green "🎯 Activate Focus Mode," blue "🌿 Grounding Mode," red "🚨 Crisis Mode"** (lines 165–190), each with hardcoded hex (`#2ECC71`, `#3498DB`, `#E74C3C`) — **the Flat-UI / Bootstrap default palette, ignoring the theme entirely.** Onyx's actual tokens are a warm amber accent (`#D9A05B`), a sage success (`#5E9A68`), a muted danger (`#C85250`). The buttons use *none* of them. So the one screen that's supposed to feel like Hearth is painted in stock RGB traffic-light colors that appear in ten thousand other dashboards.

And the semantics are wrong. Three equal-weight, equal-size, primary-colored buttons in a row means "these are three equally likely things you might want." But a user is in exactly **one** state at a time. Presenting Focus, Grounding, and Crisis as a permanent equal triad is like a thermostat showing HEAT/COOL/EMERGENCY as three identical big buttons forever. **Principle violated:** Hard Rule #1 (no statistical-average output — this is the literal Bootstrap success/info/danger button row) and the mental-health lens (surface ONE next action, not a menu of moods).

The crisis button being a loud filled-red rectangle also fights the app's own design language: themes.py defines `QPushButton#crisisButton` as a *calm outlined* danger button (transparent fill, danger border, line 365) precisely so crisis access is present-but-not-alarming. This widget throws that away and hardcodes an alarm-red fill.

#### 2.A.5 Color / contrast / spacing

- The "Current plan: FREE" badge is `#95A5A6` (a dead gray, line 107) — the most forgettable color possible for the thing gating the whole feature, and again off-theme.
- The subtitle is hardcoded `color: #666` (line 101) on a near-black `#0F0F11` background. That's a contrast ratio around **3.4:1 — below WCAG AA (4.5:1) for body text.** The one line that sells the entire product is borderline unreadable. (themes.py has `text_muted: #8E8E93` for exactly this, ~4.6:1; the widget ignores it and hardcodes worse.)
- The upsell line is `#E67E22` (line 156), yet another off-theme orange.
- Vertical rhythm is loose and undifferentiated: three identical bordered cards stacked with equal 16px gaps, no sense that "Engine Status" matters more than "Quick Actions." Everything has the same visual weight, so nothing has hierarchy.

#### 2.A.6 Motion, feedback, states

- **No motion anywhere.** "Activate Focus Mode" produces no transition, no settling, no acknowledgment that the room just changed. The most important interaction in the app — the computer visibly taking protective action — has zero choreography. It's the difference between a bodyguard stepping in front of you and a checkbox toggling.
- **No live state.** The engine status is a static string refreshed on events. There is no sense of the engine *being alive* — no heartbeat, no "watching," no recent-action feed. So "Engine: Running" reads as aspirational, not real.
- **Feedback is a modal popup.** As above — `QMessageBox`. No empty state, no loading state, no "I'm in the middle of dimming your screen" state. Binary: nothing, then a blocking alert.

#### 2.A.7 Copy — run the swap test

- *"System Automation"* — title. Swap "Hearth" for any RMM/IT tool: still works perfectly. **Dead.** It's literally the name of a Windows control-panel category. Also borderline a "never-word" violation — this is the optimization/automation register Hearth is supposed to avoid.
- *"Your computer adapts to your psychological state automatically."* — strong sentence, genuinely Hearth, then immediately undercut by everything below it. It's a promise the screen doesn't keep.
- *"Choose how aggressively the automation engine acts on your system."* (line 139) — "aggressively," "automation engine," "acts on your system." This is the voice of a sysadmin configuring a firewall, not a companion. It makes the app sound like it might *hurt* you.
- *"Engine: Running | Profile: Default | Mode: suggestions_only"* — machine voice, pipe-delimited, raw enum. **The most generic possible string.**
- *"⚡ Upgrade to PRO to enable autonomous mode."* — "autonomous mode" is creepy in this context; it sounds like you're paying to make the robot act without you. The honest, warm version of this idea exists in `_summarize()` but isn't shown here.

The one genuinely good piece of writing on the whole surface is hidden in code, never seen unless you trigger crisis mode (lines 540–551): *"On your current plan Hearth suggests supportive changes; upgrade to Pro to let it apply them to your system automatically."* That is the right voice. It's buried in a `QMessageBox`.

#### 2.A.8 Emotional tone for THIS audience

This screen makes an app that's supposed to feel like a protective companion feel like **granting root access to a script.** Words like "aggressively," "acts on your system," "autonomous," "execution mode," combined with a literal engine-status string, read as *I am handing control of my computer to a machine and I'm not sure I can trust it.* For an anxious user, that's activating. For everyone, it kills the warmth. The thing that should feel like a hearth feels like a `crontab`.

#### 2.A.9 Where it lands: **GENERIC → SAFE-GOOD at best.** Tabbed settings panel + Bootstrap button row + status string + data table. Could be any automation tool. **The flagship surface is the most generic in the app.**

---

### 2.B — FILE ORGANIZER

#### 2.B.1 The fatal failure: the condition-awareness — the one distinctive thing — is INVISIBLE in this render

The screenshot shows the **Generic** config: folders "Quick Access / Projects / Resources / Archives," tips "Drag files into the organizer or select a folder to scan." This is the *fallback* path (`_CONDITION_CONFIGS["Generic"]`), shown because no profile condition is detected (`_detect_condition()` returns "Generic," lines 146–151). So the actual user looking at this sees **a completely generic file utility** — and the one idea that makes this screen Hearth (ADHD's "🚀 DO NOW," Depression's "Rest — No Action Needed") never appears. The distinctive feature is real in the code and dead on the screen. **Principle violated:** the whole point of behavioral tokens is that the surface *visibly adapts*; here adaptation silently degrades to GENERIC and the user never knows the feature exists.

Even when a condition *is* detected, the only signal is a tiny italic line — `"Mode: ADHD-aware organization"` (line 176) — and emoji folder names in a read-only text box. The adaptation is cosmetic relabeling, not a felt difference in the room.

#### 2.B.2 Information architecture — a utility's stack of cards

Top to bottom: **title → "Organize Files" card (Select Folder / Dry Run / Undo Last + a 0% progress bar) → "Suggested Structure" card (4 folder names in a text box + Create Structure) → "Tools" card (Find Duplicates / Batch Rename) → "Tips" card → Activity Log list.** This is a feature checklist rendered as cards. There is no narrative, no "here's the safe first step," no reassurance up front. The **safety promise** (everything is reversible, nothing is deleted, preview first) — which is the entire reason a scared user would dare touch this — is relegated to **bullet points in a "Tips" card at the bottom** (lines 286–294). The most load-bearing emotional content is the least prominent. **Principle violated:** emotional/task hierarchy. The thing that makes it safe to start should be the first thing you feel, not a footnote.

#### 2.B.3 The widgets — native-Qt utility tells

- **`QProgressBar` sitting at "0%"** with nothing running (lines 231–240). The render shows a thin bar with **"0%" centered in it for no reason** — a progress bar for an operation that hasn't started. It's visual noise that signals "unfinished." A progress bar should not exist until there's progress.
- **`QTextEdit` (read-only) for "Suggested Structure"** showing `📂 Quick Access / 📂 Projects / ...` (lines 248–259). Using an editable text widget to display a folder list — that the user can click into but not edit — is a native tell. In the render the folder emoji rendered as **generic gray document/box glyphs**, so it looks like broken icons, not folders.
- **`QListWidget` as "Activity Log"** (line 189) that will render results as run-on strings: `"Preview: 12 moved, 3 skipped, 0 errors"` and `"  → Documents: report.pdf"` (lines 320–326). Comma-delimited stat string + indented arrow lines = **a console dump in a list box.** "12 moved, 3 skipped, 0 errors" is the voice of `rsync`, not Hearth.
- **Plain `QPushButton` for Dry Run / Undo Last / Find Duplicates / Batch Rename** — generic gray buttons, equal weight. "Undo Last" — the single most reassuring control on the screen — is a small tertiary gray button in a row, given no more prominence than "Dry Run."
- **`QInputDialog.getText` for batch rename** with the template `"{date}_{category}_{n:03d}{ext}"` (lines 385–390). A native text-input modal asking the user to type a **printf-style format string**. This is a developer feature exposed raw to people in a fragile state. `{n:03d}` on screen is a category error.

**Principle violated:** banned native OS widgets; Hard Rule #2. Swap test: this entire screen could be a freeware "Folder Cleaner" utility on a download site. Nothing about it could *only* be Hearth.

#### 2.B.4 The "Create Structure" button — the only colored thing, and it's the wrong thing to emphasize

The full-width amber `AccentButton("Create Structure")` (line 261) is the single most prominent control on the screen. But "create four empty folders" is a *minor* action. The major, scary, important action is "organize my actual files" (the Select Folder button up top, which is *also* amber but smaller). So the visual hierarchy points the user at making empty folders rather than at the thing they came to do. Meanwhile "Undo Last" — the thing that makes the scary action safe — is a tiny gray button. **The hierarchy is inverted: minor action loud, safety net quiet, primary action mid.**

#### 2.B.5 Color / contrast / spacing

- The widget hardcodes **light-mode fallbacks everywhere**: `background', '#f5f5f5'`, `text', '#333'`, `secondary', '#ccc'`, `accent', '#4a90d9'` (lines 161, 191–194, 235–238). If the theme dict ever comes through partial, this screen renders **light-on-light in the middle of a dark app** — a latent theme-break. Even when the theme is whole, the widget is one missing key away from a flashbang.
- The "Mode: …-aware" badge is italic accent color (line 178) — italics for emphasis is a weak, bloggy choice; it reads as a caption, not a signature feature.
- Spacing is driven by a density token (lines 167–168: 16/20/24px), which is good instinct — but it's the *only* thing the density token touches. Everything else (card style, control prominence, copy) is identical across conditions, so "ultra_low density for Depression" just means slightly tighter gaps on an identical generic layout.

#### 2.B.6 Motion, feedback, states

- **No motion.** Files moving — the literal act of tidying — is the most satisfying thing this screen could animate, and it animates nothing. Results just appear as text rows.
- **Empty state is absent.** Before you select a folder, the screen shows a 0% progress bar, an empty folder-name box, and an empty Activity Log. Three empty/zero elements with no guidance. The empty state should be the *most* designed state here (it's the user's first and most fearful moment) and it's the least.
- **No "dry run vs. real" distinction in feedback.** A preview and an actual irreversible move produce near-identical list output (`"Preview: …"` vs `"Organized: …"`, line 319). The single most important safety distinction — "did I just simulate this or actually do it?" — is one word in a gray list row.

#### 2.B.7 Copy — swap test

- *"File Organizer"* — title. Could be the name of any shareware utility. **Dead.** Generic to the point of parody.
- *"Suggested Structure," "Organize Files," "Tools," "Tips"* — every section header is the generic noun for the function. Swap "Hearth" for "WinDirStat": all four headers still work. **Dead.**
- *"Drag files into the organizer or select a folder to scan."* — "scan," "organizer." Utility voice.
- *"12 moved, 3 skipped, 0 errors"* — rsync voice. For an audience whose fear is "I'll lose something," the word **"errors"** in the result line is a small spike of dread with no explanation.
- The condition tips are *better* (Depression: "Even organizing one file is a win. Small steps count." OCD: "'Scratch' is a safe place for temporary files — they don't need to be perfect."). These are genuinely Hearth-voiced and genuinely kind — and they're **buried at the bottom in a bullet list**, the least prominent slot on the screen. The good copy exists; the layout hides it.

#### 2.B.8 Emotional tone

A scared, low-executive-function person opens this to face a mess they've avoided for months, and Hearth greets them with a **file utility**: a 0% progress bar, a list of empty folder names, four equal gray buttons, and a console-style activity log. There is no "this is safe," no "start small," no warmth, no acknowledgment that touching your own files is frightening. The reassurance the audience needs is technically present (Undo, Dry Run, the tips) but visually demoted into invisibility.

#### 2.B.9 Where it lands: **GENERIC.** A condition-aware idea wrapped in a stock file-utility skin, rendered in its generic fallback. The distinctive feature is invisible; what's visible is shareware.

---

## 3. The reimagination

### Shared principle: stop building **panels**, start building **a presence**

Both surfaces fail the same way — they're *configuration*, when they should be *companionship made visible*. The fix for both is the same conceptual move: **the screen should be a live depiction of the companion's protective state, not a form for adjusting it.** Adjustment is secondary and tucked away. Presence is primary.

---

### 3.A — AUTOMATION → "The Hearthroom" (the protective state, made visible)

**Kill the tabs. Kill the engine-status string. Kill the three RGB buttons.** Replace with a single, calm, full-bleed surface that answers "what is my computer doing for me right now?" before the user finishes reading.

#### New IA (one scrolling room, no tabs)

1. **The Hearthstone (signature element).** A single large, custom-painted focal element at top center — a slow-breathing warm ember/glow rendered with `QPainter` + radial gradient, whose **color, brightness, and breathing rate are the live state of the engine.** This is the behavioral token made literal:
   - Engine watching, calm → warm amber (`accent #D9A05B`), slow ~6s breath.
   - Focus mode active → steadier, brighter, the breath calms to near-still (the room "holds its breath" to protect you).
   - Grounding → cooler, slower, dimmer (`success`-sage tint), the room exhales.
   - Crisis → does NOT turn alarm-red; it **dims everything else and steadies into a single warm point** — the companion narrowing its attention to you.
   - Engine paused → the ember banks to a dim coal. *You can see at a glance that protection is off.*
   Built with: a `QWidget` overriding `paintEvent`, a `QPropertyAnimation` on a custom `glow` property driving a `QRadialGradient`, `update()` on a `QTimer` for the breath. This is the screen's heartbeat. **It could only exist in Hearth.**

2. **One sentence of plain truth, in Hearth's voice, large.** Replaces the pipe-delimited status string. State-driven:
   > "I'm keeping an eye on things. Nothing's changed your setup — I'll suggest, not act, until you say so."
   (FREE / suggestions-only)
   > "Focus is on. I've quieted notifications and I'm guarding this block for the next 22 minutes."
   (Focus active, Pro)
   This *is* the honest `_summarize()` copy, promoted from a hidden `QMessageBox` to the hero line.

3. **The one next action, state-aware (not a triad).** Instead of three permanent equal buttons, show **one primary protective action chosen for the user's current state**, with the others demoted to quiet text affordances. A drained user sees one warm "Dim the room and protect a focus block" button; an anxious user sees "Ground me — I'll close the noisy apps and slow things down." The full set lives behind a small "Other ways to help" reveal. This is the mental-health lens (surface ONE next action) made structural. Use the theme tokens: amber for the primary protective action, the *outlined calm* `#crisisButton` style for crisis (never filled alarm-red).

4. **The recent-care feed (replaces the rules table AND the analytics logfile).** A short, reverse-chronological, human-voiced ledger of what the companion has actually done:
   > "2:14pm — Lowered your brightness as the afternoon dipped."
   > "1:50pm — Closed Discord when your focus block started."
   > "Yesterday, 9pm — Suggested winding down. You weren't ready, so I waited."
   This makes the engine *legible and trustworthy* — you can see it acting, and see it respecting your "no." It does the job the `QTableWidget` and the ASCII analytics dump completely fail at. Built as a custom `QListWidget` with delegate-painted rows or stacked card widgets (no grid lines, no columns). This single element converts "I gave an app root access" anxiety into "I can see exactly what my companion did, and undo any of it."

5. **Trust controls, tucked under a "How much should I help?" reveal.** The execution-mode decision reframed from "how aggressively the engine acts" to a warm, momentous three-step trust dial: **"Just tell me" → "Ask me first" → "Go ahead, I trust you."** Custom segmented control (three painted segments, `QPropertyAnimation` sliding the selection), not a `QComboBox`. The Pro gate becomes "Letting Hearth act on its own is part of Pro" — honest, not "autonomous mode."

#### Signature moment #1 — **the room responds when you press the button.**
When the user activates Focus, the Hearthstone visibly calms and the *entire surface dims its chrome by ~15%* over ~600ms (`QGraphicsOpacityEffect` + `QPropertyAnimation` on non-essential elements), as if the room itself lowered the lights to help you concentrate. The app doesn't *say* "focus mode on" in a popup — it **becomes** focus mode in front of you. That's "closes Discord, dims the lights" made visible on Hearth's own surface. No other app does this because no other app's thesis is "the computer adapts to you."

#### Signature moment #2 — **banking the coals.**
When the engine is paused, the Hearthstone doesn't just gray out — it **slowly banks to a dim coal**, and the hero copy reads "I've stepped back. You're on your own for now — tap when you want me watching again." Resuming reignites it with a brief warm bloom. Pausing your bodyguard should *feel* like something, and unpausing should feel like relief.

#### Copy voice
First-person, warm, honest, never "aggressive/engine/autonomous/optimize." The companion speaks: "I'm watching," "I quieted your notifications," "I'll wait," "I stepped back." Crisis copy stays calm and specific, never alarmist.

---

### 3.B — FILE ORGANIZER → "Tidying, gently" (a guided, reversible, condition-shaped act)

**Make the condition-awareness the first thing you feel. Make safety the spine, not a footnote. Make finishing feel like relief.**

#### New IA (a guided, three-beat flow — not a card checklist)

1. **Open in the user's language, loudly.** The condition adaptation becomes the *frame*, not an italic caption. For a depressed user the screen opens: *"Let's tidy a little. We'll go gently — nothing gets deleted, and you can undo anything."* For ADHD: *"Let's clear the chaos. Pick a messy folder and I'll sort it into spots you can actually find."* This is the behavioral token as **tone of the whole room**, driven by `_detect_condition()`. And critically: **if condition is Generic/unknown, the screen should still be warm — not the shareware fallback it is now.**

2. **One inviting first step.** A single, large, friendly drop-target / "Choose a messy folder" zone — a custom-painted dashed-warm `QFrame` that accepts drag-and-drop (`setAcceptDrops`, `dragEnterEvent`/`dropEvent`) and glows on hover. This is the empty state, and it's the *most* designed element, not the least. No progress bar exists yet — progress appears only when there's progress.

3. **Preview as the default, framed as safety — not a secondary "Dry Run" button.** Selecting a folder **always previews first.** The result isn't a console string; it's a calm, human summary with the structure shown as **real folder cards** (custom widgets, not a `QTextEdit`), each labeled in the user's condition-language ("🚀 DO NOW — 14 files would move here"). The big reassuring promise — *"Nothing has moved yet. This is just a preview."* — is the hero line of this beat, with a single warm "Looks right — tidy it for real" confirm and an equally available "Not yet."

4. **The tidy itself — animated, satisfying, reversible.** On confirm, files visibly *settle* into their folders: a lightweight `QPropertyAnimation` sweep down the list as each item is filed (no need to animate real file I/O — animate the representation). The result copy is relief, not stats: *"Done. 14 things found their place. You can undo this anytime today."* — with **Undo promoted to a persistent, prominent, always-reachable affordance**, not a gray tertiary button.

5. **Tools and structure-creation demoted** to a quiet "More" area. "Batch Rename" never exposes a raw `{n:03d}` format string — it offers 2–3 named, previewed patterns ("By date," "By type and number") with a live example, no printf.

#### Signature moment #1 — **"one file is a win" for the depressed/low-energy state.**
When density is `ultra_low` (Depression), the screen doesn't just shrink gaps — it changes the *offer*. It proposes tidying **a single drawer, not the whole room**: *"We don't have to do all of it. Want to just clear the screenshots off your desktop? That's enough for today."* with one tiny, achievable action. Finishing it triggers a soft warm acknowledgment. This is the condition-token producing a genuinely different *interaction*, not a different stylesheet — exactly what the brief asks for, and impossible in a generic file utility.

#### Signature moment #2 — **the reversible promise, shown not stated.**
Every tidy leaves a visible "undo thread" — a quiet timeline at the bottom ("Tidied your Downloads · 2:40pm · undo") that persists for the session. The user can *see* the safety net existing. Fear of "I'll break something" is answered by a permanent, visible escape hatch rather than a bullet in a Tips box.

#### Copy voice
Gentle, first-person-plural for the scary parts ("let's," "we'll go gently"), never "scan/organizer/errors." Replace "errors" with honest-but-soft language ("3 files I left alone — they weren't sure where to go"). Promote the existing good tips into the flow as inline reassurance at the moment of fear.

#### Qt mechanisms (both surfaces, concrete)
- Custom `paintEvent` widgets for the Hearthstone ember and the folder/structure cards (replace `QGroupBox`, `QTextEdit`, `QTableWidget`, `QListWidget`-as-log).
- `QPropertyAnimation` / `QSequentialAnimationGroup` for the breath, the room-dimming on Focus, the file-settling, the segmented trust dial. Respect `ThemeManager.reduced_motion` and `animation_speed_ms` (Quiet theme = 0ms → instant, no motion).
- `QGraphicsOpacityEffect` for chrome-dimming during Focus.
- Drag-and-drop (`setAcceptDrops`) for the folder drop-target.
- **Use the theme tokens, not hardcoded hex.** Every `#2ECC71`/`#3498DB`/`#E74C3C`/`#666`/`#f5f5f5` in both widgets must become `accent`/`success`/`danger`/`text_muted`/`background`. This alone fixes the off-theme RGB look and the WCAG contrast failure.
- Replace every `QMessageBox` feedback with inline, in-surface state changes (especially crisis — *never* a blocking modal).

---

## 4. Quick wins vs. deep rebuilds

### Automation — quick wins (hours, high impact)
- **Delete the hardcoded hex** on the three buttons / badge / subtitle / upsell; route through theme tokens. Kills the Bootstrap-RGB look and the sub-AA `#666` subtitle contrast immediately.
- **Replace the engine-status string** `Engine: Running | … | Mode: suggestions_only` with the honest `_summarize()`-style sentence in Hearth's voice. Stop printing raw enum `.value`.
- **Fix the clipped `QGroupBox` titles** — either give them more top margin or (better) replace `QGroupBox` with `CardFrame` + a `SectionTitle`. Removes the loudest "beta" tell.
- **Make crisis feedback non-modal** — at minimum stop using `QMessageBox` for the crisis path; show inline. (Safety + tone.)
- **Reframe the three buttons' copy** away from "aggressively/engine/autonomous."
- **Promote crisis to the calm outlined `#crisisButton` style** that already exists in the theme.

### Automation — deep rebuilds
- The Hearthstone live-state ember and the room-dimming Focus choreography.
- Collapsing the four tabs into one scrolling "Hearthroom."
- The human-voiced recent-care feed replacing both the rules table and the analytics logfile.
- The segmented trust dial replacing the execution-mode `QComboBox`.

### File Organizer — quick wins (hours)
- **Hide the progress bar until progress exists** (remove the idle "0%").
- **Remove light-mode hardcoded fallbacks**; pull from theme tokens (fixes latent light-on-dark break).
- **Promote the safety promise** out of the Tips bullet list into a prominent line near the top, and **promote "Undo"** to a persistent prominent affordance.
- **Make the condition adaptation visible** even when present — turn the italic "Mode: X-aware" caption into a real, warm opening line; ensure Generic still reads as Hearth, not shareware.
- **Soften "12 moved, 3 skipped, 0 errors"** into human language; never say "errors."
- **Replace the `{n:03d}` batch-rename input** with named, previewed patterns.

### File Organizer — deep rebuilds
- The guided preview-first flow with real folder cards (replace `QTextEdit`/`QListWidget`-as-log).
- The drag-and-drop warm drop-target empty state.
- The file-settling animation and the relief-framed completion.
- The condition-token-driven *interaction* changes (the "just one drawer" offer for low-energy states), not just spacing differences.

---

## 5. The single most important move per surface

- **Automation:** stop rendering the engine as a settings panel with a status string, and render it as a **living, breathing protective presence** (the Hearthstone) whose visible state *is* the engine's state — turning "I gave an app control of my computer" anxiety into "I can see my companion watching, see what it did, and undo anything." Presence over configuration.
- **File Organizer:** make the **condition-awareness and the reversibility promise the first things the user feels** — open in their language, preview-by-default framed as safety, Undo always visible — so a scared person experiences "we'll go gently, nothing breaks" instead of a generic file utility with a 0% progress bar.
