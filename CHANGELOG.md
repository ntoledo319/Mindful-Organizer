# Changelog

All notable changes to Mindful Organizer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
- Initial release of Mindful Organizer
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
