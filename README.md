# Hearth

_A desktop that adapts to your psychology._

Hearth is an offline-first desktop app for people managing ADHD, anxiety, depression, OCD, PTSD, or bipolar — built on one belief: **your computer should adapt to your psychology, not the other way around.** It's not a tracker you feed and forget. It reads your state — mood, sleep, energy — and reshapes the day around it: matching tasks to the energy you actually have, suggesting the steadying practice that fits how today feels, and keeping crisis help one click away.

Everything lives in a single local database on your machine. **No account, no cloud, no telemetry, no network calls.** Your data is yours.

## Why Hearth is different

Most wellness software tracks. Hearth _acts_:

- **Energy-budgeted tasks** — every task carries a "spoon" cost, and your daily budget shifts with the conditions you carry. Hearth recommends only the work that fits the energy you have left, so a tired day never becomes an overcommitted one.
- **A morning that reads you** — the Today view opens with a briefing drawn from your own recent data: an energy forecast, what Hearth noticed, and one gentle next step.
- **Crisis-aware, not crisis-blind** — conservative heuristics watch for patterns (a mood crash on short sleep, a rapid drop, elevated energy with no rest) and surface the 988 lifeline and your own crisis plan _before_ you have to go looking.
- **Practices chosen for the moment** — box breathing, 5-4-3-2-1 grounding, a body scan, or a protected focus block — picked to match a low-energy, low-mood, or short-sleep day.

> Hearth is a personal, mental-health-aware tool. It is **not** a medical device and not a substitute for professional care. Its signals are gentle observations, not a clinical instrument. If you are in crisis, call or text **988** (US) or your local emergency number.

## Feature tour

| Area          | What it does                                                                                  |
| ------------- | --------------------------------------------------------------------------------------------- |
| **Today**     | Daily briefing, energy-budget meter, crisis banner, and an energy-matched next step.          |
| **Tasks**     | Priority + area + energy, with an automatic spoon-cost estimate and energy-aware ordering.    |
| **Reflect**   | Quick mood / energy / anxiety check-ins, sleep logs (auto-computes duration), and journaling. |
| **Practices** | Guided breathing with a breath pacer, grounding, meditation, and focus blocks — pre/post SUDS.|
| **Rhythm**    | Mood, energy, and sleep trends over 7 / 14 / 30 days. Patterns, not performance.              |
| **Crisis plan** | Warning signs, what helps, trusted contacts, and a note to your future self — stored locally. |

## Tech stack

| Layer        | Technology                                                          |
| ------------ | ------------------------------------------------------------------- |
| Shell        | Electron 33 (context-isolated, no node integration in the renderer) |
| UI           | React 18 + TypeScript + Vite 6                                      |
| Styling      | Tailwind CSS — warm cream, sage, eucalyptus, lavender; light + dark |
| Motion       | Framer Motion                                                       |
| Persistence  | SQLite via `better-sqlite3` (WAL mode), in the main process         |
| Intelligence | Wellness orchestrator + crisis heuristics ported to TypeScript      |
| Packaging    | electron-builder → macOS `.zip` (.app), Windows NSIS + portable     |
| CI           | GitHub Actions matrix on `macos-latest` + `windows-latest`          |

Type display is **Fraunces** (serif), body is **Inter**.

## Quickstart

Prerequisites: **Node.js 20+** and npm.

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
gh workflow run release.yml --ref production-overhaul
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

## Privacy

Hearth opens exactly one file — a local SQLite database in your OS app-data directory — and makes no network requests. The renderer runs with `contextIsolation` on and `nodeIntegration` off; it can only reach the data layer through a typed, allow-listed IPC bridge.

## License

MIT — see [LICENSE](LICENSE).
