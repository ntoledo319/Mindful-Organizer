# Technical Debt and Gaps

**Purpose:** Prioritized register of known technical debt, missing features, and risks.  
**Intended audience:** Maintainers, tech leads, auditors.  
**Confidence:** Confirmed from source code and test results. Inferences labeled.  
**Last updated:** 2026-06-08 (v1.1.0 release-hardening)

## v1.1.0 status (release-hardening pass)

Fixed this pass (see CHANGELOG and docs/RELEASE_READINESS.md): the task-duplication
migration bug, the three-way data-directory split, crisis paywalling, the dead journal
988-detection, crisis-signal severity ordering, dead dashboard/search actions, fake OS
"success" returns, the plaintext "secure" vault, broken data export, the orphaned FastAPI
layer, pervasive test-theater (phantom-module + silent-skip files now hard-imported),
zero GUI coverage (29 widget tests added), voice journal stub (now records actual audio
with graceful degradation), store listing false claims (audited and corrected), build
script drift (`build.sh` and `build_windows.bat` both fixed), and QFontDatabase headless
crash. Full suite: ~822 tests.

**Remaining, honestly:**

- **Code signing / notarization** — not done (no Apple Developer ID / Windows cert). The
  single biggest blocker to frictionless public distribution. _External — owner-provided._
- **Live OS adaptation is macOS-only.** Windows/Linux run the full app but their system
  backends are honest no-ops. macOS DND/brightness need a user Shortcut / the `brightness`
  CLI respectively, and report honestly when unavailable.
- **DB is plaintext SQLite** (filesystem-permission-hardened, 0700/0600). App-level DB
  encryption (SQLCipher) is an explicit owner decision, not implemented.
- **Medication widget keeps a JSON display model** and mirrors adherence into SQLite;
  unifying it fully on SQLite is follow-up.

## Executive Summary

The codebase is functional and well-tested in core areas. GUI widget coverage has improved
from 0% to 29 tests, but rendered-widget tests remain high-effort and do not cover all
interaction flows. Database encryption at rest and commercial packaging hardening remain
the largest outstanding risks.

## Critical

### C1: Secure content keyring fallback still reduces protection

- **Why it matters:** OS keyring storage is preferred, but fallback to an on-disk `key.bin` is still possible when keyring is unavailable.
- **Evidence:** `src/security/content_management.py` migrates keys into keyring but falls back to restricted-permission disk storage on keyring errors. Fallback is now opt-in (`force_keyring`) and warns prominently, but still possible.
- **Impact:** Reduced encryption value on systems without a working keyring backend.
- **Recommended fix:** Surface `keyring_fallback_used` in the Settings UI so users are aware; document keyring requirements per OS.
- **Effort:** S
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

- **Status:** **Fixed** during this pass. 29 `pytest-qt` tests added across dashboard, task manager, mood tracker, diary card, crisis, breathing, meditation, sleep, and file organizer widgets. Coverage is no longer zero, but interaction-heavy paths (drag-and-drop, complex state transitions) are still under-tested.
- **Why it matters (residual):** All user-facing interactions are high-risk for visual regressions.
- **Evidence:** `tests/unit/gui/` now contains 10 test files with 29 test methods.
- **Recommended fix (remaining):** Add interaction tests for task creation flow, diary card save/load, and crisis-widget 988-button wiring.
- **Effort:** M
- **Confidence:** Confirmed

### H2: Inconsistent widget constructor patterns

- **Why it matters:** Some widgets take a theme dict + explicit managers; others take the main window as parent. This makes refactoring and testing difficult.
- **Evidence:** `src/gui/main_window.py` lines 601-678: `DashboardWidget(theme, ...)` vs `ERPWidget(self)`.
- **Impact:** Maintenance friction, brittle widget tests, unclear data dependencies.
- **Recommended fix:** Standardize on explicit dependency injection (theme dict + manager references) for all widgets.
- **Effort:** M
- **Confidence:** Confirmed

### H3: `build.sh` was broken (now fixed, Windows build script also fixed)

- **Status:** **Fixed** during this pass. `build.sh` now builds correctly from `pyproject.toml`. `build_windows.bat` was rewritten to use `pyproject.toml` instead of stale `requirements.txt` and includes proper venv isolation, PyInstaller invocation, and MSIX packaging guidance.
- **Recommended fix (remaining):** Add CI build verification on Windows runner to prevent future drift.
- **Effort:** S
- **Confidence:** Confirmed

### H4: Windows Store assets generated

- **Status:** **Fixed** during this pass. `scripts/generate_store_assets.py` generated the required PNG/ICO assets in `windows_store/assets/`.

## Medium

### M1: `voice_journal.py` is a functional stub

- **Status:** **Fixed** during this pass. `src/wellness/voice_journal.py` now records actual audio via `sounddevice`/`PyAudio` when available, with graceful degradation to text-only when no microphone is present.
- **Recommended fix (remaining):** Add transcription integration when a speech-to-text backend is available.
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

- **Status:** **Fixed** during this pass. `windows_store/store_listing.md` was audited against actual source code. False claims removed; feature descriptions updated to reflect shipped capabilities (Focus Sessions, Voice Journal, etc.).

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

| Feature            | Status                                                            | Evidence                                                |
| ------------------ | ----------------------------------------------------------------- | ------------------------------------------------------- |
| Voice journal      | **Implemented** with graceful degradation                         | `src/wellness/voice_journal.py` records actual audio    |
| PDF export         | **Implemented**                                                   | `src/core/pdf_export.py` generates clinician-ready PDFs |
| Community insights | Stub                                                              | `src/core/community_insights.py`                        |
| Auto-updater       | Enhanced check-only: changelog + download links + signature hooks | `src/core/auto_updater.py`                              |

## Best Next Three Fixes

1. **Add GUI interaction tests for critical flows** (task creation end-to-end, diary card save/load, crisis-widget 988 wiring) — highest remaining user-impact gap.
2. **Harden keyring fallback UX** — surface `keyring_fallback_used` in Settings so users know their encryption strength is reduced.
3. **Finalize release/license operations** — document private key handling and packaging controls; add CI build verification on Windows.
