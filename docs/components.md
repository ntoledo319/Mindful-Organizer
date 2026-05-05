# Components and Modules

**Purpose:** Breakdown of major subsystems with responsibilities, entry points, and risks.  
**Intended audience:** Engineers, maintainers.  
**Confidence:** Confirmed from source.  
**Last updated:** 2026-05-02

## Core Subsystems

### 1. Application Bootstrap (`src/main.py`)

**Purpose:** Entry point. Configures logging, platform paths, single-instance lock, DPI, and launches the GUI.

**Entry points:**
- `main()` — primary entry
- `mindful-organizer` console script (from `pyproject.toml`)

**Key files:**
- `src/main.py`

**Responsibilities:**
- Determine data directory (`~/.mindful_optimizer` on all platforms)
- Configure rotating file + stdout logging
- Enforce single-instance via file lock (POSIX) or `O_CREAT|O_EXCL` (Windows)
- Configure high-DPI scaling before `QApplication` creation
- Show fatal error dialogs if dependencies are missing

**Risks:**
- Windows single-instance uses `O_CREAT|O_EXCL` on a file, not a mutex. Race conditions possible.
- macOS single-instance uses `fcntl` flock on a file in the data directory. If the app crashes, the lock file may persist but the lock itself is released by the kernel.
- The `check_single_instance` function on Windows deletes an existing lock file before creating a new one, which could allow a second instance to sneak through.

---

### 2. Database Manager (`src/core/database.py`)

**Purpose:** Thread-safe SQLite persistence with schema versioning and migrations.

**Entry points:**
- `DatabaseManager(db_path=None)`
- `DatabaseManager.initialize()`
- `DatabaseManager.insert/update/delete/query/execute/count`
- `DatabaseManager.transaction()` (context manager)

**Key files:**
- `src/core/database.py`

**Responsibilities:**
- Create and maintain SQLite schema (v2)
- Run migrations from `_MIGRATIONS` dict
- Provide parameterized CRUD helpers
- Export data to JSON/CSV
- Backup and restore database files

**Dependencies:**
- `sqlite3` (stdlib)
- `threading` (stdlib)

**Interactions:**
- Used by almost all core managers except `TaskManager`
- `MigrationManager` uses it to migrate legacy JSON data

**Risks:**
- `query()` accepts a raw `where` string. The docstring warns against interpolation, but there is no runtime guard.
- Schema migrations are manual and confined to one file. No down-migrations.

---

### 3. Task Manager (`src/core/task_manager.py`)

**Purpose:** Task CRUD, scheduling, templates, undo/redo, and statistics.

**Entry points:**
- `TaskManager(data_dir)`
- `add_task()`, `delete_task()`, `update_task()`, `complete_task()`
- `get_tasks_by_*()` query family
- `undo_manager` property for undo/redo

**Key files:**
- `src/core/task_manager.py`

**Responsibilities:**
- Maintain in-memory task list loaded from `tasks.json`
- Support subtasks, recurrence, dependencies, tags, custom categories
- Provide sorting and search
- Track task completion statistics

**Dependencies:**
- `json`, `uuid`, `dataclasses`
- `gui.state_bus` (for emitting signals) — **inverted dependency**

**Interactions:**
- `AdaptiveMainWindow` owns the instance
- `TaskManagerWidget` displays tasks
- `EnergyPredictor` may read tasks for forecasting

**Risks:**
- Uses JSON instead of SQLite, unlike all other managers
- No file locking on `tasks.json`; concurrent writes could corrupt data
- `get_task_by_id()` is O(n) over the task list
- Emits signals by importing `gui.state_bus` from core layer

---

### 4. Wellness Orchestrator (`src/core/wellness_orchestrator.py`)

**Purpose:** Cross-module intelligence. Aggregates mood, sleep, energy, medication, and task data to produce insights and crisis signals.

**Entry points:**
- `WellnessOrchestrator(db=None)`
- `snapshot(dt=None)` — point-in-time wellness view
- `detect_crisis_signals(conditions)` — heuristic-based alerts
- `daily_briefing(conditions, max_tasks)` — morning recommendations
- `wellness_summary(days)` — unified export

**Key files:**
- `src/core/wellness_orchestrator.py`

**Responsibilities:**
- Read latest data from SQLite tables
- Apply condition-specific heuristics
- Generate text recommendations
- Produce structured dataclasses for GUI consumption

**Dependencies:**
- `numpy` — used for mean, polyfit
- `core.database.DatabaseManager`
- `core.constants.Condition`

**Risks:**
- Crisis detection is heuristic-based, not clinical. The docstrings correctly label this as "observations rather than definitive claims."
- `numpy.polyfit` is used on small mood series (≥7 points). With very small samples this can be numerically unstable.
- Bipolar-specific heuristics depend on the string `"bipolar"` appearing in condition names (case-insensitive). This is fragile.

---

### 5. Subscription Manager (`src/core/subscription_manager.py`)

**Purpose:** Offline tier management and license key validation.

**Entry points:**
- `SubscriptionManager(data_dir)`
- `current_tier` property
- `has_feature(feature)`, `require_feature(feature)`
- `activate_license(key)`, `generate_key(tier, days)`
- `start_trial()`, `trial_days_remaining`

**Key files:**
- `src/core/subscription_manager.py`

**Responsibilities:**
- Parse and validate HMAC-signed license keys
- Track trial state in `license.json`
- Gate features by tier

**Risks:**
- Hardcoded HMAC secret (`_SECRET`). Must be replaced with per-build or asymmetric secrets before commercial distribution.
- License keys are trivially forgeable if the secret is known.
- No online revocation or usage tracking.

---

### 6. GUI Main Window (`src/gui/main_window.py`)

**Purpose:** Central orchestrator. Owns all manager references and wires widgets.

**Entry points:**
- `AdaptiveMainWindow()`
- Lazy-loaded manager properties (`sleep_tracker`, `mood_manager`, etc.)
- `_initialize_ui()`, `_add_tabs()`

**Key files:**
- `src/gui/main_window.py`

**Responsibilities:**
- Instantiate or lazy-load all managers
- Create tabbed UI with condition-aware tab selection
- Apply themes and keyboard shortcuts
- Run background timers for notifications and system stats
- Handle window close (save settings, widget states)

**Risks:**
- God object — knows about ~20 managers
- `_create_widget()` uses string-based dispatch with broad `except Exception` catchers
- Some widgets receive `self` (the main window) as parent instead of theme dict, creating inconsistent constructor signatures

---

### 7. Security / Content Management (`src/security/content_management.py`)

**Purpose:** Encrypt sensitive user files in passcode-protected folders.

**Entry points:**
- `ContentManager(root_path)`
- `create_secure_folder(...)`, `verify_access(folder_id, passcode)`
- `move_to_secure_folder(...)`, `get_folder_path(...)`

**Key files:**
- `src/security/content_management.py`

**Responsibilities:**
- Generate Fernet keys
- Hash passcodes with scrypt
- Encrypt folder metadata
- Reject path traversal in folder names

**Risks:**
- **Encryption key stored alongside encrypted data** (`key.bin` in `.content_config` inside the data directory). If the data directory is copied, the attacker gets both ciphertext and key.
- No OS keychain integration (Keychain, DPAPI, Secret Service).
- `SecurityLevel.MAXIMUM` claims "multi-factor authentication" but the implementation is single-factor (passcode only).

---

### 8. Platform Utilities (`src/windows/platform_utils.py`)

**Purpose:** OS detection, paths, DPI, notifications, startup registration, single-instance enforcement.

**Entry points:**
- `detect_os()`, `get_data_dir()`, `get_config_dir()`, `get_log_dir()`
- `get_system_theme()`, `get_scale_factor()`
- `send_desktop_notification(...)`
- `register_startup(...)`, `is_registered_for_startup()`
- `SingleInstance` class

**Key files:**
- `src/windows/platform_utils.py`

**Responsibilities:**
- Abstract platform differences
- Detect light/dark mode from OS settings
- Send native desktop notifications
- Register/unregister app for system startup

**Risks:**
- macOS startup registration writes a plist but does not load/unload it with `launchctl`.
- Windows notifications depend on `win10toast` or `winotify`, neither of which are in `pyproject.toml` dependencies.
- `SingleInstance` on Windows uses a mutex but `main.py` does not use this class; it uses its own file-based lock.
