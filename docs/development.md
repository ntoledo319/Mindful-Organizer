# Development Guide

**Purpose:** How to set up, build, test, and contribute to Hearth.
**Intended audience:** Engineers.
**Confidence:** Confirmed by running commands where possible.
**Last updated:** 2026-05-02

## Prerequisites

- Python 3.11, 3.12, or 3.13
- pip
- Git
- (Optional) PyInstaller for building executables
- (Optional) Qt platform plugins for headless testing (`QT_QPA_PLATFORM=offscreen`)

## Install Steps

```bash
git clone https://github.com/ntoledo319/Mindful-Organizer.git
cd Mindful-Organizer
python3 -m venv venv312
source venv312/bin/activate
pip install -e ".[dev]"
```

With ML features:
```bash
pip install -e ".[dev,ml,nlp]"
```

## Environment Setup

No `.env` file is required. The app creates its data directory automatically:
- macOS: `~/.mindful_optimizer/`
- Linux: `~/.mindful_optimizer/`
- Windows: `%APPDATA%/.mindful_optimizer/` or `~/.mindful_optimizer/`

**Note:** The directory name `.mindful_optimizer` is a legacy typo but is used consistently across the codebase to avoid breaking existing user data.

## Database Setup

The SQLite database is created automatically on first launch:
```bash
python -c "from src.core.database import DatabaseManager; db = DatabaseManager(); db.initialize(); print(db.db_path)"
```

Schema migrations run automatically via `DatabaseManager.initialize()`.

## Run Commands

```bash
# Run the application
python src/main.py

# Run in headless mode (for testing)
QT_QPA_PLATFORM=offscreen python src/main.py
```

## Verification Steps

After install, verify the environment:

```bash
# Check imports
python -c "from src.core.database import DatabaseManager; print('OK')"
python -c "from src.core.task_manager import TaskManager; print('OK')"
python -c "from src.gui.main_window import AdaptiveMainWindow; print('OK')"

# Run a quick smoke test
pytest tests/unit/test_database.py -v
pytest tests/unit/test_task_manager.py -v
```

## Common Pitfalls

1. **Import errors in tests** — `src/` is added to `sys.path` in `src/main.py`. If running tests outside pytest, you may need `PYTHONPATH=src`.
2. **GUI tests fail without display** — Tests marked `@pytest.mark.gui` require a display. Skip them with `pytest -m "not gui"`.
3. **PyQt6 platform plugin missing on Linux** — Install system deps: `sudo apt-get install -y libgl1-mesa-glx libegl1 libxkbcommon0`.
4. **Data directory inconsistency** — `src/windows/platform_utils.py` previously used `.mindful_organizer` while the rest of the app used `.mindful_optimizer`. This has been fixed to use `.mindful_optimizer` everywhere.

## Build Steps

### PyInstaller Executable

```bash
# macOS / Linux
bash build.sh

# Windows
build_windows.bat
```

Outputs:
- `dist/Hearth/` (one-dir mode, per `mindful_organizer.spec`)
- `dist/Hearth.exe` (Windows)

### Wheel / sdist

```bash
pip install build
python -m build
```

Outputs in `dist/`:
- `mindful_organizer-1.0.0-py3-none-any.whl`
- `mindful_organizer-1.0.0.tar.gz`

## Release Flow

There is **no automated release pipeline** in CI. Release steps are manual:

1. Update version in `pyproject.toml` and `setup.py`
2. Update `CHANGELOG.md`
3. Run `bash build.sh` (or `build_windows.bat`)
4. Tag the release: `git tag v1.0.0`
5. Push tag: `git push origin v1.0.0`
6. Create GitHub Release and attach build artifacts

## Versioning

The project uses **semantic versioning** (inferred from `pyproject.toml` and tags).
- Current version: `1.0.0`
- Previous version: `1.0.0` (in `mindful_organizer.spec` and legacy docs)

## CI/CD

GitHub Actions workflow: `.github/workflows/tests.yml`

**Triggers:**
- Push to `main`, `develop`, `feature/**`, `claude/**`
- Pull requests to `main`, `develop`

**Jobs:**
1. **test** — Runs on Ubuntu/Windows/macOS × Python 3.9–3.12
   - Installs system deps (Linux)
   - `pip install -e ".[dev]"`
   - `flake8` linting (legacy; project uses ruff locally)
   - `pytest -m "not gui and not slow" --cov=src`
   - Uploads coverage to Codecov (Ubuntu + Python 3.11 only)
2. **integration** — Runs on Ubuntu + Python 3.11 after test job passes
   - `pytest tests/integration/`

**CI gaps:**
- ruff is not run in CI
- mypy is not run in CI
- No build artifact generation in CI
- No automated release creation
