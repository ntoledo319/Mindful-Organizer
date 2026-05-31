# Hearth v1.1.0 — Release Report

Branch: `release/v1.1.0-prep` (20 commits, local — not yet pushed). Working tree clean.
Suite: **776 passed, 4 skipped** (only the optional scikit-learn tests skip); ruff clean;
all 106 src modules import cleanly. Artifact: `dist/Hearth.app` (389 MB), launch-verified.

## What the product is
A macOS-first, local-first **PyQt6 desktop application** ("Hearth") that adapts the
computing environment to a user's psychological state (ADHD/anxiety/depression/OCD/
PTSD/bipolar). Tracking, therapeutic tools, the adaptive dashboard, and crisis resources
run on macOS/Linux/Windows; **live OS actuation** (closing apps, DND, dimming) is
implemented and verified on **macOS only**. Zero telemetry; all data in local SQLite.

## Production target pursued
The strongest **responsibly shippable** desktop app: data-safe on upgrade, crisis support
never paywalled, honest about what it actuates on each OS, buildable into a tested macOS
`.app`, with a documented release path. Code signing/notarization + store accounts are the
external gate.

## Major improvements (all verified)
- **Data integrity:** v4 migration backfills task guids (fixed silent task-doubling on
  upgrade — proved non-vacuously); one canonical data dir (`core/paths.py`) + one shared
  `DatabaseManager` (fixed a three-way data split-brain).
- **Clinical safety:** crisis signals **un-paywalled**; functional 988/Crisis Text Line
  buttons; severity now scales with magnitude and signals are ordered so the urgent 988
  message always surfaces first; journal entries scanned for ideation → surface 988;
  medication adherence reaches SQLite so the miss-streak heuristic fires.
- **Honesty:** OS adaptation no longer fakes success (DND/brightness return real results;
  Windows/Linux report inert honestly); dashboard quick-actions / mood search / analytics
  revived; Focus-mode messages reflect what actually happened.
- **Security/privacy:** data dir 0700 / DB 0600; the secure vault now genuinely encrypts
  file contents; constant-time passcode compare; the shareable health report inlines
  Chart.js (no CDN fetch); update check uses a bundled certifi CA so it works when frozen.
- **Quality:** removed the orphaned/broken FastAPI layer; ended test-theater (phantom-module
  + ~26 silent-skip files now hard-imported); fixed a real gamification XP bug; repo hygiene
  (untracked backup/, removed stale docs); brand/version/docs accuracy.

## Capabilities added / repaired (not inflation)
Functional 988 dialing, journal risk surfacing, real data export of SQLite health data,
genuine at-rest vault encryption, offline self-contained reports, a real macOS `.app`
bundle + `.icns`, and an operator runbook.

## Production infra created/repaired
macOS `BUNDLE` (was missing → empty artifact); spec path bug fixed; optional-ML-robust
spec; MSIX script/manifest names + versions aligned to `Hearth`/1.1.0; release.yml attaches
the macOS `.app`; certifi bundled; `docs/RUNBOOK.md` + `docs/RELEASE_READINESS.md`.

## Verification performed
- Two adversarial workflow rounds (10-agent investigation, 6-agent review) + a 3-agent
  fix-verification, each **reproducing** issues. Final verification: clinical PASS, honesty
  PASS, integrity PASS.
- Built `dist/Hearth.app` and launched it from a clean isolated HOME → migrations to v4,
  "Application window displayed", no crash, no SSL error.
- Rendered real app screens (dashboard/mood/crisis) and inspected them.

## Build & artifact test results
`pyinstaller mindful_organizer.spec` → `dist/Hearth.app` (Info.plist 1.1.0, id
`io.hearthproject.hearth`, vendored chart.js bundled). Boot test: PASS.

## Distribution target
- **macOS:** `Hearth.app` (built, tested; unsigned).
- **Windows:** `dist/Hearth/hearth.exe` → MSIX via `build_msix.ps1` (CI-only; not built here).
- Release pipeline: tag `v*` → `.github/workflows/release.yml` builds both + GitHub Release.

## Current release state
**Ready for one explicit publish approval.** All code is committed locally; nothing is
pushed, tagged, or released. The remaining steps are owner-gated (below).

## Remaining limitations
Code signing/notarization not done (external); live OS adaptation macOS-only; DB is
plaintext SQLite (fs-hardened; SQLCipher is an owner decision); GUI widget coverage low;
medication widget keeps a JSON display model mirrored to SQLite.

## Exact next actions (owner-gated)
1. **Review & merge** the branch:
   `git push -u origin release/v1.1.0-prep` then open a PR to `main` (or merge).
   *Effect:* publishes the branch to the public repo; tests.yml runs on the PR. Reversible.
2. **Cut the release** (publishes a public GitHub Release with artifacts):
   `git tag v1.1.0 && git push origin v1.1.0`
   *Effect:* triggers `release.yml` → builds Windows MSIX + macOS `.app`, creates a public
   Release. Outward-facing; effectively irreversible once announced. **Requires approval.**
3. **Signing/stores (blocked on credentials):** Apple Developer ID cert (notarize the `.app`)
   and a Windows signing cert + Microsoft Partner Center account (sign + submit the MSIX).
