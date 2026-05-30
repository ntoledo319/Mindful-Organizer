# API Reference

**Purpose:** Document all detected public API surfaces.  
**Intended audience:** Engineers, integrators.  
**Confidence:** Confirmed from source code. Gaps are labeled.  
**Last updated:** 2026-05-29

## Public API Surfaces

Hearth is a desktop application with **no external network API**. The APIs documented here are **internal public interfaces** — the contracts between GUI widgets and domain managers.

---

### 1. Database Manager (`src/core/database.py`)

**Class:** `DatabaseManager`

| Method | Signature | Purpose |
|--------|-----------|---------|
| `__init__` | `(db_path: Path \| None = None)` | Open or create DB at path |
| `initialize` | `() -> None` | Create schema and run migrations |
| `transaction` | `() -> Generator[sqlite3.Connection, None, None]` | Context manager for transactions |
| `insert` | `(table: TableName, **data) -> int` | Insert row, return row id |
| `update` | `(table: TableName, row_id: int, **data) -> int` | Update row by id |
| `delete` | `(table: TableName, row_id: int) -> int` | Delete row by id |
| `get_by_id` | `(table: TableName, row_id: int) -> dict \| None` | Fetch single row |
| `query` | `(table, columns="*", where="", params=(), order_by="", limit=None, offset=0) -> QueryResult` | Flexible query |
| `execute` | `(sql: str, params=()) -> QueryResult` | Execute arbitrary SQL |
| `count` | `(table, where="", params=()) -> int` | Row count |
| `get_setting` | `(key: str, default=None) -> str \| None` | Read app setting |
| `set_setting` | `(key: str, value: str, category="general") -> None` | Write app setting |
| `backup` | `(backup_path=None) -> Path` | Create DB backup |
| `restore` | `(backup_path: Path) -> None` | Restore from backup |
| `export_all_to_json` | `() -> str` | Export all tables to JSON |
| `export_table_to_csv` | `(table: TableName) -> str` | Export one table to CSV |

**Security note:** `query()` and `execute()` accept parameterized `where` clauses. Never interpolate user input into `where`.

---

### 2. Task Manager (`src/core/task_manager.py`)

**Class:** `TaskManager`

| Method | Signature | Purpose |
|--------|-----------|---------|
| `__init__` | `(data_dir: Path)` | Load task records from SQLite |
| `add_task` | `(task: Task) -> Task` | Add with undo support |
| `delete_task` | `(task_id: str) -> Task \| None` | Delete with undo support |
| `update_task` | `(task_id: str, **kwargs) -> Task \| None` | Update fields with undo |
| `complete_task` | `(task_or_id) -> Task \| None` | Mark complete; handles recurrence |
| `complete_subtask` | `(task_id: str, subtask_index: int) -> SubTask \| None` | Complete subtask |
| `get_task_by_id` | `(task_id: str) -> Task \| None` | Lookup by UUID |
| `get_tasks` | `(completed=False) -> list[Task]` | Filter by completion |
| `get_tasks_by_priority` | `(priority) -> list[Task]` | Filter by priority |
| `get_tasks_by_energy` | `(max_energy: int) -> list[Task]` | Filter by energy cap |
| `get_tasks_by_tag` | `(tag: str) -> list[Task]` | Filter by tag |
| `get_blocked_tasks` | `() -> list[Task]` | Tasks with unfinished deps |
| `get_overdue_tasks` | `() -> list[Task]` | Past due date |
| `search` | `(query: str) -> list[Task]` | Title/notes/tags search |
| `batch_complete` | `(task_ids: list[str]) -> list[Task]` | Bulk complete |
| `batch_delete` | `(task_ids: list[str]) -> list[Task]` | Bulk delete |
| `save_as_template` | `(task_id, template_name) -> TaskTemplate \| None` | Save as template |
| `create_from_template` | `(template_name, **overrides) -> Task \| None` | Instantiate template |
| `get_statistics` | `() -> dict` | Comprehensive stats dict |

---

### 3. Wellness Orchestrator (`src/core/wellness_orchestrator.py`)

**Class:** `WellnessOrchestrator`

| Method | Signature | Purpose |
|--------|-----------|---------|
| `__init__` | `(db=None)` | Initialize with DB connection |
| `snapshot` | `(dt=None) -> WellnessSnapshot` | Latest wellness state |
| `detect_crisis_signals` | `(conditions=None) -> list[CrisisSignal]` | Heuristic alerts |
| `daily_briefing` | `(conditions=None, max_tasks=5) -> DailyBriefing` | Morning recommendations |
| `wellness_summary` | `(days=30) -> dict` | Unified export for reports |

**Dataclasses:**
- `WellnessSnapshot` — mood, energy, sleep, meds, tasks
- `CrisisSignal` — severity, source modules, description, recommendation
- `DailyBriefing` — date, energy forecast, task recs, insights, crisis signals, suggested skill

---

### 4. Subscription Manager (`src/core/subscription_manager.py`)

**Class:** `SubscriptionManager`

| Method | Signature | Purpose |
|--------|-----------|---------|
| `__init__` | `(data_dir=None)` | Load license state |
| `current_tier` | property -> `SubscriptionTier` | Effective tier |
| `license_info` | property -> `LicenseInfo` | Human-readable summary |
| `has_feature` | `(feature: str) -> bool` | Feature check |
| `require_feature` | `(feature: str) -> bool` | Raises `FeatureGateError` if missing |
| `activate_license` | `(license_key: str) -> LicenseInfo` | Validate and store key |
| `deactivate` | `() -> None` | Clear license |
| `generate_key` | `(tier, days=365) -> str` | Admin key generation |
| `start_trial` | `() -> LicenseInfo` | Begin 14-day trial |
| `trial_days_remaining` | property -> `int` | Days left |

---

### 5. Content Manager (`src/security/content_management.py`)

**Class:** `ContentManager`

| Method | Signature | Purpose |
|--------|-----------|---------|
| `__init__` | `(root_path: Path)` | Init vault |
| `create_secure_folder` | `(name, category, security_level, passcode, hide_folder=False) -> Path` | Create encrypted folder |
| `verify_access` | `(folder_id: str, passcode: str) -> bool` | Check passcode |
| `move_to_secure_folder` | `(file_path, folder_id, passcode) -> bool` | Move file into vault |
| `get_folder_path` | `(folder_id, passcode) -> Path \| None` | Resolve path if authorized |
| `change_passcode` | `(folder_id, old_passcode, new_passcode) -> bool` | Rotate passcode |

---

### 6. State Bus (`src/gui/state_bus.py`)

**Class:** `StateBus`

Reactive pub/sub using PyQt6 signals. Confirmed signals:

| Signal | Emitted by | Consumed by |
|--------|-----------|-------------|
| `task_changed` | `TaskManager` | `DashboardWidget` |
| `mood_changed` | `MoodManager` | `DashboardWidget` |
| `diary_card_saved` | `DiaryCardManager` | `DashboardWidget` |
| `theme_changed` | `AdaptiveMainWindow` | All widgets |
| `profile_changed` | `ProfileManager` | All widgets |

**Note:** Full signal inventory is not extractable without reading every emitter. The above is confirmed from grep results.

---

## API Gaps

The following surfaces exist in code but lack stable public contracts:
- `SmartFileSystem` APIs — internal to the file clustering subsystem
- `ExportManager` import/export APIs — functional but not documented here
- `NotificationManager` scheduling APIs — functional but complex
- GUI widget constructors — inconsistent signatures; some take theme dict, some take parent window
