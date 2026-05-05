# Dependencies and Integrations

**Purpose:** Inventory of third-party packages and integrations with risk assessment.  
**Intended audience:** Architects, security reviewers, operators.  
**Confidence:** Confirmed from `pyproject.toml`, `requirements.txt`, and source imports.  
**Last updated:** 2026-05-02

## Core Runtime Dependencies

Defined in `pyproject.toml` `[project.dependencies]`:

| Package | Version | Role | Critical? |
|---------|---------|------|-----------|
| PyQt6 | >=6.4.0 | GUI framework | **Yes** |
| numpy | >=1.24.0 | Numerical computing | **Yes** |
| cryptography | >=38.0.0 | Encryption (Fernet, scrypt) | No |
| psutil | >=5.9.0 | System monitoring | No |

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

These packages appear in `requirements.txt` or source but are **not** in `pyproject.toml`:

| Package | Where Found | Status |
|---------|-------------|--------|
| python-dateutil | `requirements.txt`, imports | **Inferred core** — used by NLP parser for date parsing |
| seaborn | `requirements.txt` | Not used in source |
| python-magic | `requirements.txt` | Not used in source |
| joblib | `requirements.txt` | Pulled in by scikit-learn |
| black | `requirements.txt` | Replaced by ruff |
| flake8 | `requirements.txt` | Replaced by ruff |
| sphinx | `requirements.txt` | Not used actively |
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
