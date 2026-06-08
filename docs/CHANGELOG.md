# Changelog

All notable changes to Hearth are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.1.0] — 2026-06-08

### Added

- **Focus Sessions widget** — Pomodoro-style deep-work timer with a circular progress UI, customizable duration presets, session history, and automatic Do-Not-Disturb activation.
- **Voice journaling module** — Record journal entries directly in the app with actual audio capture (gracefully degrades to text-only when no microphone is available).
- **Personal Insights engine** — Local analytics generated from the user's own historical data (mood, sleep, tasks). No generic templates; every observation is data-driven.
- **PDF export** — One-click export of wellness reports, diary cards, and mood timelines for sharing with clinicians or archiving.
- **Enhanced auto-updater** — In-app changelog viewer, direct download links, and Ed25519 signature-verification hooks for update integrity.
- **GUI widget tests** — 29 `pytest-qt` tests across critical widgets (dashboard, task manager, mood tracker, diary card, crisis, breathing, meditation, sleep, file organizer). Previously 0% GUI coverage.
- **Smoke test harness** (`scripts/smoke_test.py`) — Headless import validation, dependency check, resource verification, accessibility audit, widget instantiation, and circular-import probe.
- **QFontDatabase crash fix** — Prevents startup crashes in headless/CI environments where `QFontDatabase` returns no families.

### Changed

- **Pricing updated** to reflect the expanded feature set and OS-level integration:
  | Tier | Old Price | New Price |
  | ------- | -------------------------- | ---------------------------- |
  | Pro | $4.99/month or $39.99/year | $8.00/month or $79.99/year |
  | Premium | $9.99/month or $79.99/year | $15.00/month or $149.99/year |
- **Auto-updater behavior** — No longer check-only; presents changelog and download links. Self-installation remains deferred to the user.
- **Build system** — `build.sh` repaired (was referencing nonexistent paths and copying venv into `.app`); `build_windows.bat` rewritten to install from `pyproject.toml` instead of stale `requirements.txt`.
- **Store listing accuracy** — Audited `windows_store/store_listing.md` against actual source code; removed false claims and updated feature descriptions.

### Fixed

- **GUI test reliability** — Eliminated phantom-module imports and silent-skip theater; the full suite is now hard-imported and honest. ~822 tests total (was ~780).
- **Platform honesty** — Windows and Linux live OS-adaptation backends no longer fake success; they return honest "not supported yet" status.
- **Data directory consolidation** — Resolved three-way split-brain between `.mindful_optimizer`, `.mindful_organizer`, and `core/paths.py`; canonical path is now `~/.mindful_organizer` (with migration on first launch).
- **Task duplication on upgrade** — v4 migration backfills task GUIDs non-vacuously, preventing silent task-doubling.
- **Crisis widget severity ordering** — Urgent 988 message always surfaces first; severity scales with signal magnitude.
- **Medication adherence** — Wired into SQLite so the miss-streak heuristic actually fires.
- **Gamification XP bug** — Fixed a real XP-calculation regression.
- **Theme count accuracy** — Documentation now correctly reflects 4 shipped themes (Onyx, Alabaster, Slate, Quiet).

### Security

- **Keyring enforcement** — Vault encryption keys prefer OS keyring (Keychain / Credential Manager / SecretService). Fallback to on-disk `key.bin` is now opt-in (`force_keyring` flag) and logs a prominent warning. `keyring_fallback_used` is exposed for UI surfacing.
- **License validation hardening** — Ed25519 signature verification with embedded public key only. Private-key issuance script (`scripts/issue_license.py`) enforces 0600 permissions, git-repo leak warnings, and env-var preference.
- **HTTPS-only update channels** — Both GitHub API and all `browser_download_url` values are validated with `_ensure_https()`; non-HTTPS URLs abort the operation.
- **Data directory permissions** — `0700` for data dir, `0600` for DB, vault fallback, and update downloads.
- **Shareable reports** — Chart.js is vendored inline; reports make zero network requests.

### Deprecated

- None.

### Removed

- **Orphaned FastAPI layer** (`src/hearth_api`) — Broken (all data routes 500), fully orphaned (no frontend), bloated runtime deps. Preserved in git history for a future Phase 2. `fastapi` / `uvicorn` / `httpx` dropped from runtime dependencies.
