# Dependencies and Integrations

**Purpose:** Inventory of third-party packages and integrations with risk assessment.  
**Intended audience:** Architects, security reviewers, operators.  
**Confidence:** Confirmed from `pyproject.toml`, `requirements.txt`, and source imports.  
**Last updated:** 2026-05-30 (Hearth 1.1.0)

## Core Runtime Dependencies

Defined in `pyproject.toml` `[project.dependencies]`:

| Package | Version | Role | Critical? |
|---------|---------|------|-----------|
| PyQt6 | >=6.4.0 | GUI framework | **Yes** |
| numpy | >=1.24.0 | Numerical computing | **Yes** |
| cryptography | >=41.0.0 | Encryption (Fernet, scrypt) | No |
| psutil | >=5.9.0 | System monitoring | No |
| keyring | >=24.0.0 | OS credential storage | No |

**Removed in 1.1.0:** `fastapi`, `uvicorn`, `pydantic`, and `httpx` are no longer
dependencies. They backed an experimental local HTTP layer (`src/hearth_api`) that
never shipped with the desktop product and has been removed from the runtime. See
[`docs/architecture.md`](architecture.md) for the rationale.

## Optional Dependencies

### ML (`[ml]` extra)

| Package | Version | Role | Graceful Degradation? |
|---------|---------|------|----------------------|
| scikit-learn | >=1.3.0 | Energy prediction, task ranking | Yes |
| pandas | >=2.0.0 | Data processing for analytics | Yes |
| matplotlib | >=3.7.0 | Chart generation | Yes |

### NLP / Clustering (`[nlp]` extra)

| Package | Version | Role | Graceful Degradation? |
|---------|---------|------|----------------------|
| sentence-transformers | >=2.2.0 | File content embeddings | Yes |
| hdbscan | >=0.8.28 | File clustering | Yes |
| umap-learn | >=0.5.3 | Dimensionality reduction | Yes |

### Development (`[dev]` extra)

| Package | Version | Role |
|---------|---------|------|
| pytest | >=7.4.0 | Testing framework |
| pytest-cov | >=4.1.0 | Coverage |
| pytest-qt | >=4.2.0 | Qt testing utilities |
| ruff | >=0.1.0 | Linting and formatting |
| mypy | >=1.6.0 | Type checking |
| pre-commit | >=3.5.0 | Git hooks |

## Notable Missing from pyproject.toml

These packages appear in source or legacy documentation but are **not** in `pyproject.toml`:

| Package | Where Found | Status |
|---------|-------------|--------|
| python-dateutil | source imports | **Inferred optional/core** — used by NLP parser for date parsing |
| requests | `scripts/fetch_meditations.py` | Only used by optional script |

## SaaS / API Integrations

| Integration | Purpose | Data Sent | Auth | Runtime? |
|-------------|---------|-----------|------|----------|
| GitHub API (releases) | Update checking | None | None | Optional |
| Chart.js CDN | Report charts | None | None | Only in HTML reports |
| External MP3 URLs | Meditation downloads | None | None | Only via `fetch_meditations.py` |

## Operational Risk Summary

| Risk | Level | Rationale |
|------|-------|-----------|
| PyQt6 supply chain | Medium | Large binary wheels; monitor for CVEs |
| cryptography outdated | Medium | Security-critical; must stay current |
| Optional ML deps fail to install | Low | App functions without them |
| No dependency audit in CI | Medium | No `pip-audit`, `safety`, or `dependabot` scanning |
| requests used only in script | Low | Not in runtime dependencies |

## Replacement Difficulty

| Component | Replacement | Difficulty | Notes |
|-----------|-------------|------------|-------|
| PyQt6 | PySide6, wxPython, Tkinter | High | Entire GUI layer would need rewrite |
| SQLite | PostgreSQL, local JSON | Medium | Would enable multi-user but adds complexity |
| numpy | pure Python | High | Used throughout wellness orchestrator |
| cryptography | pycryptodome | Low | API differs but concepts are the same |
| scikit-learn | rule-based heuristics | Already done | Fallback exists in `ai_optimizer.py` |
