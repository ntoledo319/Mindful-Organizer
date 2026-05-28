# Changelog

All notable changes to Hearth will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-05-23

First public release. Code-complete for Windows Store submission once the
external blockers in `RELEASE_PUNCH_LIST.md` (code-signing cert, Partner
Center publisher identity, trademark) are resolved.

### Added
- **Ed25519 license signing** — Replaced symmetric HMAC with asymmetric
  Ed25519 keys. The shipped binary contains only the verification (public)
  key, so license keys can no longer be forged by reading the source. The
  private signing key is held by the issuer; `scripts/issue_license.py`
  generates keys when given `MINDFUL_LICENSE_PRIVATE_KEY`.
- **OS-keyring storage for the content-vault Fernet key** — Encryption keys
  now live in macOS Keychain / Windows Credential Manager / freedesktop
  SecretService instead of next to the ciphertext. Legacy `key.bin` is
  auto-migrated on first launch and then deleted.
- **Log rotation** — `mindful_organizer.log` now rotates at 5 MB across 5
  files (30 MB cap) instead of growing unbounded.
- **First-launch JSON→SQLite migration** — Auto-runs once on startup when
  legacy wellness JSON files exist; marker file prevents re-running.
- **Windows Store assets** — Generated 66 PNG icon variants + multi-resolution
  `app_icon.ico` from a programmatic brain-leaf logo. Run
  `python scripts/generate_store_assets.py` to regenerate.
- **AppxManifest cleanup** — Replaced placeholder `PhoneProductId` GUID
  with a real one. Documented the Publisher CN swap required at submission.

### Security
- Eliminated the hardcoded HMAC secret in `subscription_manager.py` that
  was previously the largest commercial-distribution blocker.
- Removed on-disk storage of encryption keys by default.

## [Unreleased]

### Added
- **System Automation Layer** — Desktop-native "psychological operating system" that actively reconfigures the computing environment based on psychological state. 8 modules, 78 tests, all passing.
  - `SystemAutomationEngine` — Central conductor evaluating wellness state every 10 min
  - `AutomationRules` — 14 evidence-informed trigger→action rules (energy peaks, anxiety spikes, ADHD slump, burnout, hypomania, sleep debt, crisis)
  - `PlatformActions` — Cross-platform backend (macOS AppleScript/shell, Linux/Windows stub)
  - `FocusModeManager` — Deep-work sessions with distraction app closure and analytics
  - `DisplayAdaptationEngine` — Brightness/night shift/theme based on circadian rhythm, energy, mood, and condition-specific presets
  - `AppGuardian` — Blacklisted app monitoring and closure
  - `SystemTrayController` — Always-on tray with quick mood/energy/focus/crisis buttons
  - `GlobalHotkeyManager` — Global shortcuts (Ctrl+Shift+F/C/G)
- **AutomationConfigManager** — Pro-tier configuration: execution modes (suggestions/ask-first/autonomous), custom rule builder, multiple automation profiles (work/personal/sleep), scheduled focus blocks
- **AutomationAnalytics** — Effectiveness tracking: rule firing frequency, focus session stats, app guardian activity, display adaptation events, correlation between automation and productivity
- **AutomationWidget** — Tier-aware GUI tab: Overview (execution mode, quick actions), Rules (enable/disable, custom builder for Premium), Focus (sessions, scheduled blocks), Analytics (weekly trends, rule effectiveness)
- **Tier-Gated Automation** — FREE gets suggestions/notifications only (ethical boundary: core mental health tools stay free). PRO gets autonomous execution of default rules + display adaptation + focus mode. PREMIUM gets custom rules, multiple profiles, scheduled blocks, and analytics.
- **DBT Diary Card** — Daily structured tracking with emotions, urges (0-5), skills used, effectiveness ratings, target behaviors, medication adherence, and substance use. Condition-aware content adapts to ADHD, Anxiety, Depression, OCD, and PTSD.
- **Shareable HTML Reports** — Self-contained single-file reports with embedded Chart.js charts. Open in any browser, upload to cloud storage, or paste into Notion. Replaces PDF export as the primary sharing format.
- **MoodManager** — Bridges MoodTrackerWidget to SQLite `mood_entries` table. Fixes the previously disconnected data path.
- **Condition-Aware File Organizer Widget** — Full-featured organizer with ADHD (emoji/action-based), OCD (numbered/predictable), Depression (energy-tiered), Anxiety (detailed hierarchy), and Generic modes.
- **Database Schema v2** — Added `diary_cards` table with migration from v1.

### Changed
- **Sleep Logging Simplified** — Reduced to 3 taps: bedtime, wake time, and quality (Poor/Okay/Good). Removed interruptions, notes, and sleep aids fields.
- **Mood Tracker** — Removed manual energy slider. Energy is now derived automatically from sleep, mood, and task history via the existing EnergyPredictor.
- **File Organizer** — Replaced fallback placeholder with a full widget supporting organize, dry-run preview, undo, duplicate detection, batch rename, and structure creation.
- **Subscription Tiers** — Added `diary_card` (Free) and `shareable_reports` (Premium). Removed `energy_logging` from all tiers.
- **Keyboard Shortcuts** — Removed `energy_checkin` shortcut (Ctrl+E) since manual energy logging is discontinued.
- **Notifications** — Removed `schedule_energy_check()` method and energy check-in notifications.

### Removed
- **Manual Energy Logging** — Energy is now 100% derived from other data. No manual input required.
- **PDF Reports** — Replaced by Shareable HTML Reports. PDF export code remains as fallback but is no longer the primary sharing method.

### Fixed
- **Mood data persistence** — `main_window.py` now passes `mood_manager` and `diary_card_manager` to widgets instead of `None`.

## [1.0.0] - 2024-01-XX

### Added
- Initial release of Hearth
- Mental health profile system supporting ADHD, Anxiety, Depression, OCD, PTSD
- Energy-based task management and prioritization
- Adaptive UI based on mental health profiles
- Multiple calming themes (Light, Dark, Calm, High Contrast)
- Guided meditation library from UCLA MARC, Oxford Mindfulness, NHS
- Smart file organization system
- Mood and sleep tracking
- Break suggestions based on energy levels
- Local data storage with encryption
- Cross-platform support (macOS, Linux, Windows)

### Security
- All data stored locally with encryption
- No telemetry or data collection
- Secure deletion of sensitive data

## Pre-Release History

### [0.9.0] - 2023-12-XX
- Beta release for testing
- Core functionality implemented
- Initial UI designs

### [0.5.0] - 2023-11-XX
- Alpha release
- Basic task management
- Mental health profile builder

### [0.1.0] - 2023-10-XX
- Project inception
- Initial prototypes
- Concept validation

---

## Version Guidelines

### Version Numbers
- **Major (X.0.0)**: Breaking changes, major feature additions
- **Minor (0.X.0)**: New features, backwards compatible
- **Patch (0.0.X)**: Bug fixes, minor improvements

### Release Schedule
- **Major releases**: Annually
- **Minor releases**: Quarterly
- **Patch releases**: As needed for bugs

[Unreleased]: https://github.com/ntoledo319/Mindful-Organizer/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/ntoledo319/Mindful-Organizer/releases/tag/v1.0.0
[0.9.0]: https://github.com/ntoledo319/Mindful-Organizer/releases/tag/v0.9.0
