# Environment Variables and Configuration

**Purpose:** Inventory of runtime configuration, env vars, and tool config.  
**Intended audience:** Operators, developers, release engineers.  
**Confidence:** Confirmed from source and config files.  
**Last updated:** 2026-05-02

## Environment Variables

Hearth has **no required environment variables**. The following are optional or used only in testing/CI.

| Variable | Purpose | Required? | Where Used | Sensitivity |
|----------|---------|-----------|------------|-------------|
| `QT_QPA_PLATFORM` | Qt platform plugin selection (e.g. `offscreen` for headless tests) | Optional | CI workflow (`tests.yml`), local headless testing | None |
| `APPDATA` | Windows data directory root | Optional | `src/main.py`, `src/windows/platform_utils.py` | None |
| `XDG_CONFIG_HOME` | Linux config directory override | Optional | `src/windows/platform_utils.py` | None |
| `GDK_SCALE` | Linux HiDPI scale factor | Optional | `src/windows/platform_utils.py` | None |
| `QT_AUTO_SCREEN_SCALE_FACTOR` | Qt auto-scaling | Set automatically | `src/main.py` | None |
| `QT_ENABLE_HIGHDPI_SCALING` | Qt HiDPI enable | Set automatically | `src/main.py`, `src/windows/platform_utils.py` | None |

**No secrets are read from environment variables.** The app is fully offline and self-contained.

## Runtime Configuration

Runtime settings are stored in `~/.mindful_optimizer/settings.json` (JSON) and the SQLite `settings` table.

### `settings.json` (managed by `AdaptiveMainWindow`)

| Key | Type | Default | Purpose |
|-----|------|---------|---------|
| `theme` | string | `"ember"` | Active theme name |
| `font_scale` | float | `1.0` | Font size multiplier |
| `color_blind_mode` | string \| null | `null` | Accessibility mode |
| `reduced_motion` | boolean | `false` | Reduce animations |
| `dyslexia_font` | boolean | `false` | Use dyslexia-friendly font |

### SQLite `settings` table (managed by `DatabaseManager`)

| Key | Example Value | Category |
|-----|---------------|----------|
| `theme` | `"dark"` | `appearance` |
| `notifications_enabled` | `"true"` | `notifications` |

## Build Configuration

### `pyproject.toml` (canonical source)

- **Build system:** `setuptools>=61.0`
- **Package name:** `mindful-organizer`
- **Version:** `1.0.0`
- **Python requires:** `>=3.11`
- **Entry points:**
  - `mindful-organizer = main:main`
  - `mindful-organizer-gui = main:main`

### `setup.py` (legacy wrapper)

- Kept for compatibility with older install workflows
- Metadata is delegated to `pyproject.toml`
- Should not be edited independently

### `requirements.txt` (legacy)

- Lists **core runtime dependencies only**
- For development, use `pip install -e ".[dev]"`

## Tool Configuration

| Tool | Config Location | Key Settings |
|------|----------------|--------------|
| **pytest** | `pyproject.toml` `[tool.pytest.ini_options]` | `testpaths = ["tests"]`, `--cov=src`, markers: `gui`, `slow`, `integration` |
| **ruff** | `pyproject.toml` `[tool.ruff]` | target `py311`, line-length 100, select `E,F,I,N,W,UP,B,C4,SIM` |
| **mypy** | `pyproject.toml` `[tool.mypy]` | python 3.11, `ignore_missing_imports = true` |
| **pre-commit** | `.pre-commit-config.yaml` | ruff lint+format, mypy, trailing-whitespace, EOF fixer |

## Feature Flags

There are **no explicit feature flags** in the codebase. Feature gating is done via `SubscriptionManager.has_feature()` based on the current tier (Free/Pro/Premium/Trial).

## Configuration Drift and Confusion

| Issue | Evidence | Status |
|-------|----------|--------|
| `pytest.ini` duplicated pytest config | Existed alongside `pyproject.toml` | **Fixed** — removed `pytest.ini`, consolidated into `pyproject.toml` |
| `setup.py` duplicated package metadata | Version and dependencies could drift from `pyproject.toml` | **Fixed** — reduced to a setuptools shim |
| `requirements.txt` had different versions and optional deps as core | `numpy>=1.21.0` vs `>=1.24.0` | **Fixed** — trimmed to core deps only with note |
| `build.sh` referenced nonexistent paths | `mindful_organizer/` dir, `setup.py sdist` | **Fixed** — rewritten to use PyInstaller |
