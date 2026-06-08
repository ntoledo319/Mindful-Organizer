# Hearth

_A desktop that adapts to your psychology._

The Hearth Project is a desktop-native psychological operating-system layer for people managing ADHD, anxiety, depression, OCD, PTSD, or bipolar disorder. It reconfigures your computing environment based on psychological state — closes distracting apps during anxiety spikes, enforces Do Not Disturb, dims the display, and organizes files. Built in Python and PyQt6. All data is stored locally — no cloud sync, no telemetry.

> **Platform support.** The full app — tracking, therapeutic tools, the adaptive
> dashboard, crisis resources — runs on macOS, Linux, and Windows. **Live OS
> actuation** (closing apps, Do Not Disturb, display dimming) is currently
> implemented and verified on **macOS only**; on Windows and Linux those specific
> actions are inert (the app says so rather than pretending to act) until their
> backends land. Hearth never reports a system change that didn't happen.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.4.0%2B-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-informational.svg)

## What It Is

Hearth is a single-user, offline-first desktop application that adapts the computing environment to the user's psychological state. It supports people managing ADHD, Anxiety, Depression, OCD, PTSD, and Bipolar Disorder — not by adding another tracking app, but by treating the desktop itself as the intervention surface.

**Confirmed capabilities (from source):**

- **Task management** — CRUD, subtasks, dependencies, recurring tasks, templates, undo/redo, energy-based filtering and sorting. Persists task records to SQLite; legacy JSON task data is migrated on first launch.
- **Mood tracker** — 1–10 mood scores with condition-specific symptoms. Persists to SQLite (`mood_entries` table).
- **Sleep tracker** — Bedtime, wake time, quality (1–10), duration. Persists to SQLite (`sleep_logs` table).
- **DBT Diary Card** — Daily structured tracking of emotions, urges, skills, effectiveness, target behaviors, substances, and medication adherence. Added in schema v2.
- **Energy predictor** — Forecasts from sleep + mood + task history. Optional ML deps (`scikit-learn`) enable smarter ranking; graceful degradation without them.
- **Wellness orchestrator** — Cross-module intelligence that produces `WellnessSnapshot`, detects crisis heuristics (mood crash + sleep deprivation, rapid mood drop, medication miss streak), and generates daily briefings.
- **Therapeutic tools** — Breathing exercises, grounding techniques, guided meditation metadata, journaling with prompts, ERP exposure tracking, crisis plan with contacts.
- **Focus Sessions** — Pomodoro-style deep-work timer with circular progress UI, customizable presets, and automatic DND activation to protect attention.
- **Voice Journal** — Record journal entries directly in the app (gracefully degrades to text-only when no microphone is available).
- **Personal Insights** — Local analytics generated from the user's own historical data; no generic templates.
- **PDF Export** — One-click export of wellness reports, diary cards, and mood timelines for sharing with clinicians.
- **File organizer** — Sorts files into a clean type-based structure, with an optional smart file system that uses ML clustering (`sentence-transformers`, `hdbscan`) when those extras are installed.
- **Secure content vault** _(library/API; no GUI surface yet)_ — Passcode-gated folders whose file contents are Fernet-encrypted at rest, with scrypt passcode hashing. The Fernet key lives in the OS credential store (Keychain / Credential Manager / SecretService), not next to the ciphertext. Exposed as `security.content_management.ContentManager`; a dedicated UI is on the roadmap.
- **Shareable reports** — Fully self-contained HTML reports with Chart.js vendored inline. They open offline and make **no network request**, so a report full of health data never phones home.
- **Calendar sync** — Exports tasks as ICS and parses external busy blocks for focus scheduling.
- **Wearable sync** — Imports Apple Health XML and Google Fit sleep CSV exports into local sleep logs.
- **Subscription tiers** — Free / Pro / Premium. License keys are signed with Ed25519; only the public verification key ships in the binary. A 14-day Premium trial is available without a key. See [`docs/PRICING_JUSTIFICATION.md`](docs/PRICING_JUSTIFICATION.md) for current pricing.

**Partial implementations:**

- `auto_updater.py` — Checks GitHub releases, presents changelog and download links, but does not auto-install updates.

## Tech Stack

| Layer                     | Technology                                                                            |
| ------------------------- | ------------------------------------------------------------------------------------- |
| Language                  | Python 3.11+                                                                          |
| GUI                       | PyQt6                                                                                 |
| Persistence               | SQLite (WAL mode, schema v4) + JSON for lightweight local config/templates            |
| Optional ML               | scikit-learn, pandas, matplotlib                                                      |
| Optional NLP / clustering | sentence-transformers, hdbscan, umap-learn                                            |
| Encryption                | cryptography (Fernet + scrypt for content vault; Ed25519 for license signing)         |
| Key storage               | OS keyring (Keychain / Credential Manager / SecretService)                            |
| Build                     | setuptools (`pyproject.toml`) + PyInstaller (`mindful_organizer.spec`)                |
| CI                        | GitHub Actions (`pytest` across Linux/macOS/Windows × Py 3.9–3.12)                    |
| Release                   | `.github/workflows/release.yml` builds MSIX (Windows) and `.app` (macOS) on `v*` tags |

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
- [Security Hardening Guide](docs/SECURITY_HARDENING.md)
- [Tech Debt & Gaps](docs/tech-debt-and-gaps.md)
- [Onboarding](docs/onboarding.md)

## Known Caveats

1. **Auto-updater does not self-install** — It checks release metadata, presents the changelog, and provides download links, but the user must run the installer manually.
2. **Live OS adaptation is macOS-only** — Windows and Linux report inert honestly; tracking and therapeutic features are fully cross-platform.
3. **Database is plaintext SQLite** — Protected by filesystem permissions (`0700` data dir / `0600` DB) and assumes OS full-disk encryption (FileVault/BitLocker). App-level encryption (SQLCipher) is a documented roadmap decision.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Disclaimer

Hearth is a personal mental-health-aware desktop tool. It is **not** a medical device, does not provide medical advice, diagnosis, or treatment, and is **not** a substitute for professional healthcare. If you are in crisis, call 988 (US) or your local emergency number.
