# Hearth — Release Readiness & Production Target

_Synthesis of the v1.1.0 release-hardening pass. Supersedes the scattered root-level
process docs (AUDIT_REPORT, RELEASE_PUNCH_LIST, SUBMISSION_CHECKLIST, PROJECT_TRACKER)._

## What Hearth actually is

A **macOS-first, local-first PyQt6 desktop application** that adapts the computing
environment to a user's psychological state for people managing ADHD, anxiety,
depression, OCD, PTSD, or bipolar disorder. Zero telemetry; all data in a local SQLite
database. The desktop _is_ the intervention surface — not another tracking app.

The tracking, therapeutic, and wellness features are genuinely cross-platform. The
**live OS-adaptation** layer (closing apps, Do Not Disturb, display dimming) is
**verified on macOS only**; Windows/Linux ship the full app minus live actuation.

## Production target for this pass

The strongest **responsibly shippable** version of the desktop app: data-safe on
upgrade, never paywalling crisis support, honest about what it actuates on each OS,
buildable into a tested macOS artifact, with an honest at-rest threat model and a
documented release path. Code-signing/notarization + store accounts are the external
release gate.

## Verified strengths (preserve — do not regress)

- Real offline Ed25519 license validation (only the **public** key ships).
- Solid SQLite layer: schema v4, WAL, parameterized CRUD, idempotent ALTER migrations,
  thread-safe under load, online-backup + integrity-checked restore.
- Responsible clinical posture: "supplement not a replacement" disclaimers everywhere;
  988 / Crisis Text Line / SAMHSA hard-coded as always-available defaults; heuristics
  framed as observations, never diagnoses.
- Coherent 15-tab navigation shell with per-widget graceful degradation; real 6-page
  onboarding wizard; reactive StateBus refresh; partial real accessibility (font scale,
  color-blind overrides).
- Genuinely strong tests for subscription/licensing, database CRUD (97%), themes (100%),
  and the system-automation engine. **GUI widget coverage: 29 tests** across dashboard,
  task manager, mood tracker, diary card, crisis, breathing, meditation, sleep, and file
  organizer widgets. Full suite: ~822 tests.
- Network surface is a single benign GitHub version check — the zero-telemetry claim holds.

## Decisive calls made this pass

1. **Platform scope** — macOS-first for live actuation. Windows/Linux backends return
   honest "not supported yet" instead of faking success; README/docs restated.
2. **FastAPI layer (`src/hearth_api`)** — **removed from the shipping product.** It was
   broken (all data routes 500), fully orphaned (no frontend exists; only its own theater
   test consumed it), and bloated runtime deps. Preserved in git history for a future,
   real Phase 2. fastapi/uvicorn/httpx dropped from runtime deps.
3. **PHI at rest** — filesystem hardening (0700 data dir / 0600 db) + the secure vault now
   genuinely encrypts file _contents_ (was metadata-only) + honest threat-model docs.
   Full-DB encryption (SQLCipher) is deferred as an explicit owner decision (cost/complexity).
4. **Version** — release as **1.1.0** (1.0.0 was an internal snapshot, never published).
5. **Git history bloat (~42MB binaries)** — left intact; history rewrite on a public repo
   is destructive and out of scope without explicit owner authorization. Documented.

## Blocker remediation index (22)

| #   | Blocker                                                                      | Status    |
| --- | ---------------------------------------------------------------------------- | --------- |
| 1   | Data: guid backfill migration (v4)                                           | **Fixed** |
| 2   | Clinical: un-paywall crisis                                                  | **Fixed** |
| 3   | Clinical: wire medication adherence to SQLite                                | **Fixed** |
| 4   | Clinical: functional 988 buttons                                             | **Fixed** |
| 5   | Clinical: risk-language detection                                            | **Fixed** |
| 6   | Clinical: magnitude-scaled thresholds                                        | **Fixed** |
| 7   | GUI: live dashboard quick-actions                                            | **Fixed** |
| 8   | GUI: fixed mood search                                                       | **Fixed** |
| 9   | GUI: MoodManager `conditions=` crash                                         | **Fixed** |
| 10  | OS: honest DND/brightness (real path or honest fallback, never fake success) | **Fixed** |
| 11  | OS: honest Win/Linux                                                         | **Fixed** |
| 12  | OS: AppleScript arg sanitization                                             | **Fixed** |
| 13  | Security: vault content encryption                                           | **Fixed** |
| 14  | Security: fs perms                                                           | **Fixed** |
| 15  | Build: macOS `.app` BUNDLE + `.icns`                                         | **Fixed** |
| 16  | Build: exe name = `hearth` (MSIX match)                                      | **Fixed** |
| 17  | Build: optional-dep-robust spec                                              | **Fixed** |
| 18  | Build: Windows build script (`build_windows.bat`) uses `pyproject.toml`      | **Fixed** |
| 19  | API: removed orphaned FastAPI layer                                          | **Fixed** |
| 20  | Tests: kill phantom-module + silent-skip theater                             | **Fixed** |
| 21  | Tests: add regression cover for every safety fix                             | **Fixed** |
| 22  | Tests: 29 GUI widget tests added                                             | **Fixed** |

**Additional items completed outside the original 22:**

- Store listing accuracy audit — false claims removed, feature descriptions updated.
- QFontDatabase crash fix for headless/CI environments.
- Smoke test harness (`scripts/smoke_test.py`) for headless validation.

## Known issues that surfaced this pass

- **QFontDatabase headless crash** — Fixed: `QFontDatabase` can return an empty family list in headless/CI environments, causing a `IndexError` on startup. Defensive checks added.
- **Auto-updater is enhanced but still check-only for installation** — Users receive changelog and download links, but must run the installer manually. Self-installation is deferred to a future release.
- **Medication widget keeps a JSON display model** — Adherence is mirrored into SQLite, but the widget still maintains a parallel JSON display model. Full unification is follow-up.
