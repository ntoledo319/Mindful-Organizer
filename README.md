# Hearth

_A desktop that adapts to your psychology._

Hearth is an offline-first desktop app for people managing ADHD, anxiety, depression, OCD, PTSD, or bipolar — built on one belief: **your computer should adapt to your psychology, not the other way around.** It's not a tracker you feed and forget. It reads your state — mood, sleep, energy — and reshapes the day around it: matching tasks to the energy you actually have, suggesting the steadying practice that fits how today feels, and keeping crisis help one click away.

Your records live in a local database on your machine. **No account, no cloud, no telemetry, and no record sync.** A session summary leaves the app only when you choose a PDF destination. Your data is yours.

## Why Hearth is different

Most wellness software tracks. Hearth _acts_ — and it acts past its own window:

- **Lowers the lights when you're drained** — when your own mood/energy readings say you're running low, Hearth eases a warm dim over the whole screen so a tired hour stops shouting at you. Off, automatic, or always-on; depth is yours to set. Toggle it in one click.
- **Holds the door during a focus block** — start a focus block and Hearth raises a calm full-screen hold over everything else until the time is up. Three always-there exits: the on-screen link, the Escape key, or the tray. It guards focus; it never traps you.
- **Lives in the tray** — quiet controls and a way back to Hearth from the menu bar, plus gentle, conservative notifications (a focus block finished; an urgent signal in your own data). Never a diagnosis.
- **Energy-budgeted tasks** — every task carries a "spoon" cost, and your daily budget shifts with the conditions you carry. Hearth recommends only the work that fits the energy you have left, so a tired day never becomes an overcommitted one.
- **A morning that reads you** — the Today view opens with a briefing drawn from your own recent data: an energy forecast, what Hearth noticed, and one gentle next step.
- **Crisis-aware, not crisis-blind** — conservative heuristics watch for patterns (a mood crash on short sleep, a rapid drop, elevated energy with no rest) and surface the 988 lifeline and your own crisis plan _before_ you have to go looking.
- **Practices chosen for the moment** — box breathing, 5-4-3-2-1 grounding, a body scan, or a protected focus block — picked to match a low-energy, low-mood, or short-sleep day.

Every one of these runs locally. The dim and the focus hold are plain Electron windows on your own machine; the "signals" are heuristics over the same local SQLite. Nothing about how Hearth acts requires — or makes — a network call.

> Hearth is a personal, mental-health-aware tool. It is **not** a medical device and not a substitute for professional care. Its signals are gentle observations, not a clinical instrument. If you are in crisis, call or text **988** (US) or your local emergency number.

## Feature tour

| Area          | What it does                                                                                  |
| ------------- | --------------------------------------------------------------------------------------------- |
| **Today**     | Daily briefing, energy-budget meter, crisis banner, and an energy-matched next step.          |
| **Tasks**     | Priority + area + energy, with an automatic spoon-cost estimate and energy-aware ordering.    |
| **Reflect**   | Quick mood / energy / anxiety check-ins, sleep logs (auto-computes duration), and journaling. |
| **Practices** | Guided breathing with a breath pacer, grounding, meditation, and focus blocks — pre/post SUDS.|
| **Rhythm**    | Mood, energy, and sleep trends over 7 / 14 / 30 days. Patterns, not performance.              |
| **Session summary** | A user-requested 7 / 14 / 30 day PDF of those trends, saved only to the location you choose. |
| **ERP & diary** | Exposure-session notes and structured diary cards, stored locally for personal reflection. |
| **Medications** | A reference list for names, doses, and usual times; Hearth does not issue medication reminders. |
| **Crisis plan** | Warning signs, what helps, trusted contacts, and a note to your future self — stored locally. |
| **Presence**  | The acting layer: a screen-wide dim when you're drained, a calm hold over a focus block, and a tray you can steer Hearth from. Set it all under Settings → _How Hearth shows up_. |

## Tech stack

| Layer        | Technology                                                          |
| ------------ | ------------------------------------------------------------------- |
| Shell        | Electron 43 (sandboxed, context-isolated, no Node integration in the renderer) |
| UI           | React 18 + TypeScript + Vite 6                                      |
| State (Sync) | Zustand (Global App State & Settings)                               |
| State (Async)| TanStack Query / React Query (Data Fetching & Caching)              |
| Styling      | Tailwind CSS — "Earthenware & Vellum" semantic design system        |
| Motion       | Framer Motion (Critically damped springs for accessibility)         |
| Persistence  | SQLite via `better-sqlite3` (WAL mode), in the main process         |
| Intelligence | Wellness orchestrator + crisis heuristics ported to TypeScript      |
| Packaging    | electron-builder → macOS `.zip` (.app), Windows NSIS + portable     |
| CI           | GitHub Actions matrix on `macos-latest` + `windows-latest`          |

Type display is **Fraunces** (serif), body is **Atkinson Hyperlegible**. 

For detailed technical and design guidelines, refer to:
- [Architecture Documentation](docs/ARCHITECTURE.md)
- [Design System & Typography](docs/DESIGN_SYSTEM.md)
- [Privacy Policy](docs/PRIVACY.md)

## Quickstart

Prerequisites: **Node.js 22.12+** and npm.

```bash
npm install
npm run icons   # derive build/icon.{png,ico,icns} from resources/app-icon.png
npm run dev     # launches Vite + Electron with hot reload
```

## Quality checks

```bash
npm run lint        # ESLint, zero-warning policy
npm run typecheck   # tsc for both the renderer and the Electron main process
npm test            # Vitest unit tests
```

## Building installers

```bash
npm run icons       # once, to generate the packaging icons
npm run build:linux # AppImage (unpacked) — proves the packaging config
npm run build:mac   # .zip of the .app (x64 + arm64), unsigned
npm run build:win   # NSIS installer + portable .exe
```

Output lands in `release/`. Builds are **unsigned** — on first launch macOS Gatekeeper and Windows SmartScreen will ask you to confirm.

### Automated releases

`.github/workflows/release.yml` runs a matrix on `macos-latest` and `windows-latest`. On every run it lints, typechecks, tests, builds, and uploads the installers as workflow artifacts. Trigger it manually:

```bash
gh workflow run release.yml --ref main
```

or by pushing a `v*` tag. Download the `hearth-macos` / `hearth-windows` artifacts from the run's summary page.

## Project layout

```
electron/            Main process — window, SQLite store, IPC, wellness engine
  main.ts            App lifecycle + one IPC handler per API method
  db.ts              SQLite schema + connection (WAL)
  repo.ts            Data access (tasks, mood, sleep, journal, practices, plan)
  wellness.ts        Snapshot, crisis heuristics, daily briefing, trends
  preload.ts         Context-isolated bridge built from the shared contract
src/shared/          Types + IPC contract + spoon logic (shared, testable)
src/renderer/        React UI
  screens/           Onboarding, Today, Tasks, Reflect, Practices, Rhythm, Crisis, Settings
  components/         Icons, UI primitives, breath pacer
resources/           Brand assets (app-icon, hero-illustration)
scripts/             Icon generation
build/               electron-builder resources (icons generated here)
```

## Microsoft Store status

The Partner Center identity in `store/identity.json` is real and `npm run store:check` returns `true`, but the current build is **not submitted or purchasable**. The proposed commercial model is a one-time paid official Windows package while the source remains MIT-licensed. A Store purchase would pay for the packaged binary and distribution convenience, not exclusive access to the source.

Paid-product price, listing metadata, package upload, and submission must be completed manually in Partner Center. The old automated publisher was removed after its metadata mutation failed and because downloading an unpinned Store CLI is not an acceptable release path. `windows-store.yml` builds a review artifact; it does not publish. See [`store/README.md`](store/README.md) for verified blockers and the release checklist.

## Privacy

Hearth stores records in local SQLite files in your OS app-data directory and does not transmit them. A session summary PDF is written only after you choose its destination. The renderer is sandboxed, context-isolated, and limited to a typed IPC bridge whose calls are accepted only from Hearth's own main frame. The local database is **not application-level encrypted**; read [docs/PRIVACY.md](docs/PRIVACY.md) before using it for sensitive information.

## License

MIT — see [LICENSE](LICENSE). Packaged builds also include the project license and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
