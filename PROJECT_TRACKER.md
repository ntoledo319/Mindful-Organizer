# Hearth — Project Tracker

- **Schema:** project-tracker/v1 (2026-07-24)
- **Last updated:** 2026-07-24T09:30Z by Kimi Code CLI (first-run consolidation, close-out)
- **Workspace root:** `/home/nick/Development/active/mindful_organizer` (REPO-01)
- **Branch / HEAD:** `cycle-2-shipped` @ `4a32b73`; `origin/main` @ `e0fc9e0` (fetched + live-verified 2026-07-24)
- **Working tree:** dirty — cycle-3 draft + this consolidation; fingerprint `451945c517e87554` (see RECON-001)
- **Operating mode:** ECONOMY / MAINTENANCE from the next session on
- **Canonical set:** [AGENTS.md](AGENTS.md) · [HANDOFF.md](HANDOFF.md) · [Docs index](docs/project/DOCS_INDEX.md) · [History](docs/project/REPO_HISTORY.md) · [Verification](docs/project/VERIFICATION_LOG.md) · [Decisions](revenue/DECISIONS.md) · [Proposals](docs/project/PROPOSALS.md) · [Migration map](docs/project/MIGRATION_MAP.md) · [Archive](docs/project/archive/)

## 0. How to use this tracker

1. Session start: read `AGENTS.md`, then this file, then `git status --short --branch`.
2. Compare HEAD with the header above; if moved, work from `git log`/diff, not memory.
3. Read only the canonical document your task touches (section 2). History and
   archives are for historical questions and contradictions, not routine work.
4. Monetization cycles additionally read all six `revenue/` files (AGENTS.md law).
5. Statuses require evidence; `done` requires a VER id and an exact ref.
6. Session end: update statuses, verification snapshot, and ledgers; unfinished
   work becomes `paused` (resume point) or `blocked` (unblock condition).
7. Append to `REPO_HISTORY.md` / `VERIFICATION_LOG.md`; replace — don't stack —
   "current" rows here. Run `scripts/project_docs/validate_project_docs.py`.

## 1. Current executive snapshot

| Metric / environment | Current value | As of | Evidence |
|---|---|---|---|
| Product state | Hearth 1.1.0 release candidate; Store Submission 1 complete, held in draft | 2026-07-14 | revenue/METRICS.md |
| Default-branch HEAD (`origin/main`) | `e0fc9e0` | 2026-07-24 | HIST-20260715-002, ls-remote |
| Live release | none — not submitted, certified, published, or purchasable | 2026-07-14 | HIST-20260714-003 |
| Accepted candidate | AppX SHA-256 `4900f382…facdb1`, artifact 8306541856, Partner Center Validated | 2026-07-14 | VER-20260714-002 |
| Latest CI verification | Quality Gate pass @ `4a32b73` (run 29346492274) | 2026-07-15 | VER-20260715-001 |
| Latest local verification | all local gates green (secrets 181 files, store 269 checks, typecheck ×2, 9 files/30 tests, docs validator) | 2026-07-24 | VER-20260724-001…005 |
| Collected revenue | $0.00; gap $4,000.00; 0 live listings | 2026-07-14 | revenue/METRICS.md |
| Major open blocker | Owner-only legal/payout gates HQ-01, HQ-02 (44-min queue untouched) | 2026-07-24 | revenue/HUMAN_QUEUE.md |
| Next recommended action | Owner: HQ-01 (manual IARC retake). Agents: RECON-001 | 2026-07-24 | section 11 |

One current row per metric; superseded values live in REPO_HISTORY.md.

## 2. Source-of-truth map

| Truth domain | Canonical owner |
|---|---|
| Mission, jail, operating constraints | `AGENTS.md` |
| Cold-start launchpad | `HANDOFF.md` |
| Current coordination (this file) | `PROJECT_TRACKER.md` |
| Product overview + dev/quality commands | `README.md` |
| Architecture / persistence / heuristics | `docs/ARCHITECTURE.md` |
| Vaulted capabilities | `docs/CAPABILITY_VAULT.md` |
| Design system / taste | `docs/DESIGN_SYSTEM.md`, `CLAUDE.md` |
| Privacy, terms, refunds | `docs/PRIVACY.md`, `docs/TERMS.md`, `docs/REFUNDS.md` |
| Support, security policy, accessibility status | `docs/SUPPORT.md`, `SECURITY.md`, `docs/ACCESSIBILITY.md` |
| Store release path + certification playbook | `store/README.md` |
| Installed-Windows validation | `store/WINDOWS-VALIDATION.md` |
| Listing data, screenshots, campaigns, launch drafts | `store/listing-metadata.json`, `store/SCREENSHOTS.md`, `store/CAMPAIGNS.md`, `store/LAUNCH_KIT.md` |
| Monetization plan, assets, opportunities | `revenue/PLAN.md`, `revenue/ASSETS.md`, `revenue/OPPORTUNITIES.md` |
| Observed evidence (money, Store, CI) | `revenue/METRICS.md` |
| Owner-only actions | `revenue/HUMAN_QUEUE.md` |
| Decisions (D001–D034) | `revenue/DECISIONS.md` |
| Repository/release history | `docs/project/REPO_HISTORY.md` |
| Verification events | `docs/project/VERIFICATION_LOG.md` |
| Documentation map | `docs/project/DOCS_INDEX.md` |
| Unapproved scope | `docs/project/PROPOSALS.md` |

## 3. Workstream index

| ID | Workstream | Derived status | Tasks (ready/blocked/other) | Last verified ref | Active tasks |
|---|---|---|---|---|---|
| WS-REL | Microsoft Store release (Bet A, $14.99) | blocked — all paths hard-blocked on owner gates | 2 ready, 3 blocked | `8172603` (candidate), 2026-07-14 | HQ-01…HQ-05 |
| WS-REV | Monetization portfolio ($4,000 / Day 28) | blocked — Bet A = WS-REL; Bet B unapproved (PROP-005) | 0 active, 1 proposed | revenue/METRICS.md 2026-07-14 | — |
| WS-DOCS | Documentation control system | open — RECON-001 needs reconciliation; DOCS-001 done 2026-07-24 | 1 done, 1 needs-reconciliation | VER-20260724-001…005 | RECON-001 |

## 4. Active task table

| Task | Title | Source | Status | Priority | Owner | Deps | Acceptance | Verification | Last touched | Resume from |
|---|---|---|---|---|---|---|---|---|---|---|
| HQ-01 | Manual IARC retake with legal attestation | revenue/HUMAN_QUEUE.md | ready | critical | human | — | Truthful ratings saved; date + regional results in METRICS | METRICS entry | 2026-07-15 | HUMAN_QUEUE HQ-01 steps + Partner Center link |
| HQ-02 | Seller/tax/payout readiness | revenue/HUMAN_QUEUE.md | ready | critical | human | — | Payout-ready boolean + non-sensitive note in METRICS | METRICS entry | 2026-07-15 | HUMAN_QUEUE HQ-02 steps; allow 48h validation |
| HQ-03 | Choose test route; Store-signed Windows pass | revenue/HUMAN_QUEUE.md | blocked | high | human | HQ-04 (certification); route-choice sub-step is ready now | `store/WINDOWS-VALIDATION.md` + accessibility matrix completed on signed build, fictional data | Validation record (build, route, pass/fail, footprint, date) | 2026-07-15 | Unblock = HQ-04 certification complete; decide Public→Private audience route beforehand |
| HQ-04 | Submit for certification; publish deliberately | revenue/HUMAN_QUEUE.md | blocked | critical | human | HQ-01, HQ-02, HQ-03 route choice | Certification report preserved; `Publish now` only after all gates; signed-out purchase verified | Certification result + live URL in METRICS | 2026-07-15 | Unblock = HQ-01 done + payout ready + route chosen |
| HQ-05 | Approve and send first audience batch | store/LAUNCH_KIT.md | blocked | medium | human | live purchasable page | Owner-posted launch batch with URLs + timestamps in METRICS | METRICS entry | 2026-07-15 | Unblock = signed-out checkout verification |
| RECON-001 | Working tree vs `origin/main` draft drift | HIST-20260724-001 | needs-reconciliation | high | agent (+owner approval) | PROP-001 approval | Tree matches `e0fc9e0` or carries a documented exception; draft archived (done 2026-07-24) | clean `git status` or documented exception | 2026-07-24 | Present PROP-001 + draft-vs-published spot-diff to owner |
| DOCS-001 | Documentation consolidation + control system | user instruction 2026-07-24 | done | high | agent | — | Tracker, index, history, verification log, proposals, migration map, archive, validator all green | VER-20260724-001…005 @ working-tree:`4a32b73`+dirty:`451945c517e87554` | 2026-07-24 | — |

Status vocabulary: proposed / todo / ready / in-progress / paused / blocked /
needs-reconciliation / done / verified-stale / superseded / cancelled.

## 5. Active task details

### RECON-001 — Working-tree drift (needs-reconciliation)

- Objective: one authoritative project state again.
- Facts: dirty tree = pre-publication cycle-3 draft (mtime 2026-07-15);
  `origin/main` = published iteration (`0ff209e` + `e0fc9e0`); all 9 files
  differ in wording, same content class.
- Unblock condition: owner approves PROP-001 (adopt remote state, keep draft in
  archive) or directs a merge of specific draft-only lines.
- Notes: (1) Both iterations preserved (archive M1; Git history). (2) No
  evidence of unique draft-only facts in spot review; full spot-diff is part of
  execution. (3) Do not `git checkout --` user files without approval.

### HQ-04 — Certification then publication (blocked, highest risk)

- Unblock condition: HQ-01 truthful IARC saved + HQ-02 payout ready + HQ-03
  audience route chosen.
- Hard rules: never replace the accepted AppX with artifact 8316167277; manual
  hold stays until every gate passes; certification failure → preserve report,
  fix narrow cause, new evidence chain if bytes change (never weaken truthful
  disclosure).
- Post-publication playbook: `store/README.md` §"Certification and publication
  playbook".

## 6. Blockers, risks, active discoveries

| ID | Blocked item | Why | Unblock condition | Affected |
|---|---|---|---|---|
| B1 | Certification + publication | Owner-only legal attestation (IARC) and private payout setup not done; 0/44 owner minutes spent | Owner completes HQ-01, HQ-02 | HQ-04 → HQ-05, WS-REL, WS-REV |
| B2 | Authoritative git state | Dirty pre-publication draft vs published `origin/main` | PROP-001 approval + execution | RECON-001, clean verification refs |

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| R1 — zero demand after launch (no demand evidence exists) | high | Bet A falsifier path | 5-day signal gate → one reposition → replace (revenue/PLAN.md) | agent+owner |
| R2 — certification failure (runFullTrust, content review) | medium | delay; new candidate cycle | Truthful disclosures; preserve report; narrow fix only | owner (submit), agent (fix) |
| R3 — Partner Center facts stale (last observed 2026-07-14) | medium | decisions on old state | Re-verify live during HQ-01/HQ-02 session before acting | owner+agent |

Discovery (current): D-2026-07-24 — repository moved hosts (macOS → Linux);
`revenue/PLAN.md` line 1 and handoff startup path corrected; the 2026-07-15
exit-137 shell failure does not reproduce here. Destination: resolved into
HIST-20260724-001 after this session.

## 7. Current verification snapshot

| Gate | Ref | Env | Result | Summary | Timestamp | VER |
|---|---|---|---|---|---|---|
| Quality Gate (CI) | `4a32b73` | CI ubuntu | pass | full quality gate, state-close commit | 2026-07-15 | VER-20260715-001 |
| Windows Store build (CI) | `d01c013` | CI windows | pass | MSIX + screenshots + DPAPI lifecycle, 4m57s | 2026-07-14 | VER-20260714-005 |
| Local full gate | working-tree:`4a32b73`+dirty:`451945c517e87554` | local (linux) | pass | secrets 181 files; store 269 checks; typecheck ×2 0 errors; 9 files/30 tests in 3.38s; docs validator PASS | 2026-07-24 | VER-20260724-001…005 |
| Store certification | accepted AppX `4900f382…` | EXT-PC | not submitted | package Validated in draft only | 2026-07-14 | — |
| Installed Windows pass | — | physical Windows | not observed | blocked behind HQ-03/HQ-04 | — | — |

CI state for `e0fc9e0` (docs-only commits) not yet observed — see section 11.

## 8. Environment and release state

| Surface | Ref / version | State | Last verified | Evidence | Drift |
|---|---|---|---|---|---|
| Working tree | `4a32b73` + dirty `451945c517e87554` | cycle-3 draft + docs control system, uncommitted | 2026-07-24 | git status, VER-20260724-005 | diverged from `origin/main` (RECON-001); `node_modules` rebuilt for Linux via locked `npm ci` — Electron binary pending script approval, packaging unverified here |
| Local `cycle-2-shipped` | `4a32b73` | 2 behind `origin/main` | 2026-07-24 | git | behind |
| Local `main` | `c2b1fc2` | stale, 0 ahead / 17 behind | 2026-07-24 | git | stale (PROP-003) |
| `origin/main` | `e0fc9e0` | current | 2026-07-24 | ls-remote + fetch | — |
| CI | run 29346492274 @ `4a32b73` | green; head `e0fc9e0` unobserved | 2026-07-15 | VER-20260715-001 | G2 |
| Partner Center | Submission 1, package Validated, manual hold | draft; not submitted | 2026-07-14 (stale) | HIST-20260714-003 | G3 |
| Microsoft Store live | — | does not exist | — | — | no listing |
| Landing host | — | not deployed | — | landing/README.md | PROP-004 |

Implemented ≠ committed ≠ pushed ≠ tagged ≠ built ≠ submitted ≠ certified ≠
published ≠ live-verified. The only tag is `v1.0.0` (2026-06-11); no `v1.1.0`
tag exists because tags trigger the Release Build and the Store path is manual.

## 9. Recently completed

| Date | Item | Task | Verification | History |
|---|---|---|---|---|
| 2026-07-24 | Documentation control system established (this tracker, index, history, verification log, proposals, validator) | DOCS-001 | VER-20260724-001…005 | HIST-20260724-002 |
| 2026-07-15 | Cycle-3 canonical handoff published to `origin/main` | pre-tracker | VER-20260715-001 | HIST-20260715-002 |
| 2026-07-14 | Launch support + audience assets on public main | pre-tracker | VER-20260714-004/005 | HIST-20260714-005 |
| 2026-07-14 | Accepted 1.1.0 candidate + complete held Store draft | pre-tracker | VER-20260714-001/002 | HIST-20260714-002/003 |
| 2026-07-14 | Secret-scanner deletion-safety fix | pre-tracker | VER-20260714-006 | HIST-20260714-004 |

## 10. Proposed scope awaiting approval

Compact index — details in [PROPOSALS.md](docs/project/PROPOSALS.md). Do not
start without approval.

- PROP-001 reconcile working tree with `origin/main` (S)
- PROP-002 branch hygiene: duplicate/superseded branches (S, destructive)
- PROP-003 branch strategy: FF local `main`, retire `cycle-*` naming (S)
- PROP-004 landing deployment post-publication (S, gated)
- PROP-005 Bet B Electron kit (L, conditional — revenue/OPPORTUNITIES.md A4.6)

## 11. Next recommended actions

1. **Owner:** HQ-01 manual IARC retake, then HQ-02 payout readiness (queue: 44
   min total, `revenue/HUMAN_QUEUE.md`).
2. **Agent + owner:** resolve RECON-001 via PROP-001 (present spot-diff; adopt
   `e0fc9e0`; keep archived draft).
3. **Agent:** observe the Quality Gate run for `e0fc9e0`, record VER id, update
   section 7 (closes gap G2).
4. **Agent (before any packaging on this host):** restore the Electron binary
   (`npm approve-scripts` for the 3 pending install scripts) — tests/typecheck
   are green; `npm run dev` / packaging are not (VER-20260724-005 notes).
5. **After publication only:** execute `store/README.md` "After certification"
   playbook, then PROP-004 landing deploy and HQ-05 launch batch.

## 12. Ledger and archive links

- History: [docs/project/REPO_HISTORY.md](docs/project/REPO_HISTORY.md) (+ `history/commit-index.tsv`)
- Verification: [docs/project/VERIFICATION_LOG.md](docs/project/VERIFICATION_LOG.md)
- Decisions: [revenue/DECISIONS.md](revenue/DECISIONS.md)
- Proposals: [docs/project/PROPOSALS.md](docs/project/PROPOSALS.md)
- Docs index: [docs/project/DOCS_INDEX.md](docs/project/DOCS_INDEX.md)
- Migration map: [docs/project/MIGRATION_MAP.md](docs/project/MIGRATION_MAP.md)
- Archive: [docs/project/archive/](docs/project/archive/)
- Monetization evidence: [revenue/METRICS.md](revenue/METRICS.md)
