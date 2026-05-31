# Technical Debt and Gaps

**Purpose:** Prioritized register of known technical debt, missing features, and risks.  
**Intended audience:** Maintainers, tech leads, auditors.  
**Confidence:** Confirmed from source code and test results. Inferences labeled.  
**Last updated:** 2026-05-31 (v1.1.0 release-hardening)

## v1.1.0 status (release-hardening pass)

Fixed this pass (see CHANGELOG and docs/RELEASE_READINESS.md): the task-duplication
migration bug, the three-way data-directory split, crisis paywalling, the dead journal
988-detection, crisis-signal severity ordering, dead dashboard/search actions, fake OS
"success" returns, the plaintext "secure" vault, broken data export, the orphaned FastAPI
layer, and pervasive test-theater (the suite is now hard-imported and honest: ~780 tests,
the only skips are the optional scikit-learn path).

**Remaining, honestly:**
- **Code signing / notarization** — not done (no Apple Developer ID / Windows cert). The
  single biggest blocker to frictionless public distribution. *External — owner-provided.*
- **Live OS adaptation is macOS-only.** Windows/Linux run the full app but their system
  backends are honest no-ops. macOS DND/brightness need a user Shortcut / the `brightness`
  CLI respectively, and report honestly when unavailable.
- **DB is plaintext SQLite** (filesystem-permission-hardened, 0700/0600). App-level DB
  encryption (SQLCipher) is an explicit owner decision, not implemented.
- **GUI widget coverage** remains low (logic is well-covered; rendered-widget tests are
  high-effort). The shipped app was launch-verified manually + via the built `.app`.
- The medication widget keeps a JSON display model and mirrors adherence into SQLite;
  unifying it fully on SQLite is follow-up.

## Executive Summary

The codebase is functional and well-tested in core areas, but still has significant gaps in GUI test coverage, database encryption at rest, and commercial packaging hardening.

## Critical

### C1: Secure content keyring fallback still reduces protection
- **Why it matters:** OS keyring storage is preferred, but fallback to an on-disk `key.bin` is still possible when keyring is unavailable.
- **Evidence:** `src/security/content_management.py` migrates keys into keyring but falls back to restricted-permission disk storage on keyring errors.
- **Impact:** Reduced encryption value on systems without a working keyring backend.
- **Recommended fix:** Make fallback opt-in, warn in-app, and document OS keyring requirements.
- **Effort:** M
- **Confidence:** Confirmed

### C2: License issuing process needs release hardening
- **Why it matters:** Runtime verification now uses an embedded Ed25519 public key, but private-key handling must be locked down for commercial distribution.
- **Evidence:** `src/core/subscription_manager.py` verifies Ed25519 signatures and `issue_license.py` depends on private signing material.
- **Impact:** Weak release controls could still compromise license issuance.
- **Recommended fix:** Store the private key only in the release secret manager, rotate test keys, and document issuance controls.
- **Effort:** S
- **Confidence:** Confirmed

### C3: TaskManager now uses SQLite
- **Status:** **Fixed** during this pass. `TaskManager` stores task records in `TableName.TASKS`; JSON remains only for templates/custom categories and legacy migration input.

## High

### H1: Zero automated GUI widget coverage
- **Why it matters:** All user-facing interactions are untested in CI.
- **Evidence:** No test files for `src/gui/widgets/*.py`. Coverage report shows 0%.
- **Impact:** Visual regressions and interaction bugs slip through; high manual QA burden.
- **Recommended fix:** Add `pytest-qt` tests for critical flows: task creation, diary card save/load, crisis plan display, dashboard refresh.
- **Effort:** M
- **Confidence:** Confirmed

### H2: Inconsistent widget constructor patterns
- **Why it matters:** Some widgets take a theme dict + explicit managers; others take the main window as parent. This makes refactoring and testing difficult.
- **Evidence:** `src/gui/main_window.py` lines 601-678: `DashboardWidget(theme, ...)` vs `ERPWidget(self)`.
- **Impact:** Maintenance friction, brittle widget tests, unclear data dependencies.
- **Recommended fix:** Standardize on explicit dependency injection (theme dict + manager references) for all widgets.
- **Effort:** M
- **Confidence:** Confirmed

### H3: `build.sh` was broken (now fixed, but Windows build script still rough)
- **Why it matters:** Build scripts that don't work waste time and create broken releases.
- **Evidence:** Original `build.sh` referenced nonexistent `mindful_organizer/` directory and copied venv into `.app` bundle. `build_windows.bat` installs from `requirements.txt` with outdated versions.
- **Impact:** Broken macOS builds, inconsistent Windows builds.
- **Recommended fix:** ✅ `build.sh` fixed. Next: update `build_windows.bat` to use `pyproject.toml` and add CI build verification.
- **Effort:** S
- **Confidence:** Confirmed

### H4: Windows Store assets generated
- **Status:** **Fixed** during this pass. `scripts/generate_store_assets.py` generated the required PNG/ICO assets in `windows_store/assets/`.

## Medium

### M1: `voice_journal.py` is a functional stub
- **Why it matters:** Users cannot actually record or transcribe voice journals.
- **Evidence:** `src/wellness/voice_journal.py` lines 111-115: writes silent WAV frames.
- **Impact:** User confusion, broken feature promise.
- **Recommended fix:** Implement with `sounddevice`/`PyAudio` or remove the feature and document as future work.
- **Effort:** M
- **Confidence:** Confirmed

### M2: No database encryption at rest
- **Why it matters:** Mental health data is sensitive. A stolen laptop yields plaintext SQLite.
- **Evidence:** `src/core/database.py` uses standard `sqlite3` with no encryption.
- **Impact:** Data exposure if device is physically compromised.
- **Recommended fix:** Evaluate SQLCipher or similar. Document that OS disk encryption (FileVault/BitLocker) is currently required.
- **Effort:** L
- **Confidence:** Confirmed

### M3: Log rotation added
- **Status:** **Fixed** during this pass. `src/main.py` uses `RotatingFileHandler` with 5 MB files and five backups.

### M4: Inconsistent import style
- **Why it matters:** `from core.X` vs `from src.core.X` causes IDE confusion and potential import errors.
- **Evidence:** `src/core/notification_engine.py` uses `from core.database`; tests use `from src.core.database`.
- **Impact:** Maintenance friction.
- **Recommended fix:** Standardize on absolute `src.` imports everywhere; update `sys.path` bootstrap if needed.
- **Effort:** S
- **Confidence:** Confirmed

### M5: `store_listing.md` advertises nonexistent features
- **Why it matters:** False advertising creates legal and reputational risk.
- **Evidence:** `windows_store/store_listing.md` mentions "Focus Sessions" / "Pomodoro-style focus timers" — no such feature exists in the codebase.
- **Impact:** User complaints, refund requests, store rejection.
- **Recommended fix:** Audit store listing against actual source code. Remove all unimplemented features.
- **Effort:** XS
- **Confidence:** Confirmed

## Low

### L1: `pytest.ini` and `pyproject.toml` config drift
- **Status:** **Fixed** during this audit. Config consolidated into `pyproject.toml`; `pytest.ini` removed.

### L2: `setup.py` and `pyproject.toml` version drift
- **Status:** **Fixed** during this audit. `setup.py` is now a legacy shim and delegates package metadata to `pyproject.toml`.

### L3: `requirements.txt` versions and deps differ from `pyproject.toml`
- **Status:** **Fixed** during this audit. Trimmed to core deps with alignment note.

### L4: Data directory name typo corrected
- **Why it matters:** `.mindful_optimizer` was a typo for `.mindful_organizer`.
- **Evidence:** `src/main.py` used `.mindful_optimizer`; `src/windows/platform_utils.py` previously used `.mindful_organizer`.
- **Impact:** Fixed data consistency.
- **Recommended fix:** **Fixed** — corrected to `.mindful_organizer` everywhere. Added migration logic in `src/main.py`.
- **Effort:** XS (already done)
- **Confidence:** Confirmed

### L5: Dead code in `backup/` directory
- **Why it matters:** Clutters repository, confuses new engineers.
- **Evidence:** `backup/` contains an entire older version of the codebase.
- **Impact:** Low — not imported by running code.
- **Recommended fix:** Delete `backup/` or move to a separate archive branch.
- **Effort:** XS
- **Confidence:** Confirmed

### L6: No automated accessibility audit in CI
- **Why it matters:** WCAG regressions go unnoticed.
- **Evidence:** No axe-core, Pa11y, or equivalent checks in `.github/workflows/`.
- **Impact:** Compliance and inclusion risk.
- **Recommended fix:** Add a lightweight manual checklist in PR template; consider Qt-specific a11y linting.
- **Effort:** S
- **Confidence:** Confirmed

## Partial Implementations

| Feature | Status | Evidence |
|---------|--------|----------|
| Voice journal | Stub — silent audio | `src/wellness/voice_journal.py` |
| PDF export | Stub — minimal implementation | `src/core/pdf_export.py` |
| Community insights | Stub | `src/core/community_insights.py` |
| Auto-updater | Checks releases, does not install | `src/core/auto_updater.py` |

## Best Next Three Fixes

1. **Add GUI widget tests for critical flows** (task creation, diary card, crisis plan, dashboard) — highest user-impact gap.
2. **Harden keyring fallback behavior** — avoid silently weakening secure content encryption.
3. **Finalize release/license operations** — document private key handling and packaging controls.
