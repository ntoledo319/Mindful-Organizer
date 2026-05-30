# Deployment and Operations Guide

**Purpose:** Deployment packaging, operational runbook, and troubleshooting.  
**Intended audience:** Operators, release engineers, founders.  
**Confidence:** Confirmed from build scripts and source; some operational guidance is inferred.  
**Last updated:** 2026-05-29

## Deployment Model

Hearth is a **desktop application**, not a service. "Deployment" means packaging and distributing the app to end users.

### Distribution Channels

| Channel | Status | Evidence |
|---------|--------|----------|
| GitHub Releases (binaries) | **Inferred primary** | `auto_updater.py` checks GitHub releases |
| Windows Store (MSIX) | **Partially configured** | `windows_store/` exists but assets are missing |
| PyPI (pip install) | **Configured** | `pyproject.toml` has `[project.scripts]` |
| macOS App Store | **Not configured** | No App Store signing or sandbox config |
| Homebrew / Linux repos | **Not configured** | No formula or spec files |

## Environments

There is **only one runtime environment** — the user's local machine. There are no staging, production, or QA environments in the traditional server sense.

### User Data Directories

| OS | Data Directory | Config | Logs |
|----|---------------|--------|------|
| macOS | `~/.mindful_organizer/` | `~/Library/Preferences/MindfulOrganizer/` | `~/Library/Logs/MindfulOrganizer/` |
| Linux | `~/.mindful_organizer/` | `~/.config/mindful_organizer/` | `~/.mindful_organizer/logs/` |
| Windows | `~/.mindful_organizer/` | `%APPDATA%/MindfulOrganizer/` | `%APPDATA%/MindfulOrganizer/logs/` |

**Note:** `platform_utils.py` uses `MindfulOrganizer` (no dot, no underscore) for macOS/Windows config paths. The data dir is `.mindful_organizer` everywhere.

## Build Artifacts

| Artifact | Tool | Output Path |
|----------|------|-------------|
| macOS/Linux executable | PyInstaller | `dist/Hearth/` |
| Windows executable | PyInstaller | `dist/Hearth.exe` |
| Python wheel | `python -m build` | `dist/*.whl` |
| Source distribution | `python -m build` | `dist/*.tar.gz` |
| MSIX package | `build_msix.ps1` | `*.msix` (manual) |

## Packaging

### PyInstaller (`mindful_organizer.spec`)

- **Mode:** One-directory (faster startup)
- **Windowed:** No console window
- **Hidden imports:** PyQt6, numpy, sklearn, cryptography
- **Data files:** `resources/`, `windows_store/assets/`
- **Exclusions:** test frameworks, pip, setuptools, tkinter
- **UPX:** Enabled (may cause issues with PyQt6 on some systems)

### Windows Store MSIX

- `windows_store/AppxManifest.xml` defines the package
- `build_msix.ps1` automates build, layout, PRI generation, packaging, and WACK validation
- **Assets:** Windows Store PNG/ICO assets are generated in `windows_store/assets/` by `scripts/generate_store_assets.py`.
- **Invalid:** `PhoneProductId` is a placeholder; background task extension references a nonexistent class.

## Secrets and Config Needs

- **No runtime secrets** required for core functionality.
- **License validation** uses an embedded Ed25519 public key in `src/core/subscription_manager.py`. The private signing key must stay in release secrets only.
- **Encryption keys** for secure folders are generated per-installation and stored in the OS keyring when available, with an on-disk fallback.

## Migration Concerns

- **Database schema migrations** run automatically on app start via `DatabaseManager.initialize()`.
- **JSON-to-SQLite migration** runs on first launch for remaining legacy JSON records and writes a completion marker.
- **No downgrade path** for schema migrations.

## Rollback

- **Database:** Use `DatabaseManager.restore(backup_path)` or replace `mindful_organizer.db` from a file backup.
- **Application:** Replace the executable/package with the previous version. Data is forward-compatible within major versions.

## Operational Gotchas

1. **Single-instance enforcement** — If the app crashes on Windows, the `.lock` file may persist. The startup code attempts to delete it, but this is a file-based lock, not a mutex.
2. **Log rotation** — Runtime logs rotate at 5 MB per file with five backups.
3. **No auto-update installation** — `AutoUpdater` checks for releases but does not download or install them. Users must manually update.
4. **WAL mode** — SQLite uses WAL. If the app crashes, `-wal` and `-shm` files may be left behind. SQLite handles this gracefully on next open.

## Startup Checks

1. Verify single-instance lock can be acquired
2. Verify data directory exists and is writable
3. Initialize SQLite schema (migrations run automatically)
4. Load profile (trigger onboarding if none)
5. Apply theme and accessibility settings
6. Start background timers (notifications, system stats)

## Routine Maintenance

- **Backups:** `DatabaseManager.backup()` creates timestamped copies in `~/.mindful_organizer/backups/`.
- **Cleanup:** `scripts/cleanup.py` removes build artifacts (rewritten to be safe and portable).
- **Log monitoring:** Check `~/.mindful_organizer/logs/mindful_organizer.log` for errors.

## Logs and Observability

- **Log location:** `~/.mindful_organizer/logs/mindful_organizer.log`
- **Format:** `%(asctime)s [%(levelname)s] %(name)s: %(message)s`
- **Levels:** INFO and above to file; INFO and above to stdout
- **No structured logging** — plain text only
- **No metrics pipeline** — no Prometheus, StatsD, etc.
- **No correlation IDs** — single-user app, not needed

## Incident Triage

| Symptom | Likely Cause | Where to Inspect |
|---------|-------------|------------------|
| App won't start | Missing PyQt6, or single-instance lock stuck | Logs, `~/.mindful_organizer/.lock` |
| Data missing | Wrong data directory, or DB corruption | `~/.mindful_organizer/`, backup files |
| Crashes on theme change | Stylesheet syntax error | `src/gui/themes.py`, log traceback |
| Tasks not persisting | SQLite write failure or migration issue | `mindful_organizer.db`, logs |
| Slow startup | Many SQLite rows or large JSON sidecars | File sizes, `PRAGMA wal_checkpoint` |

## Restart Guidance

1. Close the app gracefully (File → Quit or window close)
2. If frozen, kill the process. The POSIX file lock is released by the kernel; Windows lock file may need manual deletion.
3. Restart. Schema migrations and settings load automatically.

## Operational Dependencies

| Dependency | What happens if missing |
|------------|------------------------|
| PyQt6 | App cannot start |
| SQLite (stdlib) | App cannot start |
| numpy | `WellnessOrchestrator` crashes on snapshot |
| cryptography | Secure folders unavailable |
| psutil | System stats show "unavailable" |
| scikit-learn | Energy predictor falls back to heuristics |
