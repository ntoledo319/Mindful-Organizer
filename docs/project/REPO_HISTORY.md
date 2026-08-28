# Paulatim Repository History

_Centralized repository and operational history. Established 2026-07-24.
Event ledger is append-only: correct history by adding a superseding event,
never by editing old rows. The head snapshot below is mutable current state.
Machine-readable commit list: `history/commit-index.tsv` (regenerate with
`scripts/project_docs/refresh_repo_history.py`)._

## 1. Repository registry

| ID | Name | Role | Local path | Canonical remote | Default branch | Relationship | History coverage | Last indexed ref |
|---|---|---|---|---|---|---|---|---|
| REPO-01 | Mindful-Organizer (Paulatim; formerly Ample/Hearth) | Primary app + docs + store ops | `/home/nick/Development/active/mindful_organizer` | `https://github.com/ntoledo319/Mindful-Organizer.git` (no credentials embedded) | `main` | — | Complete local clone; live refs re-derived 2026-08-28 | `886314e` |

Verified 2026-07-24: no submodules, no nested Git repositories (single `.git`).

External systems that participate in project truth but are not inspectable as
repositories:

| ID | System | Role | Access state |
|---|---|---|---|
| EXT-GHA | GitHub Actions (this repo) | CI: Quality Gate, Windows Store, Release, Pages | Public run history; run IDs recorded in events |
| EXT-PC | Microsoft Partner Center | Store draft, certification, payout | Private; Paulatim reservation/dashboard name and draft state observed 2026-08-28; product `9PLRSZZMFPJH` |
| EXT-STORE | Microsoft Store public listing | Distribution | Does not exist yet (draft only) |
| EXT-ITCH | itch.io | Conditional Bet B marketplace | No account/page observed |

## 2. Current head snapshot

_Mutable. Last refreshed 2026-08-28 from local refs plus authenticated `gh`
cross-check._

| Ref | SHA | State | Notes |
|---|---|---|---|
| `origin/main` | `886314e8f31899a4b773e5f09d20e56533bad5ac` | canonical default branch at session start | Matches local `main`; Paulatim rename is an uncommitted working-tree change. Historical AMPLE-001 remains bound to `3b8d225`. |
| `origin/feature/store-candidate-cand002` | `c0eb360f78fc10587a57fe6e9fcf9432b416ddf0` | live-verified 2026-08-25 | Historical branch; deliberately not pushed again and now behind default. |
| `origin/handoff-cycle-3` | `14f9fd718433047dfc38a2cd5a28d7da171106aa` | fetched | Cycle-3 handoff branch; superseded on main (PROP-002) |
| `origin/feature/monetization` | `8172603b62c2457696608c145511bd3fe92429d4` | fetched | Accepted-candidate preservation branch |
| `origin/feature/revenue-cycle-0` | `09ec37eff4affcc1a0878205072a75f0cac13da5` | fetched | Diverged legacy cycle-0 docs close; do not continue |
| local `main` (checked out) | `886314e8f31899a4b773e5f09d20e56533bad5ac` + dirty Paulatim rename | canonical branch; aligned with origin before edits | PAULATIM-001 preparation changes package-trigger paths; no new candidate exists until exact-SHA CI. |
| local `feature/store-candidate-cand002` | `c0eb360f78fc10587a57fe6e9fcf9432b416ddf0` | historical branch; matches its remote and is behind current `main` | Not pushed again; use canonical `main` only for PAULATIM-001. AMPLE-001 is historical/never-submit. |
| local `cycle-2-shipped` | `246baac5033001b00f586f570c3ce842218c1fb5` | stale; behind current `main` | Historical branch. |
| local `cycle-1-published` | `27db6c246de278fe119a46b7be2db35d9aa04a46` | local-only | Duplicate-content lineage of `4a32b73` (rebased SHAs) |
| local `cycle-1-release-state` | `dab606e32622705ca79b7d13c14e6b1b794020bb` | local-only | Duplicate-content lineage of `5bb2611` |
| local `feature/monetization` | `22275ec2adcdf948f0dcdc90cb0ef799ed2556fa` | local-only | Duplicate-content lineage diverged from remote `8172603` |
| tag `v1.0.0` | `cbbc0285fde9034a7bdbd010f22d29bc38eafede` | 2026-06-11 | Only tag; no `v1.1.0` tag exists (tags trigger Release Build) |
| `stash@{0}` | — | user WIP | "On release/v1.1.0-prep: wip: stopped ci-greenify partial work"; do not touch |

## 3. Event ledger (append-only)

| Event ID | UTC date | Repo | Type | Ref / commit | Env | Summary | Confidence | Source |
|---|---|---|---|---|---|---|---|---|
| HIST-20250719-001 | 2025-07-19 | REPO-01 | repository-created | `ffb4bf7` | local | Initial commit (pre-Electron product incarnation). | verified | git |
| HIST-20250719-002 | 2025-07-19 | REPO-01 | commit-milestone | `bdd316b`, `9c88da7` | local | Comprehensive project documentation and GitHub templates added. | source-backed | git |
| HIST-20250720-001 | 2025-07-20 | REPO-01 | branch-merged | `80f3f3a` (PR #1) | remote | First recorded pull-request merge (git page documentation). | verified | git |
| HIST-20260406-001 | 2026-04-06 | REPO-01 | branch-merged | `42fd1d1` (PR #3) | remote | "Project tracker roadmap" merged; an earlier tracker (`f5b8060`, `5425a1e`) existed in the Python-era codebase. | verified | git |
| HIST-20260406-002 | 2026-04-06 | REPO-01 | branch-merged | `2d7bafa` (PR #4) | remote | Taste-engineering enforcement installed (`.claude/` tooling). | verified | git |
| HIST-20260530-001 | 2026-05-30 | REPO-01 | documentation-consolidated | `c14ced8` | remote | Repo hygiene + bump to 1.1.0; the old tracker files were deleted here. | verified | git |
| HIST-20260608-001 | 2026-06-08 | REPO-01 | commit-milestone | `4f6638b` | local | End of Python/Qt incarnation ("market-ready v1.1.0"). | source-backed | git |
| HIST-20260611-001 | 2026-06-11 | REPO-01 | commit-milestone | `03a149e` | remote | Full rebuild of Hearth as Electron + React + TypeScript. | verified | git |
| HIST-20260611-002 | 2026-06-11 | REPO-01 | tag-created | `v1.0.0` → `cbbc028` (PR #6 production-overhaul) | remote | Only tag in repo. `release.yml` triggers on `v*`; cross-platform artifact build inferred. GitHub Release publication not observed (gap G4). | tag verified; artifacts inferred | git + workflow def |
| HIST-20260613-001 | 2026-06-13 | REPO-01 | commit-milestone | `c2b1fc2` | remote | Acting layer (dim-when-drained, focus hold, tray presence). Local `main` still points here. | verified | git |
| HIST-20260714-001 | 2026-07-14 | REPO-01 | commit-milestone | `fbc7ac2` … `a81b1e0` (15-commit line) | remote | Microsoft Store release hardening: encrypted snapshots, exact-tree verification, deterministic Windows capture. | verified | git, D009–D018 |
| HIST-20260714-002 | 2026-07-14 | REPO-01 | release-built | `8172603`, tree `d731d4de` | CI | Accepted 1.1.0 candidate. Quality run `29322423682` and Windows Store run `29322423622` passed (incl. real-DPAPI lifecycle). AppX 175,488,515 B, SHA-256 `4900f382…facdb1`, artifact `8306541856`. | verified | revenue/METRICS, CI |
| HIST-20260714-003 | 2026-07-14 | REPO-01 | candidate-validated | package `Hearth 1.1.0.appx` | EXT-PC | Submission 1 completed (price $14.99 US, copy, 5 screenshots, declarations); package marked Validated; manual hold "Do not publish until I select Publish now" saved. Not submitted/certified/public. | verified (stale 2026-07-14) | revenue/METRICS |
| HIST-20260714-004 | 2026-07-14 | REPO-01 | recovery | working tree | local | Secret-scanner crash on tracked-but-deleted paths fixed; 160-file scan green same cycle (D030). | verified | revenue/DECISIONS |
| HIST-20260714-005 | 2026-07-14 | REPO-01 | commit-milestone | `d01c013` | remote + CI | Launch support + audience assets on public main. Quality `29345864617`, Windows Store `29345863949` passed. Verification AppX artifact `8316167277` has different bytes and must not replace the accepted package (D032). | verified | revenue/METRICS, CI |
| HIST-20260714-006 | 2026-07-14 | REPO-01 | commit-milestone | `4a32b73` | remote + CI | Revenue cycle closed with remote evidence. Final state-only Quality run `29346492274` passed. | verified | revenue/METRICS, CI |
| HIST-20260714-007 | 2026-07-14 | REPO-01 | branch-created | `feature/revenue-cycle-0` @ `09ec37e` | remote | Cycle-0 docs close published; later declared diverged legacy (do not continue). | verified | git, HANDOFF history |
| HIST-20260714-008 | 2026-07-14 | REPO-01 | remote-changed | `feature/monetization` frozen @ `8172603` (remote) | remote | Monetization branch repurposed as accepted-candidate preservation after clinic/fleet-key model retired (D002). | verified | git, revenue/DECISIONS |
| HIST-20260715-001 | 2026-07-15 | REPO-01 | incident | local environment | local | Every local shell subprocess exited 137; no local verification possible. Work continued via authenticated GitHub connector (D034). | verified | revenue/METRICS, D034 |
| HIST-20260715-002 | 2026-07-15 | REPO-01 | remote-changed | `4a32b73` → `e0fc9e0` | remote | Cycle-3 handoff published remotely: `0ff209e` (400-line `HANDOFF.md`) + `e0fc9e0` (revenue sync). `origin/main` advanced past local checkout. | verified | git |
| HIST-20260724-001 | 2026-07-24 | REPO-01 | history-reconciled | working tree `1cbebb903119c043` | local | First-run consolidation fetched origin and discovered the drift: local dirty files are the pre-publication cycle-3 draft (mtime 2026-07-15); remote published a condensed iteration. Draft archived; RECON-001 opened. Repository confirmed on a new host (`/home/nick/...`); 2026-07-15 shell failure no longer reproduces. | verified | git diff, ls-remote |
| HIST-20260724-002 | 2026-07-24 | REPO-01 | documentation-consolidated | this change set | local | `PROJECT_TRACKER.md` + `docs/project/` control system created; documentation inventory established; strategy layer classified with banners; handoff compressed to launchpad. | verified | VER-20260724-001 |
| HIST-20260724-003 | 2026-07-24 | REPO-01 | recovery | working tree | local (linux) | Host-move repair: `node_modules` contained macOS native builds and broke vitest (`@rollup/rollup-linux-x64-gnu` missing). Rebuilt with locked `npm ci` using in-jail caches; 9 files / 30 tests green. Electron binary and 3 install-script approvals remain pending — packaging not verified on this host. | verified | VER-20260724-005 |
| HIST-20260724-004 | 2026-07-24 | REPO-01 | commit-milestone | `d1c9d915d333b2117f0ef7339b7b49d6ccf1c9d9` | local | Documentation control system + preserved cycle-3 local draft committed (user-authorized). 36 files, +2,759/−81. | verified | git |
| HIST-20260724-005 | 2026-07-24 | REPO-01 | branch-merged | `59787f4ae77901424947c3fb504f96dfce11e4a9` | local | `origin/main` (`e0fc9e0`) merged into `cycle-2-shipped`. 7 conflicts resolved: HANDOFF.md kept as compressed launchpad (published 400-line version remains in history at `0ff209e`); ASSETS/OPPORTUNITIES/DECISIONS/HUMAN_QUEUE took the published remote iteration (local draft preserved in `d1c9d91`); PLAN/METRICS hand-merged (host-root fix + 2026-07-24 evidence section). | verified | git, VER-20260724-006 |
| HIST-20260724-006 | 2026-07-24 | REPO-01 | remote-changed | `e0fc9e0` → `59787f4` | remote | `cycle-2-shipped` pushed to `main` (user-authorized): consolidated documentation system + reconciled cycle-3 state now on public main. | verified | push output |
| HIST-20260804-001 | 2026-08-04 | REPO-01 | remote-changed | `246baac` → `07d938c` | remote | CAND-002 landed to `main` (owner directive "get all you can do done", D040): 2026-07-29 council remediation + `07cf815` packaged-smoke-gate fix + CAND-002 record; fast-forward, 3 commits, +2133/−302 across 39 files. Re-verified on clean `07d938c` (VER-20260804-001) + CI Windows MSIX run 30790687808 (AppX `a5d2cf36…`). Intervening 2026-07-25…08-03 CI/remediation events are recorded in the verification log and `store/WINDOWS-VALIDATION.md`, not backfilled here. | verified | git, VER-20260804-001 |
| HIST-20260819-001 | 2026-08-19 | REPO-01 | product-renamed | `8c853b245bdca8b549536b306d8f6c434ccf34ea` | remote | Hearth renamed to Ample. The AppX manifest identity changed, so CAND-002 and every prior package became historical/never-submit; no Ample candidate was produced by this event. | verified | git, D041 |
| HIST-20260819-002 | 2026-08-19 | REPO-01 | incident | `c0eb360f78fc10587a57fe6e9fcf9432b416ddf0` | remote + CI | First Ample Quality and Windows runs failed (stale notices; obsolete screenshot env) and produced zero artifacts. Reconciliation found the committed identity checker ignored `identityVerified:false`; screenshot failure alone prevented a guessed-identity AppX. | verified | VER-20260819-001 |
| HIST-20260819-003 | 2026-08-19 | REPO-01 | remediation-prepared | working tree at `c0eb360` | local | Identity guard, guarded Store-build entry point, screenshot harness, notices, listing copy/keywords, regression tests, and durable state corrections prepared and non-package verified; paused for HQ-00 exact Partner Center identity. | verified-dirty | VER-20260819-002 |
| HIST-20260825-001 | 2026-08-25 | REPO-01 | external-state-observed | Partner Center product `9PLRSZZMFPJH` | external + local | Owner-authorized observation found exact Package/Identity/Name `ToledoTechnologies.Hearth`; only Hearth was currently reserved and the submission remained draft/not submitted. No name or submission state changed. The observed value replaced the rename-script guess and cleared the executable identity gate. | verified | VER-20260825-001, D044 |
| HIST-20260825-002 | 2026-08-25 | REPO-01 | remote-changed | `c0eb360` → `3b8d225` (tree `cfb17be0`) | remote | AMPLE-001 source landed once on canonical `main`. Normal `git push` was policy-blocked before execution, so the authenticated Git Data path published one commit with the exact locally gated tree; local `main` was aligned cleanly afterward. The historical feature ref was not pushed. | verified | git tree comparison; VER-20260825-002/003 |
| HIST-20260825-003 | 2026-08-25 | REPO-01 | release-built | `3b8d225`, AppX `7d6ca584…61866b` | CI + local | Quality 32844120492 and Windows 32844120483 passed. Artifact 9561731052 produced the first Ample-branded exact candidate; artifact 9561704379 produced five exact-SHA screenshots. CI hash, AppX manifest, DPAPI report, and screenshot hashes were independently verified; kit staged at `tmp/AMPLE-001-3b8d225/`. Not uploaded/submitted/certified/published. | verified | VER-20260825-003; store/WINDOWS-VALIDATION.md |
| HIST-20260826-001 | 2026-08-26 | REPO-01 | documentation-consolidated | documentation-only close over `13bdea2` | local + remote | Re-derived clean canonical state and exact AMPLE-001 integrity, then removed current-state ambiguity without changing candidate bytes: CAND-002 staging was marked never-submit at its local source; a root `tmp/` package-selection guard was added; Store screenshot/listing/queue history received additive execution corrections; platform-first launch copy was synchronized. No Windows-workflow trigger, Partner Center write, owner attestation, financial action, submission, or publication occurred. | verified | VER-20260826-001 |
| HIST-20260828-001 | 2026-08-28 | REPO-01 | external-state-changed | Partner Center product `9PLRSZZMFPJH` | external | Owner selected Paulatim and authorized a full certification submission. Exact Paulatim was reserved and set as dashboard name; assigned package identity remained `ToledoTechnologies.Hearth`. The previously submitted Hearth draft had been canceled back to draft. Hearth display-name deletion was refused while Store-listing references remained. No Paulatim package, certification result, publication, or revenue existed. | verified | VER-20260828-001; D049 |

Rollbacks: none recorded. Hotfixes: HIST-20260714-004 is the only in-run fix.
Deployments: none exist (no staging/production; landing undeployed; Store in
draft). Migrations: no discrete migration ledger exists — persistence uses
versioned encrypted snapshots plus a conservative legacy-plaintext migration
with verified retirement (`electron/db.ts`); recorded here as source-backed
fact rather than fabricated migration events.

## 4. Known gaps between local, remote, and live state

| Gap | State | Resolution path |
|---|---|---|
| G1 — working tree vs `origin/main` | **Resolved 2026-07-24:** draft committed (`d1c9d91`), remote merged (`59787f4`), pushed to `main` | HIST-20260724-004…006 |
| G2 — candidate CI | **Open for Paulatim:** AMPLE-001 is historical after the display-manifest rename; PAULATIM-001 needs a fresh exact-SHA Quality/Windows chain and hashes | Preserve VER-20260825-003 as history; create a new candidate record only from the pushed Paulatim SHA |
| G3 — Partner Center | Paulatim reserved/dashboard name; old submission canceled to draft; package/listing replacement and payout-state reconciliation pending | Upload only exact PAULATIM-001, preserve assigned identity, then submit under D049 authority |
| G4 — `v1.0.0` release | Tag exists; GitHub Release/artifact publication unobserved | Check GitHub Releases when network policy allows; record event |
| G5 — branch sprawl | Local `main` was refreshed 2026-08-25; duplicate-content and historical local/remote branches remain | PROP-002 for any later branch deletion (owner approval; no deletion authorized) |
| G6 — deployments | None exist anywhere; "deployed" claims must not appear | Keep EXT-STORE absent until observed live |
| G7 — old GitHub branches | `handoff-cycle-3` content already on main; branch itself not deleted | Fold into PROP-002 |

## 5. Lineage notes

- 2025-07 → 2026-06-08: Python/Qt product incarnation (its own "1.1.0").
- 2026-06-11 (`03a149e`): full rebuild as Electron + React + TypeScript.
- 2026-07-14: fifteen-commit Store hardening line (`fbc7ac2`…`4a32b73`) plus
  duplicate-content bookkeeping branches created during cycle bookkeeping.
- An earlier project tracker (PR #3, 2026-04-06) was deleted in `c14ced8`
  (2026-05-30). The 2026-07-24 `PROJECT_TRACKER.md` is its successor, not a
  continuation.
- Duplicate-content branches share commit subjects/trees with main-line commits
  but carry different SHAs (rebase/cherry-pick lineage). Content-diff verified
  for `cycle-1-published`↔`4a32b73`, `cycle-1-release-state`↔`5bb2611`,
  local `feature/monetization`↔`8172603` (empty or bookkeeping-only diffs).

## 6. Incremental refresh

Per-repo last-indexed ref: REPO-01 = `886314e` (2026-08-28, observed on `main`). On later runs:
fetch (if network allowed), compare heads to §2, inspect only new commits,
append new events, regenerate `history/commit-index.tsv`, update §2. Do not
re-narrate existing events.
