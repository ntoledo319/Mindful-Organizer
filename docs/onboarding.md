# Engineer Onboarding

**Purpose:** Guide for new engineers joining the project.  
**Intended audience:** New contributors and maintainers.  
**Confidence:** Confirmed from repo structure and source.  
**Last updated:** 2026-05-02

## What to Read First

1. [`README.md`](../README.md) — Project overview and quick start
2. [`docs/overview.md`](overview.md) — What the product is and who uses it
3. [`docs/architecture.md`](architecture.md) — System design and data flow
4. [`docs/repo-map.md`](repo-map.md) — Where everything lives
5. **This file** — Practical getting-started steps

## What to Run First

```bash
# 1. Clone and setup
git clone <repo-url>
cd Mindful-Organizer
python3 -m venv venv312
source venv312/bin/activate
pip install -e ".[dev]"

# 2. Verify tests pass
pytest -m "not gui and not slow" -x

# 3. Run the app
python src/main.py

# 4. Run lint (should pass on clean code)
ruff check src/ tests/
```

## Key Architectural Concepts

1. **Offline-first desktop app** — No server, no cloud. Everything is local SQLite + JSON.
2. **Single-instance** — Only one copy of the app can run at a time.
3. **Lazy-loaded managers** — `AdaptiveMainWindow` creates managers on first access via properties. This keeps startup fast but hides dependency errors.
4. **StateBus** — PyQt6 signals decouple widgets from managers. Widgets should not call each other directly.
5. **Condition-aware UI** — Tabs and recommendations change based on the user's mental health profile.
6. **Dual persistence** — Tasks live in JSON; everything else lives in SQLite. This is historical debt.

## Essential Commands

| Command | Purpose |
|---------|---------|
| `python src/main.py` | Run the app |
| `pytest -m "not gui and not slow"` | Run fast tests |
| `pytest tests/unit/test_database.py -v` | Run specific test file |
| `pytest --cov=src --cov-report=term-missing` | Run with coverage |
| `ruff check src/ tests/` | Lint |
| `ruff format src/ tests/` | Format |
| `mypy src/` | Type check |
| `bash build.sh` | Build executable (macOS/Linux) |

## Critical Files and Directories

| Path | Why it matters |
|------|---------------|
| `src/main.py` | Boot sequence, logging, single-instance lock |
| `src/gui/main_window.py` | Central orchestrator — start here for UI changes |
| `src/core/database.py` | SQLite schema, migrations, all persistent data except tasks |
| `src/core/task_manager.py` | Task CRUD, templates, undo/redo — uses JSON, not SQLite |
| `src/core/wellness_orchestrator.py` | Cross-module intelligence, crisis detection |
| `src/core/subscription_manager.py` | Feature gating, license validation |
| `src/core/constants.py` | Canonical enums (Condition, TherapyType, etc.) |
| `tests/conftest.py` | Shared pytest fixtures |
| `pyproject.toml` | Canonical build config, dependencies, tool settings |

## Common Traps

1. **Import style** — Some core files use `from core.X` while tests use `from src.core.X`. Both work because `src/` is added to `sys.path` in `main.py`, but it can confuse IDEs. Prefer `from src.core.X` in tests.
2. **GUI tests need a display** — Skip them with `-m "not gui"`. On Linux, set `QT_QPA_PLATFORM=offscreen`.
3. **Manager properties return None** — If an optional dependency is missing, lazy-loaded properties return `None`. Widgets must handle this or crash.
4. **Data directory typo** — The app uses `~/.mindful_optimizer` (not `.mindful_organizer`). Don't fight it; it's preserved for backward compatibility.
5. **Changing schema** — Edit `_SCHEMA_SQL` in `database.py` and bump `CURRENT_SCHEMA_VERSION`. Add migration SQL to `_MIGRATIONS`.
6. **Subscription gating** — Check `subscription_manager.has_feature("feature_name")` before exposing Premium functionality.

## How to Make Safe Changes

1. **Write a test first** — The test suite is solid for core managers. Add a test in `tests/unit/`.
2. **Run the test** — `pytest tests/unit/test_<module>.py -v`
3. **Make the change** — Prefer small, focused commits.
4. **Run full test suite** — `pytest -m "not gui and not slow"`
5. **Run lint** — `ruff check src/ tests/`
6. **Run the app** — `python src/main.py` and manually verify the affected feature.

## Where to Ask Questions

- Check [`docs/DOCS_INDEX.md`](DOCS_INDEX.md) for topic-specific docs
- Check [`docs/tech-debt-and-gaps.md`](tech-debt-and-gaps.md) for known issues
- Review existing tests for usage examples
