# Repository Map

**Purpose:** Directory-level guide to the codebase.  
**Intended audience:** New engineers, auditors.  
**Confidence:** Confirmed from filesystem and source.  
**Last updated:** 2026-05-02

## Top-Level Structure

```
├── .github/              # CI/CD workflows, issue/PR templates
├── .claude/              # Claude-specific skills and configs (agent tooling)
├── backup/               # Legacy code from an earlier refactor — largely dead
├── docs/                 # Documentation suite (this directory)
├── resources/            # Static assets: meditation metadata, icons
├── scripts/              # Utility scripts (cleanup, fetch meditations)
├── src/                  # Application source code
├── tests/                # Test suite: unit + integration
├── windows_store/        # Microsoft Store packaging (MSIX)
├── build.sh              # macOS/Linux PyInstaller build script
├── build_windows.bat     # Windows PyInstaller build script
├── mindful_organizer.spec # PyInstaller spec
├── pyproject.toml        # Canonical build config and dependencies
├── setup.py              # Legacy setuptools wrapper (kept for compatibility)
└── requirements.txt      # Legacy requirements file (core deps only)
```

## `src/` — Source Code

### `src/main.py`

Application bootstrap. Configures logging, enforces single-instance lock, sets up high-DPI scaling, creates `QApplication`, and launches `AdaptiveMainWindow`.

### `src/core/` — Business Logic & Data Access

| File                       | Lines      | Status            | Notes                                                                |
| -------------------------- | ---------- | ----------------- | -------------------------------------------------------------------- |
| `database.py`              | ~716       | **Core / stable** | Thread-safe SQLite manager with migrations (schema v3)               |
| `task_manager.py`          | ~871       | **Core / stable** | Task CRUD, templates, undo/redo, statistics. Task records use SQLite |
| `wellness_orchestrator.py` | ~421       | **Core / stable** | Cross-module intelligence, crisis detection, daily briefings         |
| `subscription_manager.py`  | ~446       | **Core / stable** | Tier management, offline Ed25519 license validation                  |
| `diary_card_manager.py`    | ~200       | **Confirmed**     | DBT diary card CRUD                                                  |
| `mood_manager.py`          | ~150       | **Confirmed**     | Mood entry bridge to database                                        |
| `energy_predictor.py`      | ~300       | **Confirmed**     | Energy forecasting with optional ML                                  |
| `notification_engine.py`   | ~250       | **Confirmed**     | Context-aware notification generation                                |
| `notification_manager.py`  | ~400       | **Confirmed**     | Notification scheduling and delivery                                 |
| `file_organizer.py`        | ~350       | **Confirmed**     | File organization strategies                                         |
| `smart_file_system/`       | ~600 total | **Partial**       | ML-based file clustering; optional heavy deps                        |
| `nlp_parser.py`            | ~200       | **Confirmed**     | Natural language task parsing                                        |
| `export_manager.py`        | ~300       | **Confirmed**     | Data export (JSON/CSV) and report generation                         |
| `shareable_report.py`      | ~250       | **Confirmed**     | Self-contained HTML report with Chart.js                             |
| `pdf_export.py`            | ~150       | **Confirmed**     | PDF export of wellness reports and diary cards                       |
| `calendar_sync.py`         | ~100       | **Confirmed**     | ICS export and busy-block parsing                                    |
| `auto_updater.py`          | ~200       | **Confirmed**     | GitHub release check; does not auto-install                          |
| `migration_manager.py`     | ~281       | **Confirmed**     | JSON-to-SQLite data migration tool                                   |
| `system_optimizer.py`      | ~150       | **Confirmed**     | System stats (CPU, memory, disk)                                     |
| `ai_optimizer.py`          | ~200       | **Partial**       | scikit-learn task ranking; degrades gracefully                       |
| `values_tracker.py`        | ~150       | **Confirmed**     | ACT values alignment tracking                                        |
| `weekly_insights.py`       | ~180       | **Confirmed**     | Weekly summary generation                                            |
| `community_insights.py`    | ~100       | **Stub**          | Aggregated insights stub                                             |
| `onboarding_analytics.py`  | ~150       | **Confirmed**     | Onboarding funnel tracking                                           |
| `medication_tracker.py`    | ~250       | **Confirmed**     | Medication schedule and adherence                                    |
| `sleep_tracker.py`         | ~200       | **Confirmed**     | Sleep log management                                                 |
| `mood_analytics.py`        | ~300       | **Confirmed**     | Mood trend analysis and insights                                     |
| `smart_task_decomposer.py` | ~200       | **Confirmed**     | Breaks tasks into subtasks by condition                              |

### `src/gui/` — Presentation Layer

| File/Dir         | Status      | Notes                                                                      |
| ---------------- | ----------- | -------------------------------------------------------------------------- |
| `main_window.py` | **Core**    | `AdaptiveMainWindow` — central orchestrator, lazy-loads all managers       |
| `themes.py`      | **Core**    | Dynamic stylesheet generation, accessibility modes                         |
| `state_bus.py`   | **Core**    | Reactive pub/sub for cross-widget communication                            |
| `components/`    | **Core**    | Reusable styled widgets (buttons, cards, containers, progress, typography) |
| `widgets/`       | **Mixed**   | Feature screens. Some are substantial; some are thin wrappers              |
| `dialogs/`       | **Minimal** | Only `__init__.py` exists                                                  |

### `src/profiles/` — Mental Health Profile System

| File                               | Status        |
| ---------------------------------- | ------------- |
| `mental_health_profile_builder.py` | **Confirmed** |
| `clinical_combinations.py`         | **Confirmed** |
| `spoon_theory.py`                  | **Confirmed** |

### `src/wellness/` — Therapeutic Modules

| File                  | Status        | Notes                                                    |
| --------------------- | ------------- | -------------------------------------------------------- |
| `breathing.py`        | **Confirmed** | Breathing exercise manager                               |
| `grounding.py`        | **Confirmed** | Grounding technique manager                              |
| `meditation.py`       | **Confirmed** | Meditation session tracker                               |
| `journaling.py`       | **Confirmed** | Journal entry manager                                    |
| `journal_analyzer.py` | **Partial**   | Sentiment/distortion analysis stub                       |
| `crisis_plan.py`      | **Confirmed** | Crisis plan manager                                      |
| `erp_tracker.py`      | **Confirmed** | ERP exposure tracker                                     |
| `coping_engine.py`    | **Confirmed** | Coping recommendation engine                             |
| `voice_journal.py`    | **Stub**      | Silent WAV placeholder; see `docs/tech-debt-and-gaps.md` |

### `src/security/` — Encryption & Access Control

| File                    | Status                                         |
| ----------------------- | ---------------------------------------------- |
| `content_management.py` | **Confirmed** — Fernet + scrypt secure folders |

### `src/utils/` — Shared Helpers

| File                    | Status        |
| ----------------------- | ------------- |
| `accessibility.py`      | **Confirmed** |
| `keyboard_shortcuts.py` | **Confirmed** |
| `statistics.py`         | **Confirmed** |

### `src/windows/` — Platform-Specific Utilities

| File                | Status        | Notes                                                                    |
| ------------------- | ------------- | ------------------------------------------------------------------------ |
| `platform_utils.py` | **Confirmed** | OS detection, data directories, DPI, notifications, startup registration |

## `tests/` — Test Suite

| Directory            | Count     | Coverage Quality                                                 |
| -------------------- | --------- | ---------------------------------------------------------------- |
| `tests/unit/`        | ~30 files | Good for core managers; 29 GUI widget tests in `tests/unit/gui/` |
| `tests/integration/` | 2 files   | Cross-module workflows; `test_app_integration.py` is substantial |

## `backup/` — Legacy Code

**Status: Dead code.**  
This directory contains an earlier version of the codebase (pre-refactor). It is **not imported** by the running application. Safe to delete unless you need historical reference. Contains duplicates of `core/`, `gui/`, `profile/`, `security/`, and `utils/` modules.

## Generated / Build Artifacts

| Path             | Generated by                                 | Safe to delete?            |
| ---------------- | -------------------------------------------- | -------------------------- |
| `dist/`          | `build.sh`, `build_windows.bat`, PyInstaller | Yes                        |
| `*.egg-info/`    | setuptools                                   | Yes                        |
| `__pycache__/`   | Python bytecode                              | Yes                        |
| `.pytest_cache/` | pytest                                       | Yes                        |
| `.mypy_cache/`   | mypy                                         | Yes                        |
| `.ruff_cache/`   | ruff                                         | Yes                        |
| `file_index.db`  | Smart file system indexer                    | Yes (recreated at runtime) |
