# Assumptions and Inference Log

**Purpose:** Tracked record of important inferences made during documentation and audit.  
**Intended audience:** Auditors, maintainers, future engineers.  
**Confidence:** Each entry is labeled.  
**Last updated:** 2026-05-02

## Inferences

### A1: Target users have ADHD, Anxiety, Depression, OCD, PTSD, or Bipolar Disorder
- **Why inferred:** `Condition` enum includes these values. Profile builder, task decomposer, and wellness orchestrator all have condition-specific branches.
- **Evidence:** `src/core/constants.py`, `src/profiles/mental_health_profile_builder.py`, `src/core/wellness_orchestrator.py`
- **Confidence:** High-confidence inference
- **What a human should verify:** Whether the app is genuinely used by people with these conditions, or if the condition list is aspirational.

### A2: The product is intended for commercial distribution
- **Why inferred:** Subscription tiers (Free/Pro/Premium), license key generation, trial mechanics, Windows Store packaging, and store listing with pricing.
- **Evidence:** `src/core/subscription_manager.py`, `windows_store/store_listing.md`, `windows_store/AppxManifest.xml`
- **Confidence:** High-confidence inference
- **What a human should verify:** Whether there is an actual go-to-market plan, or if the subscription system is a prototype.

### A3: The app is single-user per OS account
- **Why inferred:** No user authentication, no multi-user schema, single-instance lock, data directory is per-user.
- **Evidence:** `src/main.py` single-instance logic, `src/core/database.py` hardcoded `DB_FILE` in home directory
- **Confidence:** Confirmed
- **What a human should verify:** N/A — confirmed by source.

### A4: No HIPAA compliance claims exist
- **Why inferred:** The disclaimer says "not a medical device" and there is no HIPAA Business Associate Agreement, encryption at rest for the DB, or audit logging.
- **Evidence:** `README.md` disclaimer, `src/core/database.py` (no encryption), `docs/security.md`
- **Confidence:** High-confidence inference
- **What a human should verify:** Whether any marketing or packaging claims HIPAA compliance. If so, the app does not meet those requirements.

### A5: `backup/` directory is dead code
- **Why inferred:** It is not referenced by `src/main.py`, `pyproject.toml`, or any import statement in the active codebase.
- **Evidence:** `grep -r "from backup\." src/` returns nothing; `grep -r "import backup" src/` returns nothing.
- **Confidence:** Confirmed
- **What a human should verify:** Whether the `backup/` directory contains anything not present in `src/` that needs to be preserved (e.g., unique asset files).

### A6: CI runs flake8 for legacy reasons, not because it's the preferred linter
- **Why inferred:** `.pre-commit-config.yaml` and local dev docs reference ruff. The CI workflow still runs flake8.
- **Evidence:** `.github/workflows/tests.yml` lines 40-43, `.pre-commit-config.yaml`
- **Confidence:** Confirmed
- **What a human should verify:** Whether the CI workflow should be updated to run ruff instead of flake8.

### A7: The data directory name was previously .mindful_optimizer (a typo)
- **Why inferred:** The product is "Hearth" but the directory was "optimizer".
- **Resolution:** Corrected to `.mindful_organizer` everywhere with migration logic in `src/main.py` for existing users.

### A8: `voice_journal.py` is intentionally a stub, not a bug
- **Why inferred:** The code contains explicit comments describing it as a placeholder, and the docstring was updated to document this status.
- **Evidence:** `src/wellness/voice_journal.py` lines 101-115
- **Confidence:** Confirmed
- **What a human should verify:** Whether there is a roadmap item to implement real voice recording, and what the intended backend is (PyAudio, WebRTC, platform APIs).

### A9: `store_listing.md` contains hallucinated features
- **Why inferred:** "Focus Sessions" / "Pomodoro-style focus timers" are advertised but no such classes, files, or references exist in `src/`.
- **Evidence:** `windows_store/store_listing.md`; `grep -ri "pomodoro\|focus_timer\|focus_session" src/` returns nothing.
- **Confidence:** Confirmed
- **What a human should verify:** Whether these features are planned for a future release and should remain in the listing with a "coming soon" label, or be removed entirely.
