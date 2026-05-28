# Hearth

*A desktop that adapts to your psychology.*

The Hearth Project is a desktop-native psychological operating-system layer for people managing ADHD, anxiety, depression, OCD, PTSD, or bipolar disorder. It reconfigures your computing environment in real time based on psychological state — closes apps during anxiety spikes, dims the display when energy is low, enforces Do Not Disturb during manic windows, and reorganizes files to match cognitive capacity. Built in Python and PyQt6. All data is stored locally — no cloud sync, no telemetry.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0%2B-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-informational.svg)

## What It Is

Hearth is a single-user, offline-first desktop application that adapts the computing environment to the user's psychological state. It supports people managing ADHD, Anxiety, Depression, OCD, PTSD, and Bipolar Disorder — not by adding another tracking app, but by treating the desktop itself as the intervention surface.

**Confirmed capabilities (from source):**

- **Task management** — CRUD, subtasks, dependencies, recurring tasks, templates, undo/redo, energy-based filtering and sorting. Persists to JSON (`tasks.json`); a one-time JSON→SQLite migration auto-runs on first launch.
- **Mood tracker** — 1–10 mood scores with condition-specific symptoms. Persists to SQLite (`mood_entries` table).
- **Sleep tracker** — Bedtime, wake time, quality (1–10), duration. Persists to SQLite (`sleep_logs` table).
- **DBT Diary Card** — Daily structured tracking of emotions, urges, skills, effectiveness, target behaviors, substances, and medication adherence. Added in schema v2.
- **Energy predictor** — Forecasts from sleep + mood + task history. Optional ML deps (`scikit-learn`) enable smarter ranking; graceful degradation without them.
- **Wellness orchestrator** — Cross-module intelligence that produces `WellnessSnapshot`, detects crisis heuristics (mood crash + sleep deprivation, rapid mood drop, medication miss streak), and generates daily briefings.
- **Therapeutic tools** — Breathing exercises, grounding techniques, guided meditation metadata, journaling with prompts, ERP exposure tracking, crisis plan with contacts.
- **File organizer** — Condition-aware organization modes (ADHD/OCD/Depression/Anxiety). Includes smart file system with optional ML clustering (`sentence-transformers`, `hdbscan`).
- **Secure content folders** — Passcode-protected folders using Fernet encryption + scrypt. Keys are stored in the OS credential store (Keychain on macOS, Credential Manager on Windows, SecretService on Linux), not next to the ciphertext.
- **Shareable reports** — Self-contained HTML reports with Chart.js (loaded from CDN). No runtime dependency.
- **Subscription tiers** — Free / Pro / Premium. License keys are signed with Ed25519; only the public verification key ships in the binary. A 14-day Premium trial is available without a key.

**Partial / stub implementations:**
- `calendar_sync.py` — Stubbed ICS integration.
- `auto_updater.py` — Checks GitHub releases but does not auto-install.
- `wearable_sync` — Listed as a Premium feature but has no implementation.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.11+ |
| GUI | PyQt6 |
| Persistence | SQLite (WAL mode, schema v2) + JSON for legacy task data |
| Optional ML | scikit-learn, pandas, matplotlib |
| Optional NLP / clustering | sentence-transformers, hdbscan, umap-learn |
| Encryption | cryptography (Fernet + scrypt for content vault; Ed25519 for license signing) |
| Key storage | OS keyring (Keychain / Credential Manager / SecretService) |
| Build | setuptools (`pyproject.toml`) + PyInstaller (`mindful_organizer.spec`) |
| CI | GitHub Actions (`pytest` across Linux/macOS/Windows × Py 3.9–3.12) |
| Release | `.github/workflows/release.yml` builds MSIX (Windows) and `.app` (macOS) on `v*` tags |

## Prerequisites

- Python 3.11, 3.12, or 3.13
- pip
- Git

## Installation

```bash
git clone https://github.com/ntoledo319/Mindful-Organizer.git
cd Mindful-Organizer
python3 -m venv venv312
source venv312/bin/activate  # Windows: venv312\Scripts\activate
pip install -e ".[dev]"
```

Optional ML features:
```bash
pip install -e ".[ml,nlp]"
```

## Local Development

```bash
# Run the app
python src/main.py

# Run tests (excludes GUI tests)
pytest -m "not gui and not slow"

# Run with coverage
pytest -m "not gui and not slow" --cov=src --cov-report=term-missing

# Linting
ruff check src/ tests/

# Formatting
ruff format src/ tests/

# Type checking
mypy src/
```

## Build

### macOS / Linux (PyInstaller)
```bash
bash build.sh
```

### Windows (PyInstaller)
```batch
build_windows.bat
```

The canonical spec is `mindful_organizer.spec`. The `build.sh` script uses PyInstaller; the older manual `.app` bundle logic has been removed.

## Repository Structure

```
├── src/
│   ├── main.py                 # Application entry point
│   ├── core/                   # Business logic & data access
│   ├── gui/                    # PyQt6 UI layer
│   ├── profiles/               # Mental health profile system
│   ├── wellness/               # Therapeutic modules
│   ├── security/               # Encryption & access control
│   ├── utils/                  # Shared helpers
│   └── windows/                # Platform-specific utilities
├── tests/
│   ├── unit/                   # Isolated tests
│   └── integration/            # Cross-module workflow tests
├── docs/                       # Documentation suite
├── resources/                  # Meditations and assets
├── scripts/                    # Utility scripts
└── pyproject.toml              # Build, dependencies, tool config
```

## Documentation

See [`docs/DOCS_INDEX.md`](docs/DOCS_INDEX.md) for the full documentation suite.

Quick pointers:
- [Architecture](docs/architecture.md)
- [Security Review](docs/security.md)
- [Tech Debt & Gaps](docs/tech-debt-and-gaps.md)
- [Onboarding](docs/onboarding.md)

## Known Caveats

1. **Data directory naming quirk** — The app uses `.mindful_optimizer` (a legacy typo) as the data directory name. This is consistent across all running code, but it differs from the product name.
2. **TaskManager uses JSON, not SQLite** — Tasks are stored in `tasks.json` while mood, sleep, medications, etc. use SQLite. `MigrationManager` can migrate legacy JSON to SQLite but the app does not do this automatically on boot.
3. **CI runs `flake8`, not `ruff`** — The GitHub Actions workflow still uses `flake8` for legacy reasons. Local development uses `ruff`.
4. **Windows Store assets missing** — `windows_store/assets/` contains no PNG images; store submission would fail without them.
5. **Hardcoded license secret** — `subscription_manager.py` contains an offline HMAC secret. This is acceptable for offline-only validation but must be replaced before any commercial distribution.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Disclaimer

Hearth is a personal mental-health-aware desktop tool. It is **not** a medical device, does not provide medical advice, diagnosis, or treatment, and is **not** a substitute for professional healthcare. If you are in crisis, call 988 (US) or your local emergency number.
