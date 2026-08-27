# Ample — Project Tracker

- **Schema:** project-tracker/v1 (2026-07-24)
- **Last updated:** 2026-08-26T20:56-04:00 (post-candidate safety reconciliation; AMPLE-001 unchanged)
- **Workspace root:** `/home/nick/Development/active/mindful_organizer` (REPO-01)
- **Branch / HEAD:** exact candidate source is `3b8d225`; canonical `main` contains documentation-only descendants that cannot change its AppX bytes. Historical remote feature ref remains at `c0eb360`
- **Working tree:** this documentation-only safety close changes no package trigger; the exact ignored kit remains staged under `tmp/AMPLE-001-3b8d225/`
- **Operating mode:** RELEASE EVIDENCE / OWNER GATES
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
| Product state | Source is Ample; Partner Center product `9PLRSZZMFPJH` retains verified identity `ToledoTechnologies.Hearth`. AMPLE-001 now exists and is CI-validated/staged; only Hearth is reserved and nothing is submitted/certified/published | 2026-08-25 | VER-20260825-001/003 |
| Default-branch candidate source | `3b8d225`; this evidence-only close is its descendant and cannot change AppX bytes. Historical remote feature ref remains at `c0eb360` | 2026-08-25 | live `git` + `gh`, VER-20260825-003 |
| Live release | none — not submitted, certified, published, or purchasable | 2026-07-14 | HIST-20260714-003 |
| Current candidate | AMPLE-001 AppX `7d6ca584…61866b`, exact source `3b8d225`, Windows run 32844120483; staged with five exact-SHA screenshots. CAND-002 and all other packages remain never-submit | 2026-08-25 | VER-20260825-003; store/WINDOWS-VALIDATION.md |
| Candidate CI verification | **Pass** at exact `3b8d225`: Quality 32844120492; Windows 32844120483 including package structure/identity, Windows x64 DPAPI lifecycle, renderer smoke, and screenshots | 2026-08-25 | VER-20260825-003 |
| Candidate local verification | full pre-push gate green with observed identity: strict preflight, lint 0, typecheck ×2, 14 files/49 tests, vite build, secrets 197, store 277, docs PASS, licenses 54, audit 0, deterministic generated assets | 2026-08-25 | VER-20260825-002 |
| Documentation-close local verification | full non-packaging gate green: lint 0, typecheck ×2, 14 files/49 tests, renderer 764 modules + Electron bundles, secrets 197, Store 277, docs PASS, diff clean | 2026-08-26 | VER-20260826-001 |
| Local test environment | `better-sqlite3` alternates between node and Electron ABIs depending on whether `electron-builder` last ran. In the Electron state 16/46 tests fail with `NODE_MODULE_VERSION` mismatch — environmental, CI unaffected. `npm rebuild better-sqlite3` restores `npm test` | 2026-08-07 | VER-20260807-001 |
| Candidate package | `Ample 1.1.0.appx`, 175489305 bytes, SHA-256 `7d6ca584a8cee92497217ab48fbd04153f32c8f8746b4cd19135d709aa61866b`; artifact 9561731052; kit `tmp/AMPLE-001-3b8d225/` | 2026-08-25 | VER-20260825-003 |
| Collected revenue | $0.00; gap $4,000.00; 0 live listings; Day-15 gate assessment executed (D035) | 2026-07-28 | revenue/METRICS.md |
| Major open blocker | All agent-side candidate work is complete. The ≤60-minute owner path exists only if the owner independently chooses D047/HQ-07's one-minute risk path, records it inside the reservation batch, and defers HQ-05/HQ-06; otherwise the queue exceeds the ceiling. Remaining reservation, IARC, payout/tax, submission, certification, signed-build review, and publication gates are owner-only | 2026-08-26 | D047; VER-20260825-003; revenue/HUMAN_QUEUE.md |
| Next recommended action | Owner decides whether to use D047's conditional ≤60-minute path; this is not an agent recommendation. Only after that decision: resolve HQ-07, reserve Ample, and begin the remaining owner gates | 2026-08-26 | section 11; revenue/HUMAN_QUEUE.md |

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
| Decisions (D001–D047) | `revenue/DECISIONS.md` |
| Repository/release history | `docs/project/REPO_HISTORY.md` |
| Verification events | `docs/project/VERIFICATION_LOG.md` |
| Documentation map | `docs/project/DOCS_INDEX.md` |
| Unapproved scope | `docs/project/PROPOSALS.md` |

## 3. Workstream index

| ID | Workstream | Derived status | Tasks (ready/blocked/other) | Last verified ref | Active tasks |
|---|---|---|---|---|---|
| WS-REL | Microsoft Store release (Bet A, $14.99) | blocked — exact candidate done; Ample reservation/owner gates remain; ≤60-minute path is conditional on D047 | 4 ready, 3 blocked, 1 done | `3b8d225` + VER-20260825-003 | HQ-01…HQ-07, D047 |
| WS-REV | Monetization portfolio ($4,000 / Day 28) | blocked — Bet A = WS-REL; Day-15 gate executed (D035); reposition menu + kit ready; Bet B either/or pending owner (D038) | 0 active, 1 proposed | revenue/METRICS.md 2026-07-28 | — |
| WS-DOCS | Documentation control system | done 2026-07-24 (on public main @ `59787f4`) | 2 done | VER-20260724-001…006 | — |
| WS-READY | Market-readiness council + remediation | done; landed before rename | 1 done | VER-20260804-001 | — |

## 4. Active task table

| Task | Title | Source | Status | Priority | Owner | Deps | Acceptance | Verification | Last touched | Resume from |
|---|---|---|---|---|---|---|---|---|---|---|
| HQ-00 | Provide observed Package/Identity/Name | revenue/HUMAN_QUEUE.md | done | critical | agent (owner-authorized) | — | Exact Partner Center string observed; no guess | VER-20260825-001; `identityVerified:true` | 2026-08-25 | — |
| HQ-01 | Manual IARC retake with legal attestation | revenue/HUMAN_QUEUE.md | ready | critical | human | — | Truthful ratings saved; date + regional results in METRICS | METRICS entry | 2026-07-15 | HUMAN_QUEUE HQ-01 steps + Partner Center link |
| HQ-02 | Seller/tax/payout readiness (+ threshold/first-payout-date note) | revenue/HUMAN_QUEUE.md | ready | critical | human | — | Payout-ready boolean + non-sensitive note in METRICS | METRICS entry | 2026-07-28 | HUMAN_QUEUE HQ-02 steps; allow 48h validation |
| HQ-03 | Choose test route; Store-signed Windows pass | revenue/HUMAN_QUEUE.md | blocked | high | human | HQ-04 (certification); route-choice sub-step is ready now | `store/WINDOWS-VALIDATION.md` + accessibility matrix completed on signed build, fictional data (incl. forced-colors focus + 200% text-scaling line items, council CPO G6) | Validation record (build, route, pass/fail, footprint, date) | 2026-07-29 | Unblock = HQ-04 certification complete; decide Public→Private audience route beforehand |
| HQ-04 | Submit for certification; publish deliberately | revenue/HUMAN_QUEUE.md | blocked | critical | human | HQ-01, HQ-02, HQ-03 route choice, HQ-07 decision, Ample reservation, AMPLE-001, ≤60-minute plan | Certification report preserved; `Publish now` only after all gates; signed-out purchase verified | Certification result + live URL in METRICS | 2026-08-26 | Unblock = owner gates + exact candidate + compliant owner-time path |
| HQ-05 | Approve and send first audience batch | store/LAUNCH_KIT.md + store/LAUNCH_TARGETS.md | blocked | medium | human | live purchasable page | Owner-posted launch batch with URLs + timestamps in METRICS | METRICS entry | 2026-07-28 | Unblock = signed-out checkout verification; destinations pre-vetted in LAUNCH_TARGETS.md |
| HQ-06 | Approve PROP-004 sequencing + deploy landing at certification time | revenue/HUMAN_QUEUE.md | ready | medium | human | owner approval of amended PROP-004 | Public prelaunch URL resolves signed-out; host + URL + timestamp in METRICS | METRICS entry | 2026-07-28 | HUMAN_QUEUE HQ-06 steps (host TOS re-check first — D007) |
| HQ-07 | Trademark clearance for "Ample" (or informed risk acceptance) | revenue/HUMAN_QUEUE.md | ready | low | human | — | USPTO + Store search note in METRICS, or explicit risk acceptance in DECISIONS | METRICS/DECISIONS entry | 2026-08-19 | HUMAN_QUEUE HQ-07 steps |
| CAND-002 | Historical Hearth replacement candidate | D040/D041 | superseded | high | agent | — | Replaced by AMPLE-001 after rename; never submit its AppX | VER-20260807-001 → AMPLE-001 | 2026-08-19 | Historical evidence only |
| AMPLE-001 | First exact Ample Store candidate | user instruction 2026-08-19 | done | critical | agent | HQ-00 done | Verified identity; full local gate; one canonical push; exact-SHA green Windows run; AppX SHA-256 + screenshots recorded and staged | VER-20260825-001…003 @ `3b8d225`; hash `7d6ca584…61866b` | 2026-08-25 | — |
| COUNCIL-001 | 7-seat market-readiness council + full remediation | user instruction 2026-07-28 | done | high | agent | — | All agent-fixable gaps M1–M10 / D1 / D2 / R1 / R2 closed; every local gate green on the remediated tree | VER-20260729-001 @ working-tree:`246baac`+dirty:`f6edf2f2b6cff045` | 2026-07-29 | — |
| RECON-001 | Working tree vs `origin/main` draft drift | HIST-20260724-001 | done | high | agent | — | Draft committed + remote merged + pushed; single authoritative tree on `main` @ `59787f4` | VER-20260724-006 @ `59787f4` | 2026-07-24 | — |
| DOCS-001 | Documentation consolidation + control system | user instruction 2026-07-24 | done | high | agent | — | Tracker, index, history, verification log, proposals, migration map, archive, validator all green | VER-20260724-001…005 @ working-tree:`4a32b73`+dirty:`451945c517e87554` | 2026-07-24 | — |

Status vocabulary: proposed / todo / ready / in-progress / paused / blocked /
needs-reconciliation / done / verified-stale / superseded / cancelled.

## 5. Active task details

### HQ-04 — Certification then publication (blocked, highest risk)

- Unblock condition: HQ-01 truthful IARC saved + HQ-02 payout ready + HQ-03
  audience route chosen + AMPLE-001 exact candidate accepted. Every Hearth AppX
  is historical after the rename.
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
| B1 | Certification + publication | Owner-only legal attestation (IARC) and private payout setup not done | Owner completes HQ-01, HQ-02 | HQ-04 → HQ-05, WS-REL, WS-REV |
| B4 | Owner-action batch | Full current queue is 79/70 minutes after exact-CI/listing scope corrections; the only ≤60-minute full-run path is 59 remaining + conservatively counted HQ-00 minute | Owner independently chooses D047's one-minute risk path, batches its record with reservation, and defers HQ-05/HQ-06; otherwise further truthful scope reduction is required | HQ-01…HQ-07, WS-REL, WS-REV |
| ~~B3~~ | ~~First Ample candidate identity~~ | **Resolved 2026-08-25:** Partner Center product `9PLRSZZMFPJH` reports exact identity `ToledoTechnologies.Hearth`; repository now has `identityVerified:true` | — | AMPLE-001 completed at VER-20260825-003 |
| ~~B2~~ | ~~Replacement candidate (CAND-002)~~ | **Resolved 2026-08-02…08-04** — the tree was committed (`fe0fc4a`…`270e650`) and CI built the candidate. This row survived five days after its own unblock condition was met; removed from active blockers 2026-08-07 | — | — |

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| R1 — zero demand after launch (no demand evidence exists) | high | Bet A falsifier path | 5-day signal gate → pre-built reposition menu RP-1…RP-4 + `store/REPOSITION_KIT.md` (revenue/PLAN.md, D037) | agent+owner |
| R2 — certification failure (runFullTrust, content review) | medium | delay; new candidate cycle | Truthful disclosures; preserve report; narrow fix only | owner (submit), agent (fix) |
| R3 — Partner Center listing facts partly stale | **medium** | decisions on old listing fields | Identity, app names, and submission overview were reobserved 2026-08-25; detailed Ample listing fields remain repository-only until the owner saves them | owner+agent |
| ~~R4~~ | — | — | **Resolved 2026-08-04** — remediation is committed and landed. Row retired 2026-08-07 | — |
| R5 — wrong MSIX submitted | high | historical Hearth bytes certified as Ample | Only AMPLE-001 `7d6ca584…61866b` from run 32844120483 is current. CAND-002, its staged kit, and all other MSIX artifacts remain explicitly never-submit | agent+owner |
| R6 — HQ-03 has no verified Windows machine (new 2026-08-07) | **low** (downgraded same day) | delays post-certification validation only | **Corrected:** HQ-03 depends on HQ-04, not the reverse — the Microsoft-signed build does not exist until after certification, so this never blocked submission. CI `windows-store.yml` already exercises the packaged AppX on `windows-latest` (DPAPI lifecycle matrix + renderer smoke + screenshots). Residual need is a human ear on Narrator | owner (post-certification) |
| ~~R8 — "Hearth" collision~~ | resolved by rename 2026-08-19 | forced candidate reset | Historical analysis retained in `revenue/NAME-RISK-2026-08-07.md` | owner+agent |
| R9 — Ample display name not reserved | high for submission | Listing cannot honestly use Ample until owner reserves it; package identity must not be renamed again | Build with observed `ToledoTechnologies.Hearth`; owner reserves Ample before submission | owner+agent |
| R7 — session-to-session document drift (new 2026-08-07) | **high** | agents act on stale state; owner acts on wrong hash/commit | Re-derive the resume point from `git`/`gh` every session rather than trusting the prior summary. This risk has now materialised three times (RECON-001, B2/R4 survival, the 08-04 resume point) | agent |

Resolved 2026-07-24 and moved to history: host-move drift + working-tree
reconciliation (HIST-20260724-001…006), stale node_modules repair
(HIST-20260724-003). CI-observation gap G2 closed 2026-07-28 — main-line CI
observed green through `origin/main` HEAD `246baac` (VER-20260728-001…003).

## 7. Current verification snapshot

| Gate | Ref | Env | Result | Summary | Timestamp | VER |
|---|---|---|---|---|---|---|
| Candidate Quality Gate (CI) | `3b8d225` | CI ubuntu | pass | full gate; run 32844120492 | 2026-08-25 | VER-20260825-003 |
| Windows Store build (CI) | `3b8d225` | CI windows | pass | run 32844120483; artifact 9561731052; AppX `7d6ca584…61866b`; screenshots 9561704379 | 2026-08-25 | VER-20260825-003 |
| Documentation safety close | working-tree:`13bdea2`+dirty (exact fingerprint in log) | local linux | pass | lint; typecheck ×2; 14 files/49 tests; vite + Electron bundles; secrets 197; Store 277; docs PASS; diff clean | 2026-08-26 | VER-20260826-001 |
| Full local candidate preflight | working-tree:`c0eb360`+dirty (exact fingerprint in log) | local (linux) | pass | strict identity preflight; lint 0; typecheck ×2; 14 files/49 tests; vite build; secrets 197; store 277; docs PASS; licenses 54; audit 0 | 2026-08-25 | VER-20260825-002 |
| Partner Center identity | product `9PLRSZZMFPJH` | EXT-PC | pass | exact `ToledoTechnologies.Hearth`; only Hearth reserved; draft/not submitted | 2026-08-25 | VER-20260825-001 |
| Store candidate/certification | AMPLE-001 `7d6ca584…61866b` | CI / EXT-PC | candidate pass / certification not observed | exact candidate staged; no Partner Center upload, submission, certification, or publication | 2026-08-25 | VER-20260825-003 |
| Installed Windows pass | — | physical Windows | not observed | blocked behind HQ-03/HQ-04 | — | — |

Historical green runs remain valid only for their exact Hearth refs. The prior
`c0eb360` failure remains historical; current exact candidate evidence is bound
only to `3b8d225` and `7d6ca584…61866b`. See store/WINDOWS-VALIDATION.md.

## 8. Environment and release state

| Surface | Ref / version | State | Last verified | Evidence | Drift |
|---|---|---|---|---|---|
| Working tree | canonical `main` over candidate source `3b8d225` | documentation-only safety reconciliation; exact kit staged in ignored `tmp/` | 2026-08-26 | git status, VER-20260826-001 | no candidate drift |
| Local `cycle-2-shipped` | `246baac` | stale; behind current `main` | 2026-08-26 | git | historical branch |
| Local `main` | documentation-only descendant of `3b8d225` | canonical checked-out branch; candidate source unchanged | 2026-08-26 | git, VER-20260826-001 | none |
| `origin/main` | documentation-only descendant of `3b8d225` | exact Ample candidate source remains `3b8d225`; candidate CI green | 2026-08-26 | git + exact-SHA gh runs | VER-20260825-003 |
| CI | candidate Quality 32844120492 + Windows 32844120483; evidence-close Quality 32845727178 | green; candidate artifacts 9561731052 / 9561704379 | 2026-08-26 | VER-20260825-003; VER-20260826-001 | none |
| Partner Center | Existing product `9PLRSZZMFPJH`; exact identity `ToledoTechnologies.Hearth`; only Hearth reserved; draft/not submitted | identity/names/overview reobserved; detailed Ample listing fields not saved | 2026-08-25 | VER-20260825-001 | owner must reserve Ample before submission |
| Microsoft Store live | — | does not exist | — | — | no listing |
| Landing host | — | not deployed | — | landing/README.md | PROP-004 (HQ-06 proposes certification-time deploy) |

Implemented ≠ committed ≠ pushed ≠ tagged ≠ built ≠ submitted ≠ certified ≠
published ≠ live-verified. The only tag is `v1.0.0` (2026-06-11); no `v1.1.0`
tag exists because tags trigger the Release Build and the Store path is manual.

## 9. Recently completed

| Date | Item | Task | Verification | History |
|---|---|---|---|---|
| 2026-08-26 | Post-candidate safety reconciliation: neutralized historical CAND-002 staging instructions, corrected current Store/listing boundaries, and propagated platform-first launch copy without touching a package trigger | documentation safety close | VER-20260826-001 | HIST-20260826-001 |
| 2026-08-25 | First exact Ample candidate: observed identity, full local gate, exact-SHA green CI, independent AppX/screenshot hashes, and staged kit | AMPLE-001 | VER-20260825-001…003 @ `3b8d225` | HIST-20260825-001…003 |
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

**AMPLE-001 is done. Do not use CAND-002 or any artifact except the exact hash
recorded for AMPLE-001.**

1. **Owner:** decide whether to use D047's conditional 60-minute path. It
   requires independently choosing HQ-07's one-minute risk path, recording it
   inside the Ample reservation batch, and deferring HQ-05/HQ-06; this is not an
   agent recommendation to waive screening. If chosen, verify the staged AppX
   hash and complete the remaining owner gates. Otherwise reduce owner scope
   truthfully before starting. Agent does none of those actions.
2. **After publication only:** execute `store/README.md` "Certification and
   publication playbook", applying `store/POST_PUBLICATION_DOC_SWEEP.md`
   same-day.

## 12. Ledger and archive links

- History: [docs/project/REPO_HISTORY.md](docs/project/REPO_HISTORY.md) (+ `history/commit-index.tsv`)
- Verification: [docs/project/VERIFICATION_LOG.md](docs/project/VERIFICATION_LOG.md)
- Decisions: [revenue/DECISIONS.md](revenue/DECISIONS.md)
- Proposals: [docs/project/PROPOSALS.md](docs/project/PROPOSALS.md)
- Docs index: [docs/project/DOCS_INDEX.md](docs/project/DOCS_INDEX.md)
- Migration map: [docs/project/MIGRATION_MAP.md](docs/project/MIGRATION_MAP.md)
- Archive: [docs/project/archive/](docs/project/archive/)
- Monetization evidence: [revenue/METRICS.md](revenue/METRICS.md)
