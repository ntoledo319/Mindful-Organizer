# Audit — existing design work against `00-aesthetic-profile.md`

Written immediately after the aesthetic profile was authored, to honestly
record where the existing brief and mockups already align and where they
miss. The fixes are tracked back into the relevant documents.

---

## Where I already aligned (keep)

- **Sidebar-first layout, not tab bar.** ✓ Matches "well-designed reading app."
- **Killed the metric-tile dashboard, replaced with Today.** ✓ "No dashboards."
- **Killed streak counters and gamification.** ✓ "No streaks displayed like a Duolingo trophy case."
- **Two-type-family system (sans for UI, serif for editorial).** ✓ Matches the typography rule.
- **Crisis mode is a separate full-screen theme.** ✓ "One thing on screen at a time when the moment calls for it."
- **Voice rules banned 'optimize', infantilizing copy, exclamation points, mascots.** ✓ Aligned.
- **Single restrained accent rule.** ✓ Structurally aligned.

## Where I missed (fix)

### 1. The accent color is too saturated — **fix immediately**

My Ember theme accent: `#D97049` (coral-orange). Too vibrant. Reads like a "wellness app trying to look warm" — the exact thing the profile rejects.

The profile says muted natural materials at dusk. Better: **aged brass / muted copper / dusty rust.** Specifically:

- `#A8845F` — aged brass, my pick (reads as "kettle that's been on the hearth for years")
- `#9C7251` — muted copper (slightly more red)
- `#8B6F4E` — burnt umber (more grounded)

The accent test from the profile: *would this color sit next to "unbleached linen" or "river stone" without clashing?* `#D97049` fails. `#A8845F` passes.

**Action:** swap `#D97049` → `#A8845F` everywhere in `02-design-brief.md` and the mockups.

### 2. Motion is too snappy and includes bounce — **fix immediately**

My brief says sub-200ms with `cubic-bezier(0.34, 1.56, 0.64, 1)` for the "expressive" curve. That bezier has an overshoot (`y > 1.0`). The profile says **"never bouncy."**

The page-turn metaphor implies:
- Slower base durations — 250-400ms for state changes, 500-700ms for editorial transitions
- Pure ease-out curves — `cubic-bezier(0.2, 0, 0, 1)` or `cubic-bezier(0.25, 0.1, 0.25, 1)`
- No spring physics anywhere

**Action:** rewrite the motion section of `02-design-brief.md`:
- `motion.micro`: 80 → **120ms**
- `motion.short`: 150 → **220ms**
- `motion.standard`: 200 → **320ms**
- `motion.expressive`: 400 → **520ms**
- Replace `ease.expressive` (overshoot bezier) with a pure decelerated ease

### 3. The sans-serif may be off — **flag for decision**

The profile says "clean humanist sans." My brief picked Söhne (Klim). Söhne sits on the line between geometric and humanist — its apertures are open enough to read as humanist, but its forms are quite mechanical. Truly humanist alternatives:

- **Untitled Sans** (Klim) — softer than Söhne, same publisher
- **Aktiv Grotesk** (Dalton Maag) — Swiss-humanist, used by Helvetica refuseniks
- **IBM Plex Sans** — open-source, sturdy humanist
- **GT America** (Grilli Type) — neo-grotesque with humanist breathing
- **Söhne** — defensible; reads as "premium tool"

The Tiempos serif pick is good — warm, sturdy, not generic.

**Action:** decision needed before fonts are licensed. Default to Söhne unless you say otherwise.

### 4. Some references I gave were wrong — **augment**

My references doc cited Linear, Things 3, Bear, Raycast, Notion, Cursor, etc. The profile names a *different* reference set: **Kinfolk, Aesop, Freitag, Eames House, libraries, old Moleskine packaging.** Several of my references (Linear's command-center density, Cursor's terminal warmth) push toward "tool" rather than "thoughtful room."

The profile's references push toward:
- **Aesop** — ivory + matte black + occasional amber. Materiality. No logo on the bottle. Apothecary discipline.
- **Kinfolk** — pale grey/beige + black + ochre. Quiet typography. Slow photography. Magazine layout discipline.
- **Eames House interior** — white walls + natural wood + sparing primary colors as panels. Modernist warmth.
- **Old Moleskine packaging** — black + cream + gold stamping. Restraint.
- **Freitag** — utilitarian slate + safety colors. Honest about being made of recycled truck tarp.
- **Libraries** — wood + lamp light + reading at a long table.

**Action:** add a "Materials references" appendix to `01-references.md` referencing these. The Linear/Bear references stay as *interaction-pattern* refs; the new ones become *aesthetic-mood* refs.

### 5. Banned vocabulary needs expansion — **fix immediately**

The profile explicitly bans the word **"journey."** My brief bans many words but missed this and a few others.

Add to banned list in `02-design-brief.md`:
- *journey*
- *we* used as the app (*"we thought you'd like…"*, *"how are we feeling today?"*)
- *friend*
- *buddy*
- *family* (used about users)
- *let's* (as a softener)
- *grab* (*"grab a few minutes…"*)
- *quick* (as a softener — "a quick check-in")

### 6. Some mockup copy is too curated — **fix**

The mockup says *"Right now"* as a section label. Borderline — could read curated. Acceptable for now but flag for review.

The mockup says *"The next thing"* as another label. Plainer would be: *"Next."*

The CTA button says *"Begin"*. Plainer: *"Start."*

Minor edits; logged.

---

## Summary of immediate revisions

| File | Change |
|---|---|
| `02-design-brief.md` | accent color, motion tokens, expand banned vocabulary |
| `01-references.md` | add Materials references appendix |
| `04-mockups/today.html` | new accent, slower motion, copy fixes |
| `04-mockups/journal.html` | new accent, slower motion |
| `04-mockups/crisis.html` | slower motion (palette is already neutral) |

## Flagged for decision (no default action)

- Sans typeface: Söhne (defensible, may not be "humanist enough") vs Untitled Sans / Aktiv Grotesk / IBM Plex Sans / GT America. I'll keep Söhne in the brief until you say otherwise.

---

*This audit is a one-time check. Going forward, the chair test, accent test, motion test, voice test, reference test, and anti-reference test from `00-aesthetic-profile.md` are the gates — applied to every screen before it ships.*
