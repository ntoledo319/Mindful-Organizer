# Hearth — Project Tracker

- **Schema:** project-tracker/v1 (2026-07-24)
- **Last updated:** 2026-07-29T08:18Z by Kimi Code CLI (council remediation complete, all local gates green)
- **Workspace root:** `/home/nick/Development/active/mindful_organizer` (REPO-01)
- **Branch / HEAD:** `cycle-2-shipped` @ `246baac`; `origin/main` @ `246baac` (pushed 2026-07-25; Quality Gate green)
- **Working tree:** dirty — market-readiness council remediation complete and verified (VER-20260729-001), **uncommitted**, awaiting owner commit decision
- **Operating mode:** ECONOMY / MAINTENANCE
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
| Product state | Hearth 1.1.0 release candidate + council remediation in tree (uncommitted); Store Submission 1 complete, held in draft | 2026-07-29 | VER-20260729-001 |
| Default-branch HEAD (`origin/main`) | `246baac` (post-reconciliation state sync) | 2026-07-28 | git rev-parse, VER-20260728-002 |
| Live release | none — not submitted, certified, published, or purchasable | 2026-07-14 | HIST-20260714-003 |
| Accepted candidate | AppX SHA-256 `4900f382…facdb1`, artifact 8306541856, Partner Center Validated — **superseded in source**: remediation changed app bytes; a replacement candidate cycle (new AppX + refreshed screenshots) is required before HQ-04 | 2026-07-29 | VER-20260714-002 + VER-20260729-001 |
| Latest CI verification | Quality Gate pass @ `246baac` (run 30137666428); Windows Store MSIX pass @ `59787f4` (run 30137481905) | 2026-07-25, observed 2026-07-28 | VER-20260728-001…003 |
| Latest local verification | all local gates green on the remediated tree: lint 0 warnings, typecheck ×2, 12 files/46 tests, renderer+electron builds, secrets 189 files, store 276 checks, docs validator | 2026-07-29 | VER-20260729-001 |
| Collected revenue | $0.00; gap $4,000.00; 0 live listings; Day-15 gate assessment executed (D035) | 2026-07-28 | revenue/METRICS.md |
| Major open blocker | Owner-only legal/payout gates HQ-01, HQ-02 (59-min queue incl. HQ-06/HQ-07, 0 minutes spent) | 2026-07-28 | revenue/HUMAN_QUEUE.md |
| Next recommended action | Owner: HQ-01 (manual IARC retake) + commit decision on the remediated tree. Agents: CAND-002 after commit | 2026-07-29 | section 11 |

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
| Installed Windows validation | `store/WINDOWS-VALIDATION.md` |
| Listing data, screenshots, campaigns, launch drafts | `store/listing-metadata.json`, `store/SCREENSHOTS.md`, `store/CAMPAIGNS.md`, `store/LAUNCH_KIT.md` |
| Reposition menu execution, launch targets, post-publication doc sweep | `store/REPOSITION_KIT.md`, `store/LAUNCH_TARGETS.md`, `store/POST_PUBLICATION_DOC_SWEEP.md` |
| Monetization plan, assets, opportunities | `revenue/PLAN.md`, `revenue/ASSETS.md`, `revenue/OPPORTUNITIES.md` |
| Observed evidence (money, Store, CI) | `revenue/METRICS.md` |
| Owner-only actions | `revenue/HUMAN_QUEUE.md` |
| Decisions (D001–D039) | `revenue/DECISIONS.md` |
| Repository/release history | `docs/project/REPO_HISTORY.md` |
| Verification events | `docs/project/VERIFICATION_LOG.md` |
| Documentation map | `docs/project/DOCS_INDEX.md` |
| Unapproved scope | `docs/project/PROPOSALS.md` |

## 3. Workstream index

| ID | Workstream | Derived status | Tasks (ready/blocked/other) | Last verified ref | Active tasks |
|---|---|---|---|---|---|
| WS-REL | Microsoft Store release (Bet A, $14.99) | blocked — owner gates + replacement candidate cycle pending | 4 ready, 3 blocked | `8172603` (candidate), 2026-07-14 | HQ-01…HQ-07, CAND-002 |
| WS-REV | Monetization portfolio ($4,000 / Day 28) | blocked — Bet A = WS-REL; Day-15 gate executed (D035); reposition menu + kit ready; Bet B either/or pending owner (D038) | 0 active, 1 proposed | revenue/METRICS.md 2026-07-28 | — |
| WS-DOCS | Documentation control system | done 2026-07-24 (on public main @ `59787f4`) | 2 done | VER-20260724-001…006 | — |
| WS-READY | Market-readiness council + remediation | done 2026-07-29 in tree (uncommitted) | 1 done | VER-20260729-001 | — |

## 4. Active task table

| Task | Title | Source | Status | Priority | Owner | Deps | Acceptance | Verification | Last touched | Resume from |
|---|---|---|---|---|---|---|---|---|---|---|
| HQ-01 | Manual IARC retake with legal attestation | revenue/HUMAN_QUEUE.md | ready | critical | human | — | Truthful ratings saved; date + regional results in METRICS | METRICS entry | 2026-07-15 | HUMAN_QUEUE HQ-01 steps + Partner Center link |
| HQ-02 | Seller/tax/payout readiness (+ threshold/first-payout-date note) | revenue/HUMAN_QUEUE.md | ready | critical | human | — | Payout-ready boolean + non-sensitive note in METRICS | METRICS entry | 2026-07-28 | HUMAN_QUEUE HQ-02 steps; allow 48h validation |
| HQ-03 | Choose test route; Store-signed Windows pass | revenue/HUMAN_QUEUE.md | blocked | high | human | HQ-04 (certification); route-choice sub-step is ready now | `store/WINDOWS-VALIDATION.md` + accessibility matrix completed on signed build, fictional data (incl. forced-colors focus + 200% text-scaling line items, council CPO G6) | Validation record (build, route, pass/fail, footprint, date) | 2026-07-29 | Unblock = HQ-04 certification complete; decide Public→Private audience route beforehand |
| HQ-04 | Submit for certification; publish deliberately | revenue/HUMAN_QUEUE.md | blocked | critical | human | HQ-01, HQ-02, HQ-03 route choice, CAND-002 (replacement package) | Certification report preserved; `Publish now` only after all gates; signed-out purchase verified | Certification result + live URL in METRICS | 2026-07-29 | Unblock = HQ-01 done + payout ready + route chosen + new candidate accepted |
| HQ-05 | Approve and send first audience batch | store/LAUNCH_KIT.md + store/LAUNCH_TARGETS.md | blocked | medium | human | live purchasable page | Owner-posted launch batch with URLs + timestamps in METRICS | METRICS entry | 2026-07-28 | Unblock = signed-out checkout verification; destinations pre-vetted in LAUNCH_TARGETS.md |
| HQ-06 | Approve PROP-004 sequencing + deploy landing at certification time | revenue/HUMAN_QUEUE.md | ready | medium | human | owner approval of amended PROP-004 | Public prelaunch URL resolves signed-out; host + URL + timestamp in METRICS | METRICS entry | 2026-07-28 | HUMAN_QUEUE HQ-06 steps (host TOS re-check first — D007) |
| HQ-07 | Trademark clearance for "Hearth" (or 1-min risk acceptance) | revenue/HUMAN_QUEUE.md | ready | low | human | — | USPTO + Store search note in METRICS, or explicit risk acceptance in DECISIONS | METRICS/DECISIONS entry | 2026-07-28 | HUMAN_QUEUE HQ-07 steps |
| CAND-002 | Replacement candidate cycle after remediation commit | council CTO/CISO seats (G1 caveat) | ready | high | agent | owner commit approval | New CI Windows Store run on the remediation commit → new AppX hash + refreshed screenshots recorded in `store/WINDOWS-VALIDATION.md`; old candidate marked historical; draft package replacement queued into HQ-04 steps | VER id for the new CI run | 2026-07-29 | Commit + push (needs owner approval), then watch the Windows Store workflow |
| COUNCIL-001 | 7-seat market-readiness council + full remediation | user instruction 2026-07-28 | done | high | agent | — | All agent-fixable gaps M1–M10 / D1 / D2 / R1 / R2 closed; every local gate green on the remediated tree | VER-20260729-001 @ working-tree:`246baac`+dirty:`f6edf2f2b6cff045` | 2026-07-29 | — |
| RECON-001 | Working tree vs `origin/main` draft drift | HIST-20260724-001 | done | high | agent | — | Draft committed + remote merged + pushed; single authoritative tree on `main` @ `59787f4` | VER-20260724-006 @ `59787f4` | 2026-07-24 | — |
| DOCS-001 | Documentation consolidation + control system | user instruction 2026-07-24 | done | high | agent | — | Tracker, index, history, verification log, proposals, migration map, archive, validator all green | VER-20260724-001…005 @ working-tree:`4a32b73`+dirty:`451945c517e87554` | 2026-07-24 | — |

Status vocabulary: proposed / todo / ready / in-progress / paused / blocked /
needs-reconciliation / done / verified-stale / superseded / cancelled.

## 5. Active task details

### HQ-04 — Certification then publication (blocked, highest risk)

- Unblock condition: HQ-01 truthful IARC saved + HQ-02 payout ready + HQ-03
  audience route chosen + CAND-002 replacement candidate accepted (the 2026-07-29
  remediation changed app bytes, so the previously accepted AppX is historical).
- Hard rules: never replace the accepted AppX with artifact 8316167277 or
  8613344727; manual hold stays until every gate passes; certification failure →
  preserve report, fix narrow cause, new evidence chain if bytes change (never
  weaken truthful disclosure). The hash guard protects against accidental swaps,
  not deliberate candidate cycles (store/WINDOWS-VALIDATION.md 2026-07-28 note).
- Post-publication playbook: `store/README.md` §"Certification and publication
  playbook" + pre-drafted `store/POST_PUBLICATION_DOC_SWEEP.md` (same-day apply).

## 6. Blockers, risks, active discoveries

| ID | Blocked item | Why | Unblock condition | Affected |
|---|---|---|---|---|
| B1 | Certification + publication | Owner-only legal attestation (IARC) and private payout setup not done; 0/59 owner minutes spent | Owner completes HQ-01, HQ-02 | HQ-04 → HQ-05, WS-REL, WS-REV |
| B2 | Replacement candidate (CAND-002) | Remediated tree uncommitted; CI builds candidates from commits | Owner approves commit + push | HQ-04, screenshots, evidence chain |

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| R1 — zero demand after launch (no demand evidence exists) | high | Bet A falsifier path | 5-day signal gate → pre-built reposition menu RP-1…RP-4 + `store/REPOSITION_KIT.md` (revenue/PLAN.md, D037) | agent+owner |
| R2 — certification failure (runFullTrust, content review) | medium | delay; new candidate cycle | Truthful disclosures; preserve report; narrow fix only | owner (submit), agent (fix) |
| R3 — Partner Center facts stale (last observed 2026-07-14) | medium | decisions on old state | Re-verify live during HQ-01/HQ-02 session before acting; resolve "Submission options: Incomplete" flag (council release seat G4) | owner+agent |
| R4 — remediation drift/loss while uncommitted | medium | rework; candidate confusion | Commit + push promptly on owner approval (single remediated tree, gates green) | owner (approval), agent (commit) |

Resolved 2026-07-24 and moved to history: host-move drift + working-tree
reconciliation (HIST-20260724-001…006), stale node_modules repair
(HIST-20260724-003). CI-observation gap G2 closed 2026-07-28 — main-line CI
observed green through `origin/main` HEAD `246baac` (VER-20260728-001…003).

## 7. Current verification snapshot

| Gate | Ref | Env | Result | Summary | Timestamp | VER |
|---|---|---|---|---|---|---|
| Quality Gate (CI) | `246baac` | CI ubuntu | pass | full quality gate on main HEAD (run 30137666428); earlier pass @ `59787f4` (run 30137481908) | 2026-07-25 | VER-20260728-001/002 |
| Windows Store build (CI) | `59787f4` | CI windows | pass | MSIX + screenshots, 3m25s (run 30137481905); artifact 8613344727 recorded as non-candidate | 2026-07-25 | VER-20260728-003 |
| Local full gate (remediated tree) | working-tree:`246baac`+dirty:`f6edf2f2b6cff045` | local (linux) | pass | lint 0 warnings; typecheck ×2 0 errors; 12 files/46 tests; renderer+electron builds; secrets 189 files; store 276 checks; docs validator PASS | 2026-07-29 | VER-20260729-001 |
| Store certification | accepted AppX `4900f382…` (historical after remediation; CAND-002 pending) | EXT-PC | not submitted | package Validated in draft only | 2026-07-14 | — |
| Installed Windows pass | — | physical Windows | not observed | blocked behind HQ-03/HQ-04 | — | — |

CI observed green through `origin/main` HEAD `246baac` (authenticated gh CLI,
2026-07-28); gap G2 closed. Every main-line commit has a green Quality Gate,
including `e0fc9e0` (run 29404177408) and `0ff209e` (run 29404066796). The
newest MSIX artifact (8613344727) is verification output, not the accepted
candidate — see store/WINDOWS-VALIDATION.md.

## 8. Environment and release state

| Surface | Ref / version | State | Last verified | Evidence | Drift |
|---|---|---|---|---|---|
| Working tree | `246baac` + remediation diff (31 files, +1180/−273) | dirty — remediation complete, gates green, uncommitted | 2026-07-29 | git status, VER-20260729-001 | `node_modules` rebuilt for Linux; Electron binary pending script approval — packaging unverified here |
| Local `cycle-2-shipped` | `246baac` | synced with `origin/main` | 2026-07-28 | git | — |
| Local `main` | `c2b1fc2` | stale, far behind | 2026-07-24 | git | stale (PROP-003) |
| `origin/main` | `246baac` | current | 2026-07-28 | git + gh run list | — |
| CI | Quality Gate 30137666428 @ `246baac`; MSIX 30137481905 @ `59787f4` | green through `origin/main` HEAD | 2026-07-25, observed 2026-07-28 | VER-20260728-001…003 | — |
| Partner Center | Submission 1, package Validated, manual hold | draft; not submitted | 2026-07-14 (stale) | HIST-20260714-003 | G3 |
| Microsoft Store live | — | does not exist | — | — | no listing |
| Landing host | — | not deployed | — | landing/README.md | PROP-004 (HQ-06 proposes certification-time deploy) |

Implemented ≠ committed ≠ pushed ≠ tagged ≠ built ≠ submitted ≠ certified ≠
published ≠ live-verified. The only tag is `v1.0.0` (2026-06-11); no `v1.1.0`
tag exists because tags trigger the Release Build and the Store path is manual.

## 9. Recently completed

| Date | Item | Task | Verification | History |
|---|---|---|---|---|
| 2026-07-29 | 7-seat market-readiness council (CTO/CISO/CPO/CMO/release/legal/CFO) + full remediation of every agent-fixable gap: local-day boundary, atomic toggles, IPC-trust tests, packaged-harness gate, editable decompose, task editing, onboarding budget step, pre-consent erase, nudges default off + disclosures, crisis-plan auto-save, forced-colors focus, error boundary, About diagnostics, Day-15 gate + honest money model, reposition kit, launch targets, doc sweep, notices CI | COUNCIL-001 | VER-20260729-001 (+ VER-20260728-004/005) | — |
| 2026-07-28 | CI observed green through `origin/main` `246baac` (G2 closed); newest MSIX artifact recorded as non-candidate; post-publication doc sweep pre-drafted; third-party-notices freshness CI-enforced | market-readiness remediation D2 (council) | VER-20260728-001…005 | — |
| 2026-07-24 | Working-tree draft reconciled with `origin/main`; pushed to `main` | RECON-001 | VER-20260724-006 | HIST-20260724-004…006 |
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
- PROP-004 landing deployment — sequencing amendment proposed: deploy at
  certification-submit time, not post-publication (HQ-06, D039)
- PROP-005 Bet B Electron kit (L, conditional — revenue/OPPORTUNITIES.md A4.6;
  either/or vs 60-min queue budget in D038)

## 11. Next recommended actions

1. **Owner:** commit decision on the remediated tree (unblocks CAND-002), then
   HQ-01 manual IARC retake and HQ-02 payout readiness (queue: 59 min total,
   `revenue/HUMAN_QUEUE.md`).
2. **Agent (after commit/push):** CAND-002 — observe the Windows Store CI run on
   the remediation commit, record the new AppX hash + refreshed screenshots in
   `store/WINDOWS-VALIDATION.md`, mark the old candidate historical, queue the
   draft-package swap into HQ-04 steps. Screenshot refresh is required:
   onboarding, tasks, and settings UI changed.
3. **Agent (before any packaging on this host):** restore the Electron binary
   (`npm approve-scripts` for the 3 pending install scripts) — tests/typecheck
   are green; `npm run dev` / packaging are not (VER-20260724-005 notes).
4. **After publication only:** execute `store/README.md` "Certification and
   publication playbook", applying `store/POST_PUBLICATION_DOC_SWEEP.md`
   same-day, then HQ-06 landing deploy and HQ-05 launch batch.

## 12. Ledger and archive links

- History: [docs/project/REPO_HISTORY.md](docs/project/REPO_HISTORY.md) (+ `history/commit-index.tsv`)
- Verification: [docs/project/VERIFICATION_LOG.md](docs/project/VERIFICATION_LOG.md)
- Decisions: [revenue/DECISIONS.md](revenue/DECISIONS.md)
- Proposals: [docs/project/PROPOSALS.md](docs/project/PROPOSALS.md)
- Docs index: [docs/project/DOCS_INDEX.md](docs/project/DOCS_INDEX.md)
- Migration map: [docs/project/MIGRATION_MAP.md](docs/project/MIGRATION_MAP.md)
- Archive: [docs/project/archive/](docs/project/archive/)
- Monetization evidence: [revenue/METRICS.md](revenue/METRICS.md)
