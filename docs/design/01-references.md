# Hearth — Visual & Interaction Reference Library

**Phase 1 · Task 25 · Status: draft 1**

This is the input to the design brief. Every claim here should drive a concrete design decision in `02-design-brief.md`. Read with one question in your head: *"would Hearth feel cheapened or strengthened by stealing this?"*

---

## Part I — The references (what Hearth steals)

### 1. Linear — `linear.app`

**Visual identity.** Linear redefined "premium SaaS aesthetic" by refusing the bright-color-and-friendly-illustrations playbook the 2018-era productivity tools chose. Dark by default. Surfaces are near-black with a faint warm tint (`#08090A` background, `#1F2023` raised panels), never pure black. Accent: a deep electric indigo (`#5E6AD2`) that appears sparingly — usually as a single focused stroke or active-state cue.

**Typography.** Inter Variable across the entire UI. Inter Display is used for marketing/headings to add slight expression. The body text is genuinely small (13px effective) and tightly tracked, signaling *density-as-respect-for-time*. There are exactly three text sizes in the working UI: 13 (body), 11 (metadata), 17 (page titles). No `text-xl text-2xl text-3xl text-4xl` stack.

**Color.** Functional, never decorative. Status colors (`#26B5CE` info, `#5E6AD2` primary, `#7C8DC8` neutral-violet, `#EB5757` destructive) and absolutely nothing else. No pastel illustration accents. No "category color tagging" that pollutes the eye.

**Density.** *Dense but never cramped.* 8pt grid, 12-16px component padding, 4-6px list-item padding. Information layered through hierarchy of weight and color, not through whitespace inflation. Counter to current "spacious is premium" tendency.

**Motion.** Sub-200ms transitions on everything. Their command palette opens with a 120ms scale-and-fade. The signature move: state changes (status pill flipping, issue moving column) animate at **150ms with `cubic-bezier(0.2, 0, 0, 1)`** — fast enough to feel mechanical, slow enough to register.

**The premium feel.** Linear feels expensive because *every micro-interaction is intentional*. There are no idle, decorative animations. There is no "delight" gif. The cursor changes shape exactly when it should. The keyboard shortcut hints appear exactly when they're earned. It feels like a tool designed by someone who has used too many bad tools.

**What Hearth steals:**
- Dark surfaces with warm tint (not pure black)
- Tight type scale (3 sizes max in core UI)
- Sub-200ms motion budget
- Single restrained accent color used as scarce resource
- Density as a value statement
- Command palette as primary navigation (Cmd+K)

---

### 2. Things 3 — Cultured Code

**Visual identity.** The most Mac-native productivity app shipping. Pure white surfaces. Generous whitespace. Bright icon-mark colors (sky blue, mango, leaf green) used as *category signals*, never as decoration. The design has aged remarkably well since 2017 because it bet on Apple HIG conventions rather than chasing trends.

**Typography.** SF Pro Text exclusively. Variable weights (regular for body, semibold for headings, medium for actionable text). Text sizes echo macOS system conventions: 11pt sidebar, 13pt body, 17pt window title. Reads as *native*, not webby.

**Color.** A muted palette that lets the *content* hold attention: list-mark blue, list-mark yellow, list-mark green for the standard list types. Each project gets a custom color, but the colors come from a curated set that never clashes. No raw RGB hues — every color has been desaturated slightly toward warm gray.

**Density.** Generous. ~12px between list items, ~20-24px of vertical breathing room around section dividers. Information is layered through generous gutters rather than weight contrast.

**Motion.** *Things* invented the magic-paper interaction: clicking a task expands it via a fluid transform animation that feels like origami unfolding. The expansion animation is **~400ms ease-out** with a subtle scale-and-translate. This is one of the few cases where a longer animation reads as premium rather than slow, because it's *functional* — it shows you where the task came from.

**The premium feel.** Things feels premium because *interaction physics are honored.* Drag-and-drop has weight. Reordering has snap-into-place tactility. The check-off animation is satisfying because it confirms the action completed mechanically, not just visually.

**What Hearth steals:**
- macOS native typography weights (medium > regular for actionable labels)
- Color as functional signal, not decoration
- Interaction physics — drag, drop, reorder should *feel* like weight
- Generous whitespace in the *content* views (mood entry, journal, crisis plan)
- Resist the urge to over-densify everywhere — Linear-density for lists, Things-density for content

---

### 3. Bear — `bear.app`

**Visual identity.** The best typography in a writing app shipping today. Bear treats text as the entire product. The default theme ("Solarized Light") uses a creamy parchment background (`#FDF6E3`) with deep slate text — anti-glare, anti-LCD, deeply readable for long sessions.

**Typography.** Custom-tuned editor type stack. Default writing font is **Avenir Next** on Mac, with **iA Writer Mono** and **Iowan Old Style** alternatives. Heading hierarchy uses *only weight and tracking* — no size changes for H1 vs H2 vs H3, just bolder and tighter. This is unusual and effective.

**Color.** Theme-driven. Bear ships ~20 themes; each is internally coherent. The themes are sold as a paid feature. The Solarized themes (Ethan Schoonover) are the gold standard. Themes never use more than 4-5 colors.

**Density.** Editor-first density: lots of breathing room around the text, narrow column (~600px max), wide left margin for tag pills. Sidebar is dense; editor is spacious.

**Motion.** Almost no motion. The product is text; motion would distract. Sidebar reveals are ~150ms. Tag inserts use a subtle highlight pulse (200ms). That's it.

**The premium feel.** Bear is premium because *typography is treated as the brand.* The fonts aren't free Google Fonts; they're licensed. The themes aren't generic dark/light; they're crafted. The kerning of the tag pills is hand-tuned.

**What Hearth steals:**
- Theme system that's actually *theme* (color + type + spacing), not just dark/light toggle
- Real licensed typefaces, not Inter
- Text density: narrow content columns (~600px) for reading/writing flows
- Restraint in motion — let content be the show
- Solarized-style themes as a reference for what "warm and readable" actually means

---

### 4. Raycast — `raycast.com`

**Visual identity.** The new Spotlight. Centered command-palette window that floats over everything. Translucent background with subtle vibrancy. The interaction model — type, get suggestions, hit enter — is the *entire* visual identity.

**Typography.** SF Pro Text. Tight, slightly condensed for the command list. Single-line item heights (~36px). The whole product is one list. No marketing pages inside the app.

**Color.** Deep purple-violet brand (`#FF6363` actually a coral red as accent, despite the purple wordmark). Inside the app: muted dark surfaces, soft accent colors per command type. Color usage is *light* — most pixels are neutral.

**Density.** Maximum density. List items are 36px tall. Eight visible at once. The product is built around *the user types fast* — visual surface area is a constraint, not a canvas.

**Motion.** Window appears with a 100ms scale-up + fade. Item selection is instant — no animation between item highlights. The command-running spinner is the only persistent motion.

**The premium feel.** Raycast feels premium because *latency is treated as design.* Nothing takes longer than necessary. The keyboard is the primary input. Mouse interactions exist but feel secondary.

**What Hearth steals:**
- Command palette pattern (Cmd+K) for "do anything"
- Single-line list density for action-oriented UIs (the automation rules screen, the focus mode picker)
- Latency-as-design — sub-100ms feedback on everything
- Keyboard-primary, mouse-secondary affordance
- Translucent floating panels for ephemeral interactions (mood quick-entry, crisis plan trigger)

---

### 5. Notion — `notion.so`

**Visual identity.** The "writing-as-database" aesthetic. White surfaces with warm gray accents. Deeply customizable per-page but with strong defaults. Block-based — every interactive element is a "block" with consistent handles.

**Typography.** Inter for sans-serif, Lyon for serif (premium feel), Source Code Pro for monospace. Font choice is per-page (a humanizing touch). Three text sizes only: Small, Default, Large. The simplicity is the lesson.

**Color.** Pure-grayscale by default. Colors enter as *content tags* (orange, yellow, green, blue, purple, pink, gray, brown, red) but never as chrome. Notion's chrome is exclusively black-on-white-on-gray.

**Density.** Variable per page. The sidebar is dense; the page canvas is whatever the user makes it. Notion's lesson: ship *less density chrome*, let *content density* be the user's choice.

**Motion.** Subtle. Block hover reveals the drag handle and "+" affordance via 80ms fade. Page transitions are ~200ms. Slash command menu opens at ~150ms.

**The premium feel.** Notion feels premium because *the affordances are progressive disclosure.* You don't see the drag handle until you hover. You don't see the formatting toolbar until you select text. The chrome only appears when relevant.

**What Hearth steals:**
- Progressive disclosure of chrome (hide controls until needed)
- Three text sizes (Small, Default, Large) — not eight
- Grayscale chrome, color reserved for user content/tags
- Custom font per "page type" — the journal could use Lyon serif, the dashboard Inter sans, the diary card mono — as a way to communicate the *mode*

---

### 6. Cursor — `cursor.sh`

**Visual identity.** A VS Code fork that managed to feel warmer, smarter, and less industrial than VS Code despite being technically the same codebase. The dark theme uses a warm charcoal (`#1E1E1E` base, but tinted slightly toward sepia) instead of cold blue-gray.

**Typography.** SF Pro Display for chrome, JetBrains Mono for code. Standard VS Code monospace bar (~13px). Nothing surprising.

**Color.** Warm dark surfaces. The AI chat panel uses an even warmer gradient — almost amber-tinted. Accent: a soft electric blue, used sparingly.

**Density.** Maximum (it's a coding tool).

**Motion.** Minimal. The chat streaming token-by-token is the dominant motion, and it's chosen to feel like *thinking*, not like loading. Lines fade in at the speed of reading.

**The premium feel.** Cursor feels premium because *the AI feels like a coworker, not a chatbot.* The streaming pace is engineered. The suggestion accept/reject UI is one keystroke. The chat panel doesn't compete with the editor; it sits adjacent and quiet.

**What Hearth steals:**
- Warm-tinted dark surfaces over cold dark
- Token-streaming feel for any AI-generated copy (suggestions, coping recommendations) — let words appear at reading pace
- Adjacent panels rather than modal overlays for secondary interactions
- Single-keystroke accept/reject for any AI suggestion

---

### 7. Arc Browser — `arc.net` (now `browser.company`)

**Visual identity.** A browser that felt like it was designed by painters, not engineers. Sidebar-first instead of tab-bar. Pixelated-paint feel in chrome. Custom typography. Heavy use of curved cards and gradients that *feel* hand-rendered.

**Typography.** Inter, but used with massive scale contrast — 11pt sidebar items next to 28pt section headers. The chrome reads more "magazine layout" than "browser."

**Color.** Each "Space" gets a user-chosen gradient as its identity. The browser's chrome adapts to that gradient. Result: every install of Arc *feels different* without the user having to do much.

**Density.** Sparse where Linear is dense. The sidebar has generous padding because Arc bets on *personality over efficiency*.

**Motion.** Heavy. Sidebar slide-ins are ~250ms with overshoot easing. Tab close has a satisfying squish. Sometimes too much — Arc lost users who felt the motion was performative.

**The premium feel.** Arc feels premium because *it has a point of view about how the user should organize the web.* The Spaces concept, the auto-archive after 24 hours, the side-tabs — all opinionated choices.

**What Hearth steals:**
- User-chosen accent gradient that themes the whole app (each profile gets its own visual identity)
- Sidebar-first layout for the primary nav (this matters — see IA notes)
- Opinionated default behaviors over "configure everything" panels
- Caution: don't out-motion Linear. Arc's motion budget is too generous.

---

### 8. iA Writer — `ia.net`

**Visual identity.** Distraction-free writing. The window is the canvas. No sidebar, no toolbar — just text on a wide surface, centered, with a narrow active line (focus mode dims everything except the current sentence).

**Typography.** iA Writer Duospace — a custom monospace-but-readable typeface specifically designed for writing. The font *is* the product identity. There's an entire blog post defending why monospace is correct for thinking.

**Color.** Bone-white background (`#F7F7F4`) with deep gray text (`#5F5F5F`). Dark theme inverts. Accent: a single tasteful blue for links, applied sparingly.

**Density.** Maximum whitespace. The text is the only thing on the screen.

**Motion.** Almost none. Focus mode's sentence-by-sentence dimming is a 200ms opacity transition. That's it.

**The premium feel.** iA Writer feels premium because *they're willing to remove things other apps would consider essential*. No word count by default. No formatting toolbar. No sidebar of files. Just the text.

**What Hearth steals:**
- Custom typeface as core identity (consider licensing one specifically for Hearth)
- Focus-mode pattern for the journaling screen
- The discipline to *remove*, not just *add*

---

### 9. Cron (Notion Calendar) — `notion.com/product/calendar`

**Visual identity.** The most beautiful calendar shipping. Reframed calendar UI around *visual time blocks* rather than tiny text in cells. Heavy use of meeting-color theming. Excellent typography in the event cards.

**Typography.** Inter. Event titles are 12px medium; metadata is 10px regular. Tight, readable, scannable.

**Color.** Each calendar gets a color but it's used *only as a left-edge stripe* on the event block — never as a fill. This keeps the canvas readable even with 10 calendars overlaid.

**Density.** Dense. A standard 5-day view shows 12 working hours at a glance.

**Motion.** Hover reveals quick actions in 80ms. Drag-to-reschedule has 16ms responsiveness. Time-zone toggle slides at 250ms.

**The premium feel.** Cron feels premium because *every common action is one keystroke or one drag.* Create event = type. Reschedule = drag. Join meeting = single click in the event card. Almost no menus.

**What Hearth steals:**
- Color as left-edge accent stripe pattern (for mood entries, automation triggers, focus sessions)
- One-keystroke / one-drag for common actions
- Density without visual noise — keep margins, lose chrome

---

### 10. Soulver — `soulver.app`

**Visual identity.** A "calculator" that is actually a notepad where lines do math. The closest reference in feel to what Hearth wants — *warm, helpful, present without being demanding.* Soft pastel theme defaults. Hand-crafted icon set.

**Typography.** SF Pro for text, custom-weighted numerals for math. The custom numerals are crucial — they give Soulver its hand-made feel even though Apple's SF Pro is system-standard.

**Color.** Warm pastels — pale yellow background, muted blue accents, mint-green for results. Reads as *paper and pencil*, not glass-and-aluminum.

**Density.** Notebook-density. Generous line spacing, narrow column.

**Motion.** Minimal. Numbers update live as you type — that's the motion.

**The premium feel.** Soulver feels premium because *it has a personality.* The default theme doesn't look like any other Mac app. The icon is recognizable from a screenshot. The product has *taste*.

**What Hearth steals:**
- Warm pastel base palette as an option (one of Hearth's themes should feel like this)
- The "paper and pencil" aesthetic for the journal and mood entry screens
- Live-updating values for derived metrics (energy estimate, spoon counter)
- An icon that's recognizable from a glance

---

### 11. Tot — The Iconfactory

**Visual identity.** Seven dots representing seven notes. That's the entire app. Maximum constraint = maximum identity. Each note has its own color. The colors are *the navigation.*

**Typography.** System font, monospace optional. Whatever the OS gives you.

**Color.** Seven specific colors — gray, red, orange, yellow, green, blue, purple — used as dot navigation and content backgrounds in light mode. Strong, saturated. Distinguishing each note instantly.

**Density.** N/A — there's barely a UI.

**Motion.** Switching between notes is a horizontal slide at ~200ms.

**The premium feel.** Tot is premium because *the constraint is the design.* Seven notes, no more, no less. No folders, no tags, no search. The simplicity is opinionated and stubborn.

**What Hearth steals:**
- Color-as-navigation pattern (each automation profile could get a distinct color identity)
- The discipline of *artificial scarcity* — Hearth should impose limits where competitors don't (e.g., one active focus session at a time, one mood entry per check-in)
- Hardware-keyboard switching between primary modes

---

## Part II — The anti-references (what Hearth refuses to look like)

### Calm

**Why it reads as wellness slop.** Aurora gradients (purple → teal → pink), a font choice that's trying to be "soothing" (rounded geometric sans, probably Montserrat or Avenir Next Rounded), photographic content thumbnails of mountains and lakes, hero copy like "Find your calm." Bottom tab bar with five icons trying to look like a meditation rosary. Every interaction confirms you are *consuming wellness content*.

**Specific patterns to avoid:**
- Aurora / sunset gradients of any kind
- Photographs of nature as primary imagery
- Rounded-corner everything
- The phrase "Find your..." as headline pattern
- Soft, friendly, parental copywriting voice
- Star ratings on meditation tracks (treating mental health like Spotify)

### Headspace

**Why it reads as wellness slop.** Cartoonish 2D illustration system featuring "Andy" the meditation buddy. Pastel orange/yellow/teal palette. Hand-drawn-style typography in marketing. The app feels like a children's book about emotions.

**Specific patterns to avoid:**
- Mascot illustrations
- Hand-drawn / "doodled" UI elements
- Pastel orange / mango / coral as primary brand color (this is Headspace's color; using it means inheriting the comparison)
- Animations of cute characters during loading states
- Achievement badges that look like merit badges

### Bearable

**Why it reads as wellness slop.** Bear-themed mascot. Five-point emoji-style mood selector with cartoon faces. Heavy use of charts that look like a teenager's mood diary. Color-coded "factors" that resemble TikTok category filters.

**Specific patterns to avoid:**
- Emoji or cartoon faces as mood selectors
- The "tap which face matches your feeling" UX pattern (it's infantilizing)
- Color-coded "factor" pills in a wrapping grid
- Default screen being a chart instead of an action

### Sanvello / Wysa / Replika

**Why it reads as wellness slop.** Chat-bubble UX where you "talk to your wellness companion." Friendly-bot avatars. The interface is structured around back-and-forth conversation, which medicalizes the relationship in the worst way (you = patient, app = therapist-roleplayer).

**Specific patterns to avoid:**
- Chat UI as the primary interaction
- Bot avatars / personification of the app
- Onboarding that "asks how you're feeling" before doing anything
- Streak counters and gamification of self-care
- Any UI that implies the app *cares* about you

### Daylio

**Why it reads as wellness slop.** Mood selector grid with cartoon faces. Hand-drawn "activity" icons (yoga mat, coffee cup, sleep z's). Pie charts dominating the home screen. Achievement-unlocked dopamine triggers for logging streaks.

**Specific patterns to avoid:**
- Activity icon grids of clipart objects
- Pie charts on the home screen
- "X days streak!" headers
- Color schemes that change based on mood selected

### Finch / Reflectly

**Why it reads as wellness slop.** Both lean hard into pet/character companions. Pastel everything. Animated reactions to user inputs. "Your bird is hungry, journal today!" notifications. The interaction model is *Tamagotchi-as-therapy*.

**Specific patterns to avoid:**
- Virtual pets or avatars that require the user to "feed" them with self-care
- Any notification that uses emotional manipulation ("Your X misses you")
- Daily streak gamification
- Customizing the appearance of a character

### Insight Timer

**Why it reads as wellness slop.** Marketplace UI for meditation content. Looks like a music streaming app for meditations. Featured cards with photographic backgrounds, instructor headshots in circles, star ratings, play counts.

**Specific patterns to avoid:**
- Spotify/Netflix-style carousel rows of "featured content"
- Instructor photos in circular avatars
- Play counts, ratings, social-proof badges on therapeutic content
- "Recommended for you because you completed X"

### The generic Bootstrap admin dashboard

**Why it reads as generic.** Three-column card grid on the dashboard. Stat tiles in the top row showing arbitrary numbers. Sidebar with icon + label per menu item. Tables with action buttons in the rightmost column. Filter chips above the table. This template was set in 2014 and most "admin" UIs still ship variants of it.

**Specific patterns to avoid:**
- Three-column stat-tile rows ("Total tasks: 47 | Completed this week: 12 | Active streaks: 3")
- Generic icon + label sidebar
- Bootstrap card-with-shadow grids
- Datatables with rightmost action column
- Filter chip rows above content

### The "Stripe-inspired SaaS marketing page" archetype

**Why it reads as generic.** Purple-to-blue gradient hero. Three-icon-and-text feature grid below the fold. Pricing table with three tiers and a "most popular" badge. Logo strip of customer companies. Testimonial cards with circular avatars. Footer with sitemap.

This is the most-copied SaaS layout on the web. Hearth's marketing site (when it exists) must refuse all of it.

### The "Notion-clone for productivity" archetype

**Why it reads as generic.** Sidebar of nested pages. Cmd+K command palette (Hearth wants this but for different reasons). Slash-command insertion menu. Block-based editor. Database views with toggle-between-list-and-board.

This isn't bad — it's just claimed. Hearth using these patterns means inheriting the comparison. Use them only when the alternative is materially worse.

---

## Part III — Synthesized recommendations (what Hearth steals, in priority order)

**Tier 1 — non-negotiable foundations**

1. **From Linear:** dark warm-tinted surfaces; tight 3-size type scale; sub-200ms motion budget; single restrained accent; command palette (Cmd+K) as primary navigation.
2. **From Bear:** theme system that varies color + type + spacing (not just light/dark toggle); real licensed typeface, not Inter; narrow content columns for journal/reading flows.
3. **From Things 3:** macOS-native typography weights and density in the content views; interaction physics — drag, drop, reorder should *feel* mechanical.
4. **From Soulver:** warm pastel theme option; "paper and pencil" aesthetic for mood entry and journaling; an icon recognizable from a screenshot.

**Tier 2 — applied selectively**

5. **From Raycast:** floating-panel pattern for mood quick-entry and crisis plan trigger; sub-100ms keyboard latency target.
6. **From Cron:** color as left-edge accent stripe on entries (mood, focus session, automation event), never as fill.
7. **From Notion:** progressive disclosure of chrome — hide controls until hover/focus.
8. **From Cursor:** token-streaming pace for any AI-generated copy (coping suggestions, daily briefing); adjacent-panel layout for AI vs editor.

**Tier 3 — flavors and accents**

9. **From iA Writer:** focus-mode pattern for the journal — dim everything except active sentence.
10. **From Arc:** user-chosen accent color/gradient per *profile* (work vs personal vs recovery), themes the chrome.
11. **From Tot:** color-as-navigation for switching automation profiles via keyboard.

---

## Cross-cutting principles that the references converge on

- **Dark UIs are warm-tinted, not cold-tinted.** Linear, Cursor, Raycast all use background colors with slight sepia/orange shift. The bluish dark of older Material Design reads cold.
- **Real typography is licensed, not free Google Fonts.** Bear pays for fonts. Linear paid for Inter Display customizations. Hearth should budget for one custom typeface.
- **Color is functional, not decorative.** Every reference uses color to communicate state (active/done/error/info) or category (Cron's calendar stripes, Tot's note dots), never as background pattern or "brand color splash."
- **Motion is sub-200ms or it's absent.** None of the references have animations longer than ~250ms in functional UI (Things' magic-paper expansion is the exception; it's a sub-second action).
- **The cursor and the keyboard are first-class citizens.** Every reference has a keyboard-primary path through the product.
- **Progressive disclosure beats chrome.** Notion, Linear, Things all hide affordances until needed. Hearth should follow.

---

## What this rules out for Hearth

- Aurora / sunset gradients (Calm)
- Mascots, virtual pets, character avatars (Finch, Headspace, Replika)
- Emoji or cartoon-face mood selectors (Bearable, Daylio)
- Pie charts or stat tiles on the home screen (Bootstrap admin dashboards)
- Three-card-grid feature rows in marketing (Stripe-clone SaaS pages)
- Streak counters and gamification of self-care (Daylio, Finch)
- Photographic nature imagery (Calm, Insight Timer)
- Inter as the entire type system (every SaaS ships this — Hearth needs a distinguishing serif or display face)
- Pure black or pure white as background (cold; use warm-tinted surfaces)
- Chat bubbles as primary UI (Wysa, Replika, Sanvello)

---

## Sources used

- [Linear Brand Guidelines](https://linear.app/brand)
- [linear.app design tokens at fontofweb](https://fontofweb.com/tokens/linear.app)
- [Things 3 design at MacStories](https://www.macstories.net/reviews/things-3-beauty-and-delight-in-a-task-manager/)
- [Cultured Code blog](https://culturedcode.com/things/blog/)
- [iA Writer typography manifesto](https://ia.net/writer/blog)
- [Soulver homepage](https://soulver.app)
- [Tot at iconfactory](https://tot.rocks)
- Personal knowledge of Bear, Raycast, Notion, Cursor, Arc, Cron, and the listed anti-references through direct daily use

---

**Next:** `02-design-brief.md` translates these references into concrete tokens (palette, type scale, motion curves, spacing scale) and a written voice spec.
