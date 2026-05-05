# Testing Guide

**Purpose:** Testing strategy, conventions, and current coverage posture.  
**Intended audience:** Engineers, QA.  
**Also see:** [`docs/development.md`](development.md) for local setup and commands.  
**Confidence:** Confirmed from test files and CI workflow. Test counts are approximate.  
**Last updated:** 2026-05-02

## Test Framework

- **pytest** with `pytest-cov` for coverage
- **pytest-qt** for GUI widget tests (optional; skipped in CI)
- **conftest.py** provides shared fixtures: `tmp_data_dir`, `sample_profile`, `sample_tasks`, `sample_mood_entries`

## Test Locations

| Type | Location | Notes |
|------|----------|-------|
| Unit | `tests/unit/` | Isolated, fast, no GUI required |
| Integration | `tests/integration/` | Cross-module workflows |

## Commands

```bash
# Fast suite (excludes GUI and slow tests)
pytest -m "not gui and not slow"

# With coverage
pytest -m "not gui and not slow" --cov=src --cov-report=term-missing

# Single file
pytest tests/unit/test_task_manager.py -v

# Integration only
pytest tests/integration/ -v

# GUI tests (local only, requires display)
pytest -m gui
```

## Conventions

- Filename: `test_<module_name>.py`
- Class name: `Test<FeatureArea>`
- Method name: `test_<behaviour>_<condition>`
- Use `pytest.mark.skipif` for optional-dependency modules
- Use `pytest.mark.gui` for tests requiring a display
- Use `pytest.mark.slow` for long-running tests

## What Is Covered Well

- Database CRUD, backup, restore, export (`test_database.py`)
- Task lifecycle: add, complete, undo, redo, recurrence, templates (`test_task_manager.py`)
- Mood analytics and insights (`test_mood_analytics.py`)
- Energy prediction (`test_energy_predictor.py`)
- NLP task parsing (`test_nlp_parser.py`)
- Subscription manager: tier validation, license keys, trials (`test_subscription_manager.py`)
- Content manager: encryption, passcode verification, path traversal (`test_content_management.py`)
- Wellness orchestrator: crisis signals (`test_wellness_orchestrator.py`)
- Breathing, coping, ERP, journaling, sleep, medication trackers

## What Is Not Covered

- **GUI widgets** — 0% automated coverage in CI. All `src/gui/widgets/*.py` lack tests.
- **Theme stylesheet generation** — No automated rendering tests.
- **Voice journal** — Module is a stub; no real audio I/O to test.
- **Calendar sync** — Stub implementation.
- **Shareable report Chart.js rendering** — HTML structure is not validated in tests.
- **Database migration v1→v2** — No test verifies migration correctness with real data.

## Mocking Strategy

- **Database:** Use `tmp_data_dir` fixture with a real SQLite DB in `/tmp`. Fast and realistic.
- **ML models:** Skip tests when `scikit-learn` or `sentence-transformers` are absent (`pytest.mark.skipif`).
- **Subscription manager:** Use `tmp_data_dir` to create isolated license state per test.

## Critical Flows That Must Remain Covered

1. Task add → complete → undo → redo → persistence round-trip.
2. Database insert with constraint violations (must raise `IntegrityError`).
3. Export JSON → import JSON → data integrity verification.
4. Crisis signal detection for low mood + sleep deprivation.
5. Content manager encryption round-trip and passcode verification.
6. Subscription license key generation → activation → feature gating.

## Known Gaps and Recommended Next Tests

| Gap | Risk | Recommended Test |
|-----|------|------------------|
| GUI widgets untested | Visual regressions, interaction bugs | Add `pytest-qt` widget tests for critical paths (task creation, crisis widget, diary card). |
| Shareable report rendering | Browser compatibility | Test that generated HTML contains all expected sections and valid JSON for Chart.js. |
| Multi-threaded DB access | Race conditions | Stress-test concurrent reads/writes via `threading`. |
| Diary card migration | Schema upgrade failure | Test v1→v2 migration creates `diary_cards` table and preserves existing data. |
