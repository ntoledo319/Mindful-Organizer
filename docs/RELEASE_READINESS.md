# Hearth — Release Readiness & Production Target

_Synthesis of the v1.1.0 release-hardening pass. Supersedes the scattered root-level
process docs (AUDIT_REPORT, RELEASE_PUNCH_LIST, SUBMISSION_CHECKLIST, PROJECT_TRACKER)._

## What Hearth actually is

A **macOS-first, local-first PyQt6 desktop application** that adapts the computing
environment to a user's psychological state for people managing ADHD, anxiety,
depression, OCD, PTSD, or bipolar disorder. Zero telemetry; all data in a local SQLite
database. The desktop _is_ the intervention surface — not another tracking app.

The tracking, therapeutic, and wellness features are genuinely cross-platform. The
**live OS-adaptation** layer (closing apps, Do Not Disturb, display dimming) is
**verified on macOS only**; Windows/Linux ship the full app minus live actuation.

## Production target for this pass

The strongest **responsibly shippable** version of the desktop app: data-safe on
upgrade, never paywalling crisis support, honest about what it actuates on each OS,
buildable into a tested macOS artifact, with an honest at-rest threat model and a
documented release path. Code-signing/notarization + store accounts are the external
release gate.

## Verified strengths (preserve — do not regress)

- Real offline Ed25519 license validation (only the **public** key ships).
- Solid SQLite layer: schema v3, WAL, parameterized CRUD, idempotent ALTER migrations,
  thread-safe under load, online-backup + integrity-checked restore.
- Responsible clinical posture: "supplement not a replacement" disclaimers everywhere;
  988 / Crisis Text Line / SAMHSA hard-coded as always-available defaults; heuristics
  framed as observations, never diagnoses.
- Coherent 15-tab navigation shell with per-widget graceful degradation; real 6-page
  onboarding wizard; reactive StateBus refresh; partial real accessibility (font scale,
  color-blind overrides).
- Genuinely strong tests for subscription/licensing, database CRUD (97%), themes (100%),
  and the system-automation engine.
- Network surface is a single benign GitHub version check — the zero-telemetry claim holds.

## Decisive calls made this pass

1. **Platform scope** — macOS-first for live actuation. Windows/Linux backends return
   honest "not supported yet" instead of faking success; README/docs restated.
2. **FastAPI layer (`src/hearth_api`)** — **removed from the shipping product.** It was
   broken (all data routes 500), fully orphaned (no frontend exists; only its own theater
   test consumed it), and bloated runtime deps. Preserved in git history for a future,
   real Phase 2. fastapi/uvicorn/httpx dropped from runtime deps.
3. **PHI at rest** — filesystem hardening (0700 data dir / 0600 db) + the secure vault now
   genuinely encrypts file _contents_ (was metadata-only) + honest threat-model docs.
   Full-DB encryption (SQLCipher) is deferred as an explicit owner decision (cost/complexity).
4. **Version** — release as **1.1.0** (1.0.0 was an internal snapshot, never published).
5. **Git history bloat (~42MB binaries)** — left intact; history rewrite on a public repo
   is destructive and out of scope without explicit owner authorization. Documented.

## Blocker remediation index (22)

Data: guid backfill migration (v4). Clinical: un-paywall crisis; wire medication adherence
to SQLite; functional 988 buttons; risk-language detection; magnitude-scaled thresholds.
GUI: live dashboard quick-actions; fixed mood search; MoodManager `conditions=` crash.
OS: honest DND/brightness (real path or honest fallback, never fake success); honest
Win/Linux; AppleScript arg sanitization. Security: vault content encryption; fs perms.
Build: macOS `.app` BUNDLE + `.icns`; exe name = `hearth` (MSIX match); optional-dep-robust
spec. API: removed. Tests: kill phantom-module + silent-skip theater; add regression cover
for every safety fix. Hygiene: untrack `backup/`; remove tool cruft; brand drift → Hearth.
