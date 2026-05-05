# Technical Debt and Gaps

**Purpose:** Prioritized register of known technical debt, missing features, and risks.  
**Intended audience:** Maintainers, tech leads, auditors.  
**Confidence:** Confirmed from source code and test results. Inferences labeled.  
**Last updated:** 2026-05-02

## Executive Summary

The codebase is functional and well-tested in core areas, but has significant gaps in GUI test coverage, dual persistence (JSON + SQLite), and security hardening for commercial distribution.

## Critical

### C1: Encryption key stored alongside encrypted data
- **Why it matters:** If the data directory is copied, the attacker gets both ciphertext and key, nullifying the encryption.
- **Evidence:** `src/security/content_management.py` line 46: `key_file = self.config_path / "key.bin"`
- **Impact:** Reduced encryption value for any threat model involving data exfiltration.
- **Recommended fix:** Integrate OS keychain (Keychain on macOS, DPAPI on Windows, Secret Service on Linux).
- **Effort:** M
- **Confidence:** Confirmed

### C2: Hardcoded HMAC license secret
- **Why it matters:** License keys are trivially forgeable if the secret is known.
- **Evidence:** `src/core/subscription_manager.py` line 204: `_SECRET = b"mindful-organizer-offline-license-v1"`
- **Impact:** Anyone can generate valid Pro/Premium license keys.
- **Recommended fix:** Replace with per-build secret injected at packaging time, or switch to Ed25519 asymmetric signatures.
- **Effort:** S
- **Confidence:** Confirmed

### C3: TaskManager uses JSON instead of SQLite
- **Why it matters:** Dual persistence complicates backups, migrations, and consistency. JSON has no concurrency protection.
- **Evidence:** `src/core/task_manager.py` lines 383-408: reads/writes `tasks.json` directly.
- **Impact:** Data corruption risk if two instances somehow run; inconsistent backup strategy.
- **Recommended fix:** Migrate `TaskManager` to `DatabaseManager` (TableName.TASKS). `MigrationManager` already has the transform logic.
- **Effort:** M
- **Confidence:** Confirmed

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

### H4: Windows Store assets missing
- **Why it matters:** Store submission requires specific PNG assets.
- **Evidence:** `windows_store/assets/` contains only `README.md`, no images.
- **Impact:** Cannot publish to Microsoft Store.
- **Recommended fix:** Generate or source 44×44, 150×150, 620×300 PNGs and place in `assets/`.
- **Effort:** XS
- **Confidence:** Confirmed

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

### M3: No log rotation
- **Why it matters:** Log file grows indefinitely.
- **Evidence:** `src/main.py` lines 27-34: `FileHandler` with no `RotatingFileHandler`.
- **Impact:** Disk space exhaustion on long-running systems.
- **Recommended fix:** Replace with `logging.handlers.RotatingFileHandler` (max 5MB × 3 backups).
- **Effort:** XS
- **Confidence:** Confirmed

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
- **Status:** **Fixed** during this audit. `setup.py` version aligned to `1.1.0`.

### L3: `requirements.txt` versions and deps differ from `pyproject.toml`
- **Status:** **Fixed** during this audit. Trimmed to core deps with alignment note.

### L4: Data directory name inconsistency
- **Why it matters:** `.mindful_optimizer` is a typo for `.mindful_organizer`.
- **Evidence:** `src/main.py` uses `.mindful_optimizer`; `src/windows/platform_utils.py` previously used `.mindful_organizer`.
- **Impact:** Potential for data fragmentation if different code paths use different directories.
- **Recommended fix:** **Fixed** — standardized on `.mindful_optimizer` everywhere to preserve existing user data. Documented as known quirk.
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
| Calendar sync | Stub — ICS integration skeleton | `src/core/calendar_sync.py` |
| PDF export | Stub — minimal implementation | `src/core/pdf_export.py` |
| Community insights | Stub | `src/core/community_insights.py` |
| Wearable sync | Listed as Premium feature, no code | `src/core/subscription_manager.py` FEATURES_BY_TIER |
| Auto-updater | Checks releases, does not install | `src/core/auto_updater.py` |

## Best Next Three Fixes

1. **Add GUI widget tests for critical flows** (task creation, diary card, crisis plan, dashboard) — highest user-impact gap.
2. **Migrate TaskManager from JSON to SQLite** — eliminates dual persistence, simplifies backups, reduces corruption risk.
3. **Replace hardcoded HMAC secret with per-build secret** — required before any commercial distribution.
