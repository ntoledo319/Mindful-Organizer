# Contributing Guide

**Purpose:** Inferred contribution expectations from repo structure and tooling.  
**Intended audience:** Contributors.  
**Confidence:** Inferred from config files; no formal governance doc exists.  
**Last updated:** 2026-05-02

## Coding Standards

The project uses the following tools, configured in `pyproject.toml`:

- **ruff** — Linting and formatting (replaces black, flake8, isort)
- **mypy** — Type checking
- **pytest** — Testing

Run before committing:

```bash
ruff check src/ tests/
ruff format src/ tests/
mypy src/
pytest -m "not gui and not slow"
```

## Style Conventions

- **Line length:** 100 characters
- **Quotes:** Double quotes
- **Indent:** 4 spaces
- **Imports:** Sorted via ruff (isort rules)
- **Type hints:** Encouraged but not strictly enforced (`disallow_untyped_defs = false` in mypy config)
- **Docstrings:** Google-style for public functions, classes, and modules

## Branch and PR Clues

- CI runs on pushes to `main`, `develop`, `feature/**`, and `claude/**`
- PRs target `main` or `develop`
- No formal branching model is documented, but the existence of `develop` suggests GitFlow-like usage

## Review-Sensitive Areas

Pay extra attention when modifying:

1. **`src/core/database.py`** — Schema changes affect all modules. Migrations must be backward-compatible.
2. **`src/security/content_management.py`** — Encryption and passcode handling. Small mistakes have large security impact.
3. **`src/core/subscription_manager.py`** — License validation logic. Changes affect revenue.
4. **`src/gui/main_window.py`** — Central orchestrator. Changes here can break many widgets.
5. **`src/core/wellness_orchestrator.py`** — Crisis detection heuristics. Must remain conservative and non-diagnostic.

## Test Expectations

- All new business logic should have unit tests in `tests/unit/`
- Integration tests go in `tests/integration/` for cross-module workflows
- GUI tests are welcome but must be marked with `@pytest.mark.gui`
- Use `tmp_data_dir` and `tmp_path` fixtures for filesystem isolation
- Mock external dependencies (network, platform APIs)

## Commit Guidance

No formal commit convention is enforced, but good practices:
- Use present tense ("Add feature" not "Added feature")
- Reference issue numbers if applicable
- Keep commits focused and atomic

## Release Hygiene

- Update `CHANGELOG.md` for user-facing changes
- Update version in `pyproject.toml` and `setup.py`
- Update `mindful_organizer.spec` version if building with PyInstaller
- Tag releases with `vX.Y.Z`
