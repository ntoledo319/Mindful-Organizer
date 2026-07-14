# Evidence Ledger

Only observed evidence belongs here. Forecasts and target arithmetic live in
`PLAN.md` and `OPPORTUNITIES.md`.

## 2026-07-14 01:24 EDT — Cycle 0 baseline

| Metric | Observed value | Evidence |
|---|---:|---|
| Collected profit recorded in workspace | **$0.00** | No live payment rail, sale record, payout, or earnings export exists in scope |
| Gap to target | **$4,000.00** | $4,000 target − $0 ledgered collected profit |
| Public GitHub stars | 0 | Repository metadata read 2026-07-14 |
| Public GitHub forks | 0 | Repository metadata read 2026-07-14 |
| Public GitHub releases | 0 | Repository Releases page read 2026-07-14 |
| Live paid listing verified | 0 | Reserved Store product ID exists; no live product page or purchasable state was verified |
| Current downloadable build | 0 | Historical v1.0.0 workflow artifacts are expired and predate this cycle |
| Production dependency vulnerabilities | 0 | `npm audit --omit=dev --json`, saved as `revenue/npm-audit-production.json` |
| Runtime packages with generated notices | 54 | `npm run licenses`; project license is separately packaged |

### Historical remote evidence

- Stale Python **Tests #40** failed all nine jobs:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/27457790209>.
- **Deploy GitHub Pages #2** failed and Pages is not an eligible commercial host:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/27326075652>.
- Historical **Release Build #6** succeeded, but its artifacts expired and are
  not current release evidence:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/27326127499>.
- Historical **Store Publish #5** failed during metadata update. That mutation
  was removed; paid metadata is now manual:
  <https://github.com/ntoledo319/Mindful-Organizer/actions>.

### Local and hosted verification ledger

- Public review branch shipped:
  <https://github.com/ntoledo319/Mindful-Organizer/tree/feature/revenue-cycle-0>.
- Hosted Quality Gate #41: **passed** locked install, lint, both TypeScript
  projects, 11 tests, renderer build, and Electron bundle build:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29309084417>.
- Final local `npm run lint -- --no-cache`: **passed**.
- Final local `npm run typecheck`: **passed**.
- Final local `npm test`: **2 files / 11 tests passed** under Vitest 4.1.10.
- `npm run vite:build`: **passed**, 762 renderer modules plus main/preload.
- `npm run icons` and `npm run winstore-assets`: **passed** after Jimp 1.6
  migration.
- Full and production-only `npm audit`: **0 known vulnerabilities**.
- SQLite in-memory load under the local Node runtime: **passed** after restoring
  its Node-native binding.
- Local `npm run build:dir`: **failed** during the Electron 43 SQLite rebuild;
  Apple Clang 14 / SDK 13.3 cannot find C++20 `<source_location>`. This is a
  recorded packaging failure, not a passing build.
- No sale, signup, visit, or listing-impression number was observed.

### Hosted package evidence — 2026-07-14 01:44 EDT

- **Windows Store (MSIX) Build #9: passed** all steps:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29309185258>.
- Head commit: `6fb4d884933cab41cae65f6bbaf4e0fb624dfb9d`.
- Artifact: `hearth-msix`, ID `8301428016`, 179,750,864 bytes, expires
  2026-08-13.
- GitHub artifact digest:
  `sha256:aecc37c1f8bc18bb8e0f27fb4b7b7d23e6e6a688240c99870288ed4c55c81afe`.
- Fresh Quality Gate for the same commit also passed:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29309185278>.
- **Not observed:** installation success, launch behavior, Windows App
  Certification Kit result, Store certification, listing visibility, page views,
  purchases, refunds, or payout.

The artifact does not clear encryption, provenance, support, install-smoke,
certification, or paid-listing gates. Collected profit remains **$0.00** and the
gap remains **$4,000.00**.
