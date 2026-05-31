# Hearth — Operator Runbook

A concise operational reference for building, releasing, supporting, and recovering
Hearth. Hearth is a **single-user, local-first desktop app**; there is no server to
operate, so "operations" here means the release pipeline and the user's local data.

## 1. Where data lives

One canonical, platform-appropriate directory (resolved by `src/core/paths.py`):

| Platform | Data directory |
|----------|----------------|
| macOS    | `~/Library/Application Support/.mindful_organizer` |
| Linux    | `~/.mindful_organizer` |
| Windows  | `%APPDATA%\.mindful_organizer` |

Contents: `mindful_organizer.db` (SQLite, schema v4, WAL), `logs/`, `license.json`,
`current_profile.json`, `update_state.json`, JSON config/templates, and the
`.secure_vault` / `.content_config` for the encrypted vault. On POSIX the directory
is `0700` and the database `0600`. **All health data stays here — no cloud, no telemetry.**

## 2. First run

- On launch the app migrates a legacy `~/…/.mindful_optimizer` directory to
  `.mindful_organizer` if present, runs SQLite migrations up to schema v4 (idempotent),
  and imports any legacy JSON wellness files once (a `.migration_complete` marker
  prevents re-runs).
- No profile → the onboarding wizard runs. A `current_profile.json` skips it next time.
- A single-instance lock (`.lock`) prevents two copies running at once.

## 3. Build

```bash
python3 -m venv venv312 && source venv312/bin/activate
pip install -e ".[dev]"          # add ",ml,nlp" for the optional ML/clustering extras
pip install pyinstaller
QT_QPA_PLATFORM=offscreen pytest -q     # gate the build on a green suite
pyinstaller mindful_organizer.spec --clean --noconfirm
```

Artifacts: **macOS** → `dist/Hearth.app`; **Windows** → `dist/Hearth/hearth.exe`
(packaged into MSIX by `windows_store/build_msix.ps1`). The spec collects the optional
ML stack only if it is installed, so a lean build still succeeds.

## 4. Release

1. Update `CHANGELOG.md` and bump the version in `src/app_metadata.py`,
   `pyproject.toml`, and the spec's `BUNDLE` (keep all three in sync).
2. Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`.
3. `.github/workflows/release.yml` builds the Windows MSIX and macOS `.app` on the tag
   and attaches them to a GitHub Release.
4. **Signing is required before public distribution and is the external gate** — see §7.

## 5. Backup / restore / rollback

- **Backup** — `DatabaseManager.backup(dest)` uses SQLite's online backup API for a
  consistent snapshot while the app runs. Recommend users copy the whole data
  directory (§1) periodically; it is self-contained.
- **Restore** — `DatabaseManager.restore(src)` integrity-checks the snapshot before
  swapping it in. To restore manually: quit Hearth, replace `mindful_organizer.db`
  (and remove stale `-wal`/`-shm` sidecars), relaunch.
- **Rollback (app version)** — migrations only add columns/rows and never drop data, so
  a newer DB generally opens on an older build, but this is not guaranteed across major
  schema jumps. Safe rollback = reinstall the previous build **and** restore a backup
  taken on that version. Always back up the data directory before upgrading.

## 6. Support / triage

- **Logs**: `<data dir>/logs/mindful_organizer.log` (rotating, 5 MB × 5). The first
  place to look for any crash or failed action.
- **Crash handling**: unhandled exceptions are logged and shown in a native error dialog.
  By design there is **no remote crash reporting** — that would violate the zero-telemetry
  promise. Ask users to send the log file if they consent.
- **"It says it couldn't change Do Not Disturb / brightness"**: expected on macOS 12+
  without a user Shortcut, and on Windows/Linux (live OS actuation is macOS-only for now).
  The app reports this honestly instead of pretending; tracking/therapeutic features are
  unaffected.
- **Update check fails silently**: the in-app updater is check-only and tolerant of
  network/SSL failures; it never blocks startup.

## 7. Known limitations / external gate

- **Code signing & notarization are NOT done** (no Apple Developer ID / Windows
  signing certificate available). Unsigned builds trigger Gatekeeper/SmartScreen
  warnings and cannot be published to the App Store / Microsoft Store. This is the
  single biggest blocker to public distribution and requires owner-provided credentials.
- **Live OS adaptation is macOS-only**; Windows/Linux backends are honest no-ops.
- **Database is plaintext SQLite** protected by filesystem permissions + the user's
  OS account + full-disk encryption. App-level DB encryption (SQLCipher) is a roadmap
  decision, not implemented.
- **Auto-updater is check-only** (notifies; does not self-install).
