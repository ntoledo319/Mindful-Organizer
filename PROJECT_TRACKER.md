# Ample — Project Tracker

- **Schema:** project-tracker/v1 (2026-07-24)
- **Last updated:** 2026-08-25T11:33Z (AMPLE-001 local gate green; canonical commit/CI pending)
- **Workspace root:** `/home/nick/Development/active/mindful_organizer` (REPO-01)
- **Branch / HEAD:** checked-out `main`, `origin/main`, and `origin/feature/store-candidate-cand002` all at `c0eb360`; local `main` was fast-forwarded from stale `c2b1fc2`
- **Working tree:** active dirty at `c0eb360` — exact identity, pipeline fixes, listing copy, tests, and state reconciliation pass the complete local gate; commit/push pending
- **Operating mode:** RELEASE PREP / CI
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
| Product state | Source is Ample; Partner Center product `9PLRSZZMFPJH` retains exact package identity `ToledoTechnologies.Hearth`, now recorded and verified. Only Hearth is currently reserved; no fresh candidate exists yet and nothing is submitted/certified/published | 2026-08-25 | VER-20260825-001 |
| Default-branch HEAD (`origin/main`) | `c0eb360`; checked-out local `main` was fast-forwarded to match, and the historical feature ref also matches | 2026-08-25 | live `git` + `gh`, VER-20260825-002 |
| Live release | none — not submitted, certified, published, or purchasable | 2026-07-14 | HIST-20260714-003 |
| Current candidate | none. CAND-002 (`a5d2cf36…b18f`) and every other existing MSIX are historical Hearth artifacts and never-submit after the manifest rename | 2026-08-19 | D041; store/WINDOWS-VALIDATION.md |
| Latest CI verification | **Fail** at `c0eb360`: Quality 32310869115/32310866310 (stale notices); Windows 32310869046/32310866359 (old screenshot env), zero artifacts. Committed identity checker also incorrectly accepted `identityVerified:false` | 2026-08-19 | VER-20260819-001 |
| Latest local verification | full pre-push gate green with observed identity: strict preflight, lint 0, typecheck ×2, 14 files/49 tests, vite build, secrets 197, store 277, docs PASS, licenses 54, audit 0, deterministic generated assets | 2026-08-25 | VER-20260825-002 |
| Local test environment | `better-sqlite3` alternates between node and Electron ABIs depending on whether `electron-builder` last ran. In the Electron state 16/46 tests fail with `NODE_MODULE_VERSION` mismatch — environmental, CI unaffected. `npm rebuild better-sqlite3` restores `npm test` | 2026-08-07 | VER-20260807-001 |
| Candidate package | none; no Ample AppX or screenshots artifact exists. The staged CAND-002 kit is historical and never-submit | 2026-08-19 | VER-20260819-001; store/WINDOWS-VALIDATION.md |
| Collected revenue | $0.00; gap $4,000.00; 0 live listings; Day-15 gate assessment executed (D035) | 2026-07-28 | revenue/METRICS.md |
| Major open blocker | Package identity gate resolved. AMPLE-001 is in progress; separate owner-only Ample display-name reservation, IARC, payout, submission, and publication gates remain | 2026-08-25 | VER-20260825-001; revenue/HUMAN_QUEUE.md |
| Next recommended action | Commit and push canonical `main`, watch exact-SHA CI, hash the AppX, update evidence, and stage only that run's package + screenshots | 2026-08-25 | section 11; AMPLE-001 |

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
| Decisions (D001–D044) | `revenue/DECISIONS.md` |
| Repository/release history | `docs/project/REPO_HISTORY.md` |
| Verification events | `docs/project/VERIFICATION_LOG.md` |
| Documentation map | `docs/project/DOCS_INDEX.md` |
| Unapproved scope | `docs/project/PROPOSALS.md` |

## 3. Workstream index

| ID | Workstream | Derived status | Tasks (ready/blocked/other) | Last verified ref | Active tasks |
|---|---|---|---|---|---|
| WS-REL | Microsoft Store release (Bet A, $14.99) | blocked — fresh candidate in progress; Ample name reservation + owner gates remain | 4 ready, 4 blocked, 1 in-progress | `c0eb360` dirty + VER-20260825-002 | HQ-01…HQ-07, AMPLE-001 |
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
| HQ-04 | Submit for certification; publish deliberately | revenue/HUMAN_QUEUE.md | blocked | critical | human | HQ-01, HQ-02, HQ-03 route choice, AMPLE-001 | Certification report preserved; `Publish now` only after all gates; signed-out purchase verified | Certification result + live URL in METRICS | 2026-08-19 | Unblock = owner gates + fresh Ample candidate accepted |
| HQ-05 | Approve and send first audience batch | store/LAUNCH_KIT.md + store/LAUNCH_TARGETS.md | blocked | medium | human | live purchasable page | Owner-posted launch batch with URLs + timestamps in METRICS | METRICS entry | 2026-07-28 | Unblock = signed-out checkout verification; destinations pre-vetted in LAUNCH_TARGETS.md |
| HQ-06 | Approve PROP-004 sequencing + deploy landing at certification time | revenue/HUMAN_QUEUE.md | ready | medium | human | owner approval of amended PROP-004 | Public prelaunch URL resolves signed-out; host + URL + timestamp in METRICS | METRICS entry | 2026-07-28 | HUMAN_QUEUE HQ-06 steps (host TOS re-check first — D007) |
| HQ-07 | Trademark clearance for "Ample" (or informed risk acceptance) | revenue/HUMAN_QUEUE.md | ready | low | human | — | USPTO + Store search note in METRICS, or explicit risk acceptance in DECISIONS | METRICS/DECISIONS entry | 2026-08-19 | HUMAN_QUEUE HQ-07 steps |
| CAND-002 | Historical Hearth replacement candidate | D040/D041 | superseded | high | agent | — | Replaced by AMPLE-001 after rename; never submit its AppX | VER-20260807-001 → AMPLE-001 | 2026-08-19 | Historical evidence only |
| AMPLE-001 | First exact Ample Store candidate | user instruction 2026-08-19 | in-progress | critical | agent | HQ-00 done | Verified identity; full local gate; one canonical push; exact-SHA green Windows run; AppX SHA-256 + screenshots recorded and staged | VER-20260825-001/002 + new CI VER + hash | 2026-08-25 | Commit/push canonical `main`; never use CAND-002 |
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
| ~~B3~~ | ~~First Ample candidate identity~~ | **Resolved 2026-08-25:** Partner Center product `9PLRSZZMFPJH` reports exact identity `ToledoTechnologies.Hearth`; repository now has `identityVerified:true` | — | AMPLE-001 package/CI work remains in progress |
| ~~B2~~ | ~~Replacement candidate (CAND-002)~~ | **Resolved 2026-08-02…08-04** — the tree was committed (`fe0fc4a`…`270e650`) and CI built the candidate. This row survived five days after its own unblock condition was met; removed from active blockers 2026-08-07 | — | — |

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| R1 — zero demand after launch (no demand evidence exists) | high | Bet A falsifier path | 5-day signal gate → pre-built reposition menu RP-1…RP-4 + `store/REPOSITION_KIT.md` (revenue/PLAN.md, D037) | agent+owner |
| R2 — certification failure (runFullTrust, content review) | medium | delay; new candidate cycle | Truthful disclosures; preserve report; narrow fix only | owner (submit), agent (fix) |
| R3 — Partner Center listing facts partly stale | **medium** | decisions on old listing fields | Identity, app names, and submission overview were reobserved 2026-08-25; detailed Ample listing fields remain repository-only until the owner saves them | owner+agent |
| ~~R4~~ | — | — | **Resolved 2026-08-04** — remediation is committed and landed. Row retired 2026-08-07 | — |
| R5 — wrong MSIX submitted | high | historical Hearth bytes certified as Ample | No current package is valid. CAND-002, its staged kit, and six later Hearth MSIX artifacts are explicitly never-submit; future staging binds exact SHA/run/hash | agent+owner |
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
| Quality Gate (CI) | `c0eb360` | CI ubuntu | fail | stale renamed THIRD_PARTY_NOTICES; runs 32310869115/32310866310 | 2026-08-19 | VER-20260819-001 |
| Windows Store build (CI) | `c0eb360` | CI windows | fail | screenshot launcher used obsolete `HEARTH_*`; runs 32310869046/32310866359; zero artifacts | 2026-08-19 | VER-20260819-001 |
| Full local candidate preflight | working-tree:`c0eb360`+dirty (exact fingerprint in log) | local (linux) | pass | strict identity preflight; lint 0; typecheck ×2; 14 files/49 tests; vite build; secrets 197; store 277; docs PASS; licenses 54; audit 0 | 2026-08-25 | VER-20260825-002 |
| Partner Center identity | product `9PLRSZZMFPJH` | EXT-PC | pass | exact `ToledoTechnologies.Hearth`; only Hearth reserved; draft/not submitted | 2026-08-25 | VER-20260825-001 |
| Store candidate/certification | — | CI / EXT-PC | in progress | no fresh package yet; identity gate cleared for AMPLE-001 | 2026-08-25 | VER-20260825-001 |
| Installed Windows pass | — | physical Windows | not observed | blocked behind HQ-03/HQ-04 | — | — |

Historical green runs remain valid only for their exact Hearth refs. Current
`c0eb360` CI is red and produced no Ample artifacts; see
store/WINDOWS-VALIDATION.md.

## 8. Environment and release state

| Surface | Ref / version | State | Last verified | Evidence | Drift |
|---|---|---|---|---|---|
| Working tree | `main` @ `c0eb360` + identity/listing/pipeline/reconciliation diff | active dirty; identity verified and full gate green; canonical commit/push pending | 2026-08-25 | git status, VER-20260825-002 | AMPLE-001 in progress |
| Local `cycle-2-shipped` | `246baac` | stale, 13 behind `origin/main` | 2026-08-19 | git | historical branch |
| Local `main` | `c0eb360` + dirty | checked out; fast-forwarded to `origin/main`; candidate commit pending | 2026-08-25 | git, VER-20260825-002 | active AMPLE-001 tree |
| `origin/main` | `c0eb360` | current Ample source; CI red | 2026-08-19 | git + gh run list | VER-20260819-001 |
| CI | Quality + Windows runs at `c0eb360` | red; zero Ample artifacts | 2026-08-19 | VER-20260819-001 | local fixes unpushed |
| Partner Center | Existing product `9PLRSZZMFPJH`; exact identity `ToledoTechnologies.Hearth`; only Hearth reserved; draft/not submitted | identity/names/overview reobserved; detailed Ample listing fields not saved | 2026-08-25 | VER-20260825-001 | owner must reserve Ample before submission |
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

**AMPLE-001 is in progress. Do not use CAND-002.**

1. **Agent:** commit once, push canonical `main` once, and watch the exact-SHA
   Quality + Windows workflows to completion.
2. **Agent after green CI:** download `ample-msix` and
   `ample-store-screenshots`, hash the contained AppX, append validation records,
   and stage both artifacts plus a hash README under `tmp/`.
3. **Owner later:** reserve Ample, then complete HQ-02 payout, HQ-01 IARC,
   HQ-03/HQ-04 certification and signed-build validation, and deliberate
   publication. Agent does none of those owner-only actions.
4. **After publication only:** execute `store/README.md` "Certification and
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
