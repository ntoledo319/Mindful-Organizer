# Hearth — Information Architecture

**Phase 1 · Task 27 · Status: draft 1**
**Depends on:** `01-references.md`, `02-design-brief.md`
**Feeds into:** `04-mockups/` (HTML prototypes), Phase 2 (FastAPI route design)

This document maps every screen in Hearth, the hierarchy between them, the key flows users actually take, and the keyboard model. The current PyQt6 app has 15 primary tabs — most of them rarely visited. We cut to **8 primary surfaces** and reorganize what remains around *what a user actually does*, not *what the codebase has a module for*.

---

## I. The fundamental shift — from "tabs of features" to "surfaces of life"

The current UI is structured by what the engineering team built: each module gets a tab. The redesign is structured by **what the user is doing in their life at this moment**:

| Current tab | What was wrong | Where it goes now |
|---|---|---|
| Dashboard | Metric tiles. Looks like an admin panel. Nobody opens it to *do* anything. | Killed. Replaced by **Today**. |
| Tasks | Generic todo list. Not the differentiator. | Folded into **Today** as the "What's actionable" section. |
| Mood | Single-purpose form. Most users skip it because it's friction. | Folded into **Journal**. Quick-entry via command palette. |
| Diary Card | DBT-specific, daily ritual. | Folded into **Journal** as a daily structured-entry mode. |
| Journal | Free-form text. | Becomes **Journal** — the single timeline of *what happened today and how it felt*. |
| Breathing | One screen for one exercise. | Folded into **Practice**. |
| ERP | Condition-specific exposure tracker. | Folded into **Practice** (visible only with OCD condition). |
| Meditation | Audio player + library. | Folded into **Practice**. |
| Grounding | Walk-through exercises. | Folded into **Practice**. |
| Sleep | Sleep tracker. | Folded into **Sleep & Body**. |
| Medication | Medication reminders + adherence. | Folded into **Sleep & Body**. |
| Files | The condition-aware file organizer. Currently broken-ish. | **Demoted** — accessible from command palette, not in sidebar. |
| Automation | Pro feature for system automation. | Becomes **Focus** (combines automation rules, focus mode, app guardian, display adaptation). |
| Crisis Plan | Always-relevant safety surface. | **Crisis** — always present in chrome, but as a single floating button, not a tab. |
| Settings | Settings page. | Folded into **Profile**. |
| Panic Log | Condition-specific tracker. | Folded into **Journal** as an entry type. |

---

## II. The eight primary surfaces

### 1. Today — the home screen

The default screen on launch. Replaces "Dashboard." Single vertical column, 640px max width.

**Structure (top to bottom):**
- **Right now** — a single sentence describing the current psychological state Hearth has detected. *"Your energy is mid-day, a notch below baseline. Two tasks open."* Plain text, no chart.
- **The next action** — one large card with the single most important thing the user could do in the next 5 minutes. May be a task, a wellness check-in, a focus session, or "nothing — you're caught up."
- **Today so far** — a quiet timeline of significant entries (mood logged at 9:14am, focus session 10:00-10:45, sleep entry from this morning). Each entry is a single line with a left-edge color stripe (per design brief).
- **Open loops** — the 3-5 most actionable items from across the system (incomplete tasks, missed medication, automation pending confirmation). Each is a one-line interactive row.

No charts, no metric tiles, no "your streak is 7 days." Just *what's happening and what's next.*

### 2. Journal — the timeline of how today felt

A single chronological surface for everything the user writes or logs about their emotional/cognitive experience.

**Entry types:**
- **Quick mood** — single tap from anywhere; appears in journal as a small entry
- **Diary card** — daily structured entry (DBT style); appears as a card-style entry
- **Free-form journal** — long-form text with optional prompt; appears as an editorial-typography entry
- **Panic log** — structured entry for panic episodes (visible if Anxiety/Panic condition active)
- **Trigger note** — quick "I noticed X triggered me" entry

**View options:** day, week, month (calendar view of entry density). Default: day view.

**Why this consolidation:** the current product makes the user pick a tab before logging. Hearth doesn't care which type — it's all just *journaling*. The form follows the user's intent, not the engineer's data model.

### 3. Practice — the therapeutic exercise library

Everything the user might *do* therapeutically: breathing, meditation, grounding, ERP exposure runs.

**Structure:**
- A list of available practices, grouped by purpose: *Regulate* (breathing, grounding), *Process* (meditation, journaling prompts), *Confront* (ERP — visible only with OCD).
- Tapping a practice opens it as a focused full-screen runner with minimal chrome — the breathing animation, the meditation player, the ERP timer.
- After completion: a single line written to the journal with the practice name and duration.

### 4. Sleep & Body — embodied tracking

Two related but distinct surfaces:
- **Sleep** — 3-tap entry (bedtime, wake, quality), with a 14-day trend strip across the top
- **Medication** — adherence log + refill reminders + side-effect notes

**Why combined:** both are about body-state inputs that affect everything else. Both are *quick logging* tasks, not deep interactions.

### 5. Focus — the OS-level intervention layer

Where Pro/Premium users configure the automation engine.

**Sections:**
- **Current state** — what Hearth is currently doing (autonomous mode active, focus session running, app guardian watching X)
- **Rules** — the 11 default automation rules + custom rules (Premium)
- **Focus sessions** — start a focus session manually; history of past sessions
- **Display adaptation** — preview of how display tuning responds to state
- **App guardian** — list of apps Hearth will manage

### 6. Crisis — always one click away

**Not a sidebar item.** A persistent floating action button (bottom-right of every screen) plus a global keyboard shortcut (`Cmd+Shift+C`).

Triggers full-screen takeover with Quiet theme. Three large buttons:
- **Call 988** (US Suicide & Crisis Lifeline)
- **Text the Crisis Line** (text HOME to 741741)
- **Show me what to do right now** (opens the user's saved crisis plan)

A fourth quiet button: *I'm safe — close this.*

### 7. Library — file organization

Demoted from primary navigation. Accessible via command palette ("Go to library"). The current file-organizer feature stays available but stops competing for sidebar real estate it doesn't earn.

### 8. Profile — settings, conditions, preferences

- Account / subscription
- Conditions managed (the mental-health profile)
- Theme picker (Ember / Linen / Quiet)
- Keyboard shortcuts
- Privacy & data export
- About / version

---

## III. Sidebar layout

```
┌─────────────────────┐
│  ◊ Hearth          │  ← brand mark + Cmd+K trigger
│  ─────────────      │
│  ◯ Today           │
│  ✎ Journal         │
│  ❀ Practice        │
│  ─────────────      │
│  ☾ Sleep & Body    │
│  ◐ Focus           │
│  ─────────────      │
│  ⌂ Library         │
│                     │
│                     │
│  ─────────────      │
│  ◉ Profile  ⚙       │  ← profile switcher + settings
└─────────────────────┘
                  [✦]   ← floating Crisis button, bottom-right of viewport
```

- 220px wide expanded, 56px collapsed (icon-only)
- Active item: warm accent left-stripe (3px wide), no background fill
- Hover: `bg.hover` background, no border
- Visual rule: at most one accent stripe visible at any time

---

## IV. Key user flows

### Flow A — First launch

1. **Welcome** — single screen. *"Hearth adapts your desktop to your psychology. Three quick questions to make it yours."* One button: *Begin.*
2. **Conditions** — multi-select chips for the six supported conditions. Plain checkboxes, no friendly mascots. *"This shapes what Hearth watches for."*
3. **First entry** — quick mood scale (1-10), optional one-line note. *"This is your baseline. Future entries are compared to it."*

Total: **3 screens.** Current onboarding is 6. The user is in the product in under 90 seconds.

### Flow B — Daily check-in

1. User opens Hearth → Today screen.
2. Top of screen shows current state. Below it: *"Log how you feel right now."* — single-tap button.
3. Tap opens a 200ms-animated quick-entry modal with mood scale + one-line note + (optional) tag chip.
4. Save closes modal, writes entry to journal, refreshes Today's *Right now* state.

Total interaction: **~4 seconds.** No tab switching, no form filling.

### Flow C — Mood quick-entry from anywhere

1. From any screen, user presses `Cmd+Shift+M` (or invokes from system tray).
2. Floating panel appears centered (Raycast-style), 480px wide.
3. Single mood scale slider + optional one-line note + Enter to save.
4. Auto-dismisses after save with a 200ms fade.

No requirement to be in the Journal tab. Logging is *ambient*, not destinational.

### Flow D — Crisis trigger

1. User presses `Cmd+Shift+C` or taps the floating Crisis button.
2. Full-screen Quiet-theme takeover, 300ms fade-in.
3. Three large buttons centered: Call 988 / Text Crisis Line / Show me what to do.
4. A fourth quiet button at the bottom: *I'm safe — close this.*

System automation runs in parallel: dims screen to 20%, mutes notifications, minimizes other windows.

### Flow E — Focus session

1. User invokes from command palette (`Cmd+K → "focus"`) or sidebar.
2. Picker: duration (25 / 45 / 90 min), profile (work / deep / creative), apps to close.
3. Confirm starts the session. Sidebar collapses. A minimal countdown appears in the chrome.
4. Mid-session: the only available actions are *End session* and *Crisis*.
5. End: a single-screen summary — what was achieved (auto-detected if possible), one-question reflection.

### Flow F — Automation rule pending confirmation (Pro)

1. Hearth detects anxiety spike. Per user's tier (PRO with "ask first" mode), a system tray notification appears: *"Close Discord, dim screen — anxiety detected. Apply?"*
2. Tray notification has three options: *Apply / Skip / Snooze 30min.*
3. Apply runs the action. Skip dismisses. Snooze defers.

No modal interruption of the user's current work. The notification is system-level, not in-app.

### Flow G — Switching profile

1. `Cmd+P` opens profile switcher (or click profile photo in sidebar bottom).
2. List of profiles with their last-active time.
3. Click switches. UI re-themes to the profile's accent color in 200ms.

---

## V. Keyboard map

The Cmd-prefixed shortcuts. Hearth is keyboard-primary; every common action has a binding.

| Shortcut | Action |
|---|---|
| `Cmd+K` | Open command palette |
| `Cmd+,` | Open settings |
| `Cmd+1` through `Cmd+7` | Jump to sidebar item by index |
| `Cmd+J` | Jump to Journal |
| `Cmd+T` | Jump to Today |
| `Cmd+P` | Profile switcher |
| `Cmd+/` | Toggle sidebar collapse |
| `Cmd+Shift+M` | Quick mood entry (floating panel) |
| `Cmd+Shift+J` | Quick journal entry (floating panel) |
| `Cmd+Shift+F` | Start focus session |
| `Cmd+Shift+C` | Crisis mode |
| `Cmd+Shift+G` | Grounding exercise (5-4-3-2-1) |
| `Cmd+Shift+B` | Breathing exercise (box breath default) |
| `Esc` | Close modal / exit focus mode / exit crisis mode |
| `Cmd+E` | Toggle Ember/Linen theme |
| `Cmd+Shift+E` | Activate Quiet theme |

All shortcuts use `Ctrl` on Windows/Linux. All shortcuts are remappable in Profile → Keyboard.

---

## VI. Progressive disclosure rules

What's visible at each level of engagement.

### At rest (no hover, no focus)
- Sidebar shows nav items only
- Cards show their content with no edit affordances
- Journal entries show preview text
- No drag handles, no kebab menus, no inline edit buttons

### On hover
- The hovered row reveals its inline actions (kebab menu, drag handle)
- The hovered item's color deepens (`bg.hover`)
- Reveal animation: `motion.micro` (80ms)

### On click / focus
- Entry expands into edit mode (`motion.expressive` 400ms, the magic-paper transform)
- Right-side inspector slides in if relevant
- Sidebar dims to draw focus to the inspector

### On Cmd+K
- Command palette floats over the viewport (200ms scale + fade)
- Background is unblurred but dimmed to 60% opacity
- All other input is ignored

---

## VII. System tray / menu bar

Hearth is a *persistent presence* on the user's machine. The Tauri shell provides:

**macOS:** menu bar app — small Hearth glyph in the menu bar, always visible. Click opens a 320px-wide popover with:
- Current psychological state (single sentence)
- Quick mood entry
- Start focus session
- Crisis button
- Open Hearth (returns to main window)

**Windows:** system tray icon — same popover, same content. Right-click for context menu (Show / Hide / Quit).

**Linux:** AppIndicator with the same popover.

Closing the main window does *not* quit Hearth — it minimizes to tray/menu bar. The agent keeps running for automation.

---

## VIII. The seven decisions this document made

These are the load-bearing IA decisions. Anything downstream that contradicts these is wrong:

1. **8 primary surfaces, not 15.** Today / Journal / Practice / Sleep & Body / Focus / Library / Profile + Crisis as floating affordance.
2. **Today replaces Dashboard.** Action-oriented, no metric tiles.
3. **Mood, diary, journal, panic log all consolidate into Journal.** The user doesn't pick a tab to log; they just log.
4. **Crisis is a floating button + global shortcut, not a sidebar item.** It's the most important surface; it deserves persistent reach.
5. **3-screen onboarding, not 6.** Welcome / Conditions / First entry.
6. **Cmd+K is the primary navigation system for power users.** Sidebar exists for discovery; palette exists for speed.
7. **Hearth lives in the menu bar / system tray.** The main window is one surface; the tray is the ambient surface.

---

**Next:** `04-mockups/` — HTML/CSS prototypes of Today, Journal, and Crisis screens. These three validate the design brief end-to-end before we commit to a React build.
