# Paulatim — Project Tracker

- **Schema:** project-tracker/v1 (2026-07-24)
- **Last updated:** 2026-08-31 (PAULATIM-001 certified and publicly purchasable; post-publication validation/signal monitoring active)
- **Workspace root:** `/home/nick/Development/active/mindful_organizer` (REPO-01)
- **Branch / HEAD:** `main` is an evidence-only successor to exact documentation-truth commit `889100c76abe3e862bdfc6e2b0164f2db174e7f5` (tree `08c0ea17eedd143e82d00dd3a6f7ee6ed5c30fe1`), itself a documentation-only descendant of PAULATIM-001 source `f2d2a417`; re-derive the mutable successor SHA from `git`
- **Working tree:** clean after the documentation-truth evidence close; exact certified package bytes remain unchanged
- **Operating mode:** LIVE / POST-PUBLICATION VALIDATION AND SIGNAL MONITORING
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
| Product state | Paulatim 1.1.1 is Microsoft-certified and exposed with an active $14.99 USD purchase action in the United States Store market at `https://apps.microsoft.com/detail/9PLRSZZMFPJH` | 2026-08-31 | VER-20260831-001; D051/D052 |
| Default-branch candidate source | PAULATIM-001 source `f2d2a4177fcb05d5b24405c598d0eb9b9d7f01e6`; tree `320490a5cfc1d5e409e8ce0ea2fb05147dc97e4d` | 2026-08-28 | VER-20260828-003 |
| Live release | Paulatim 1.1.1 / product `9PLRSZZMFPJH`; signed-out page and live catalog verified | 2026-08-31 | VER-20260831-001 |
| Current candidate | PAULATIM-001: `Paulatim 1.1.1.appx`, 175,489,702 bytes, SHA-256 `af8b458149d4c00de7f02d4f4c73a4b786d14dbbd391b0db7e1750d4bf4b5146`. AMPLE-001, CAND-002, and every other package are historical/never-submit | 2026-08-28 | VER-20260828-003; store/WINDOWS-VALIDATION.md |
| Candidate CI verification | Quality 33169087812 and Windows 33169087811 passed on exact source `f2d2a417`; artifacts 9684903207 / 9684887490 independently verified | 2026-08-28 | VER-20260828-003 |
| Candidate local verification | full gate green: identity preflights; lint; typecheck ×2; 15 files/52 tests; renderer 764 modules + Electron bundles; secrets 199; Store 277; docs PASS; notices 54; audit 0; deterministic assets; diff clean | 2026-08-28 | VER-20260828-002; dirty fingerprint in log |
| Documentation-truth-audit local verification | full non-packaging gate green: identity strict; lint 0; typecheck ×2; 15 files/52 tests; renderer 764 modules + Electron bundles; secrets 199; Store 274; docs PASS; notices 54; audit 0; diff clean; no Windows-trigger path | 2026-08-31 | VER-20260831-006; exact dirty fingerprint in log |
| Documentation-truth-audit Quality | exact commit `889100c`, tree `08c0ea17`; Quality 33451146452 green; no Windows Store run | 2026-08-31 | VER-20260831-007 |
| Local test environment | `better-sqlite3` alternates between node and Electron ABIs depending on whether `electron-builder` last ran. In the Electron state 16/46 tests fail with `NODE_MODULE_VERSION` mismatch — environmental, CI unaffected. `npm rebuild better-sqlite3` restores `npm test` | 2026-08-07 | VER-20260807-001 |
| Candidate package | Exact kit: `tmp/PAULATIM-001-f2d2a41/`; AppX hash `af8b4581…b5146`; screenshot ZIP hash `a4bc6785…45e50`; these are evidence for the sole certified/public package and must not be re-uploaded | 2026-08-31 | VER-20260828-003/004; VER-20260831-001 |
| Collected revenue | $0.00; gap $4,000.00; 1 live purchasable listing; views/acquisitions/purchases/payouts unobserved; five-day signal clock began 2026-08-31 | 2026-08-31 | revenue/METRICS.md |
| Major open operational gaps | Live `appWebsiteUrl` and `SupportUri` both point to the generic studio site; four Store-copy surfaces use ambiguous account wording; HQ-03 physical-Windows accessibility remains unobserved | 2026-08-31 | VER-20260831-001; D052; section 11 |
| Next recommended action | Complete HQ-03 and monitor first external signal through the 2026-09-05 gate; HQ-08 requires fresh owner authority to reconcile Store links and account wording before outreach | 2026-08-31 | D051/D052; section 11 |

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
| Decisions (D001–D052) | `revenue/DECISIONS.md` |
| Repository/release history | `docs/project/REPO_HISTORY.md` |
| Verification events | `docs/project/VERIFICATION_LOG.md` |
| Documentation map | `docs/project/DOCS_INDEX.md` |
| Unapproved scope | `docs/project/PROPOSALS.md` |

## 3. Workstream index

| ID | Workstream | Derived status | Tasks (ready/blocked/other) | Last verified ref | Active tasks |
|---|---|---|---|---|---|
| WS-REL | Microsoft Store release (Bet A, $14.99) | live in U.S. market — exact Paulatim release publicly purchasable; residual HQ-03 and owner-controlled Store-link/account-copy reconciliation open | 1 ready validation, 2 optional/post-live tasks, 1 blocked Store-listing correction | VER-20260831-001; D052 | HQ-03, HQ-05, HQ-06, HQ-08 |
| WS-REV | Monetization portfolio ($4,000 / Day 28) | active — Bet A live; five-day signal gate due 2026-09-05; Bet B remains conditional (D038) | 1 active, 1 proposed | revenue/METRICS.md 2026-08-31 | WS-REL |
| WS-DOCS | Documentation control system | done 2026-07-24 (on public main @ `59787f4`) | 2 done | VER-20260724-001…006 | — |
| WS-READY | Market-readiness council + remediation | done; landed before rename | 1 done | VER-20260804-001 | — |

## 4. Active task table

| Task | Title | Source | Status | Priority | Owner | Deps | Acceptance | Verification | Last touched | Resume from |
|---|---|---|---|---|---|---|---|---|---|---|
| HQ-00 | Provide observed Package/Identity/Name | revenue/HUMAN_QUEUE.md | done | critical | agent (owner-authorized) | — | Exact Partner Center string observed; no guess | VER-20260825-001; `identityVerified:true` | 2026-08-25 | — |
| HQ-01 | Manual IARC retake with legal attestation | revenue/HUMAN_QUEUE.md | done | critical | human | — | Partner Center records Age ratings Complete; do not reconstruct or retake the questionnaire | VER-20260828-001; METRICS 2026-08-28 | 2026-08-28 | Exact regional ratings still need non-destructive observation only if the final review screen exposes them |
| HQ-02 | Seller/tax/payment-profile readiness | revenue/HUMAN_QUEUE.md | done | critical | human | — | Partner Center shows tax and payment profiles Complete; no private values recorded | VER-20260828-004; METRICS 2026-08-28 | 2026-08-31 | First-payout date remains unobserved until real proceeds exist; recheck only on a concrete blocker or payment event |
| HQ-03 | Store-delivered physical-Windows pass | revenue/HUMAN_QUEUE.md | ready | high | human | — | `store/WINDOWS-VALIDATION.md` + accessibility matrix completed with fictional data (forced-colors focus + 200% scaling included) | Validation record (build, public Store route, pass/fail, footprint, date) | 2026-08-31 | Install from the live Store page; current scoped estimate is 15 active minutes |
| HQ-04 | Finalize, certify, and publish Paulatim | revenue/HUMAN_QUEUE.md | done | critical | agent (owner-authorized) | — | Exact package/listing/screenshots saved; Hearth package/name removed; Microsoft certified; public page and $14.99 purchase action observed | VER-20260828-003/004; VER-20260831-001 | 2026-08-31 | Do not repeat or create another package |
| HQ-05 | Approve and send first audience batch | store/LAUNCH_KIT.md + store/LAUNCH_TARGETS.md | blocked | medium | human | HQ-08 + live purchasable page | Owner-posted launch batch with URLs + timestamps in METRICS | METRICS entry | 2026-08-31 | Resolve/reverify customer-facing Store links and account wording, then recheck destination rules before owner sends |
| HQ-06 | Optionally deploy the live-aware landing page | revenue/HUMAN_QUEUE.md | ready | medium | human | owner approval + free-host TOS re-check | Public live-aware URL resolves signed-out; host + URL + timestamp in METRICS | METRICS entry | 2026-08-31 | Certification-time sequencing is moot; use current HUMAN_QUEUE HQ-06 steps |
| HQ-07 | Name-risk decision after exact `Ample` unavailability | revenue/HUMAN_QUEUE.md | done | low | human | — | Owner chooses/reserves an available launch name and records decision | VER-20260828-001; D049 | 2026-08-28 | Paulatim selected and reserved |
| CAND-002 | Historical Hearth replacement candidate | D040/D041 | superseded | high | agent | — | Replaced by AMPLE-001 after rename; never submit its AppX | VER-20260807-001 → AMPLE-001 | 2026-08-19 | Historical evidence only |
| AMPLE-001 | First exact Ample Store candidate | user instruction 2026-08-19 | superseded | critical | agent | — | Historical evidence complete; never submit after Paulatim rename | VER-20260825-001…003 @ `3b8d225`; hash `7d6ca584…61866b` | 2026-08-28 | Replaced by PAULATIM-001; historical evidence only |
| PAULATIM-001 | First exact Paulatim 1.1.1 Store candidate | owner authorization 2026-08-28 | done | critical | agent | — | Visible Paulatim branding; unique 1.1.1 package; stable Store/data internals; exact-SHA green CI; independently verified AppX/screenshots; staged kit | VER-20260828-002/003 @ `f2d2a417`; AppX `af8b4581…b5146` | 2026-08-31 | Preserve the exact certified/public bytes; do not resubmit or rebuild |
| HQ-08 | Reconcile live Paulatim links + account wording | revenue/HUMAN_QUEUE.md | blocked | high | human | fresh explicit authorization + authenticated Partner Center session | Support URI targets `docs/SUPPORT.md`; owner chooses the App website destination; short description/description/feature/caption qualify “no account”; all reverified publicly | public catalog recheck + METRICS entry | 2026-08-31 | Both links use the generic studio site and four public copy surfaces retain ambiguous wording; a new submission/publication cycle may be required; agent may only reobserve until separately authorized |
| COUNCIL-001 | 7-seat market-readiness council + full remediation | user instruction 2026-07-28 | done | high | agent | — | All agent-fixable gaps M1–M10 / D1 / D2 / R1 / R2 closed; every local gate green on the remediated tree | VER-20260729-001 @ working-tree:`246baac`+dirty:`f6edf2f2b6cff045` | 2026-07-29 | — |
| RECON-001 | Working tree vs `origin/main` draft drift | HIST-20260724-001 | done | high | agent | — | Draft committed + remote merged + pushed; single authoritative tree on `main` @ `59787f4` | VER-20260724-006 @ `59787f4` | 2026-07-24 | — |
| DOCS-001 | Documentation consolidation + control system | user instruction 2026-07-24 | done | high | agent | — | Tracker, index, history, verification log, proposals, migration map, archive, validator all green | VER-20260724-001…005 @ working-tree:`4a32b73`+dirty:`451945c517e87554` | 2026-07-24 | — |

Status vocabulary: proposed / todo / ready / in-progress / paused / blocked /
needs-reconciliation / done / verified-stale / superseded / cancelled.

## 5. Active task details

### HQ-04 — Paulatim certification and publication (completed 2026-08-31)

- Outcome: exact PAULATIM-001 was accepted by CI and Partner Center; tax and
  payment profiles were observed Complete; the Paulatim listing and five exact
  screenshots were saved; the Hearth package and display-name reservation were
  removed; Microsoft certified the submission; the owner released the hold;
  and the United States Store purchase action was observed publicly.
- Hard rules: never replace, re-upload, rebuild, resubmit, or republish the
  accepted AppX. The historical manual-hold/failure procedure is closed unless
  Microsoft reports a new concrete defect.
- Post-publication outcome: `store/POST_PUBLICATION_DOC_SWEEP.md` was applied.
  HQ-03 remains unobserved; HQ-08 is a separate owner-controlled listing-only
  correction and does not authorize any package change.

## 6. Blockers, risks, active discoveries

| ID | Blocked item | Why | Unblock condition | Affected |
|---|---|---|---|---|
| ~~B1~~ | ~~Certification + publication~~ | **Resolved 2026-08-31:** exact PAULATIM-001 passed Microsoft certification; owner-authorized publication produced a live $14.99 purchase path | — | HQ-03 remains a residual post-publication validation gap |
| ~~B4~~ | ~~Owner-action batch~~ | **Resolved 2026-08-28:** the owner completed IARC, selected Paulatim, and explicitly delegated reservation, draft replacement, and certification submission to the agent. D047 remains the true historical time model. | — | Tax/payment readiness, submission, certification, and publication are complete; HQ-03 and optional distribution remain |
| ~~B3~~ | ~~First Ample candidate identity~~ | **Resolved 2026-08-25:** Partner Center product `9PLRSZZMFPJH` reports exact identity `ToledoTechnologies.Hearth`; repository now has `identityVerified:true` | — | AMPLE-001 completed at VER-20260825-003 |
| ~~B2~~ | ~~Replacement candidate (CAND-002)~~ | **Resolved 2026-08-02…08-04** — the tree was committed (`fe0fc4a`…`270e650`) and CI built the candidate. This row survived five days after its own unblock condition was met; removed from active blockers 2026-08-07 | — | — |

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| R1 — zero demand after launch (no demand evidence exists) | high | Bet A falsifier path | 5-day signal gate → pre-built reposition menu RP-1…RP-4 + `store/REPOSITION_KIT.md` (revenue/PLAN.md, D037) | agent+owner |
| ~~R2 — certification failure~~ | resolved 2026-08-31 | Microsoft certified exact PAULATIM-001 | Preserve the exact report/package evidence; no new candidate needed | agent |
| R3 — Partner Center/live-listing facts can drift | **low** | decisions on stale fields | Package/submission facts reobserved at certification; signed-out page/catalog, price, rating, and purchase action observed 2026-08-31 | agent |
| ~~R4~~ | — | — | **Resolved 2026-08-04** — remediation is committed and landed. Row retired 2026-08-07 | — |
| R5 — wrong MSIX submitted | resolved | historical Hearth or Ample bytes submitted as Paulatim | Partner Center contains only PAULATIM-001 `af8b4581…b5146`; preserve it unchanged. AMPLE-001, CAND-002, and every other AppX remain never-submit | agent |
| R6 — HQ-03 has no verified Windows machine (new 2026-08-07) | **low** (downgraded same day) | delays post-certification validation only | **Corrected:** HQ-03 depends on HQ-04, not the reverse — the Microsoft-signed build does not exist until after certification, so this never blocked submission. CI `windows-store.yml` already exercises the packaged AppX on `windows-latest` (DPAPI lifecycle matrix + renderer smoke + screenshots). Residual need is a human ear on Narrator | owner (post-certification) |
| ~~R8 — "Hearth" collision~~ | resolved by rename 2026-08-19 | forced candidate reset | Historical analysis retained in `revenue/NAME-RISK-2026-08-07.md` | owner+agent |
| ~~R9 — display name not reserved~~ | resolved | **Resolved 2026-08-28:** exact Paulatim is reserved and set as dashboard name on product `9PLRSZZMFPJH`; package identity remains `ToledoTechnologies.Hearth` | Hearth listing references were removed and its display-name reservation was deleted; preserve the stable package identity | agent |
| R7 — session-to-session document drift (new 2026-08-07) | **high** | agents act on stale state; owner acts on wrong hash/commit | Re-derive the resume point from `git`/`gh` every session rather than trusting the prior summary. This risk has now materialised three times (RECON-001, B2/R4 survival, the 08-04 resume point) | agent |
| R10 — live Store links / account wording mismatch | **medium** | Store visitors reach a generic studio page, and “no account” can be mistaken for no Microsoft account requirement | Owner explicitly authorizes/executes HQ-08 in an authenticated Partner Center session; then reverify both links and the corrected copy before outreach | owner; agent may reobserve only until authorized |

Resolved 2026-07-24 and moved to history: host-move drift + working-tree
reconciliation (HIST-20260724-001…006), stale node_modules repair
(HIST-20260724-003). CI-observation gap G2 closed 2026-07-28 — main-line CI
observed green through `origin/main` HEAD `246baac` (VER-20260728-001…003).

## 7. Current verification snapshot

| Gate | Ref | Env | Result | Summary | Timestamp | VER |
|---|---|---|---|---|---|---|
| Historical AMPLE-001 Quality Gate | `3b8d225` | CI ubuntu | pass / superseded | full gate; run 32844120492; never-submit after Paulatim rename | 2026-08-25 | VER-20260825-003 |
| Historical AMPLE-001 Windows build | `3b8d225` | CI windows | pass / superseded | run 32844120483; artifact 9561731052; AppX `7d6ca584…61866b`; never-submit | 2026-08-25 | VER-20260825-003 |
| Documentation safety close | working-tree:`13bdea2`+dirty (exact fingerprint in log) | local linux | pass | lint; typecheck ×2; 14 files/49 tests; vite + Electron bundles; secrets 197; Store 277; docs PASS; diff clean | 2026-08-26 | VER-20260826-001 |
| Full local candidate preflight | working-tree:`c0eb360`+dirty (exact fingerprint in log) | local (linux) | pass | strict identity preflight; lint 0; typecheck ×2; 14 files/49 tests; vite build; secrets 197; store 277; docs PASS; licenses 54; audit 0 | 2026-08-25 | VER-20260825-002 |
| Paulatim candidate local gate | working-tree:`886314e`+dirty (exact fingerprint in log) | local linux | pass | identity preflights; lint; typecheck ×2; 15 files/52 tests; vite + Electron bundles; secrets 199; Store 277; docs PASS; notices 54; audit 0; generated assets deterministic; diff clean | 2026-08-28 | VER-20260828-002 |
| Paulatim exact candidate | `f2d2a417` | CI ubuntu + windows + local linux | pass | Quality 33169087812; Windows 33169087811; artifacts 9684903207/9684887490; AppX `af8b4581…b5146`; five screenshot hashes match | 2026-08-28 | VER-20260828-003 |
| Partner Center submission | product `9PLRSZZMFPJH`; submission `1152921505701225649` | EXT-PC | In certification / Pre-processing | only Paulatim package/name; listing and five screenshots saved; age/tax/payment Complete; manual publication hold | 2026-08-28 | VER-20260828-004 |
| Paulatim certification + public release | product `9PLRSZZMFPJH`; exact PAULATIM-001 | EXT-PC + signed-out Store/catalog | pass / live | certification stages green; Publish now executed; public title/publisher/screenshots; active $14.99 Purchase action | 2026-08-31 | VER-20260831-001 |
| Post-release trigger-safety baseline | `1c0d164` | CI ubuntu + trigger audit | pass | Quality 33398564825 green; identical package tree; no Windows workflow run | 2026-08-31 | VER-20260831-002 |
| Post-publication documentation close | working-tree:`bcefdd4`+dirty (exact fingerprint in log) | local linux | pass | full non-packaging suite; 25 docs/listing/landing paths; no Windows-trigger path; no package command | 2026-08-31 | VER-20260831-003 |
| Post-publication documentation Quality | `5cfc573` | CI ubuntu + trigger audit | pass | Quality 33401339453 green; exact verified tree; no Windows workflow run | 2026-08-31 | VER-20260831-004 |
| Post-publication evidence close | `5ad1d21` | CI ubuntu + trigger audit | pass | Quality 33401875798 green; final launch evidence only; no Windows workflow run | 2026-08-31 | VER-20260831-005 |
| Documentation truth audit | `889100c` | CI ubuntu + trigger audit | pass | Quality 33451146452 green; exact locally gated tree `08c0ea17`; no Windows workflow run | 2026-08-31 | VER-20260831-006/007 |
| Evidence close local gate | working-tree:`f2d2a417`+dirty (21 docs/landing paths) | local linux | pass | full non-packaging suite; no package command; Windows-trigger exclusion checked separately | 2026-08-28 | VER-20260828-005 |
| Evidence close Quality Gate | `ad9d22a` | CI ubuntu | pass | run 33177707087; notices, secrets, Store/landing validation, audit, lint, typecheck, tests, and build green; no Windows workflow triggered | 2026-08-28 | VER-20260828-006 |
| Installed Windows pass | public Store build | physical Windows | ready / not observed | HQ-04 is complete; execute the scoped 15-minute HQ-03 pass without implying it preceded publication | — | — |

Historical green runs remain valid only for their exact refs. The prior
`c0eb360` failure and AMPLE-001 success remain history; neither supplies
Paulatim candidate bytes. See store/WINDOWS-VALIDATION.md.

## 8. Environment and release state

| Surface | Ref / version | State | Last verified | Evidence | Drift |
|---|---|---|---|---|---|
| Working tree | evidence-only successor to exact docs commit `889100c` | clean after documentation truth close; certified bytes unchanged | 2026-08-31 | git status + tree comparison | none |
| Local `cycle-2-shipped` | `246baac` | stale; behind current `main` | 2026-08-26 | git | historical branch |
| Local `main` | evidence-only successor to `889100c76abe3e862bdfc6e2b0164f2db174e7f5` | synchronized with origin after close; PAULATIM-001 source remains `f2d2a417` | 2026-08-31 | git | none |
| `origin/main` | evidence-only successor to `889100c76abe3e862bdfc6e2b0164f2db174e7f5` | public documentation truth close; no package input changed | 2026-08-31 | git + gh | none |
| CI | PAULATIM-001 source `f2d2a417`; substantive documentation head `889100c` | candidate Quality/Windows green; documentation Quality 33451146452 green; no Windows run after candidate | 2026-08-31 | VER-20260828-003; VER-20260831-007 | none |
| Partner Center | Product `9PLRSZZMFPJH`; submission `1152921505701225649`; exact identity `ToledoTechnologies.Hearth`; only Paulatim name/package | certification passed; publication initiated; $14.99 | 2026-08-31 | VER-20260831-001 | UI last observed In publishing while public edge was already live |
| Microsoft Store live | `https://apps.microsoft.com/detail/9PLRSZZMFPJH` | public; active $14.99 USD Purchase action | 2026-08-31 | VER-20260831-001 | page/catalog live; sales metrics not yet observed |
| Landing host | — | not deployed | — | landing/README.md | HQ-06 is an optional live-aware deployment; certification-time sequencing is moot |

Implemented ≠ committed ≠ pushed ≠ tagged ≠ built ≠ submitted ≠ certified ≠
published ≠ live-verified. The only tag is `v1.0.0` (2026-06-11); no `v1.1.0`
tag exists because tags trigger the Release Build and the Store path is manual.

## 9. Recently completed

| Date | Item | Task | Verification | History |
|---|---|---|---|---|
| 2026-08-31 | Reconciled U.S.-only availability, Microsoft-vs-Paulatim account wording, public/configured categories, Store URLs/copy, proposal state, payout uncertainty, and post-publication owner actions without changing package bytes | documentation truth audit | VER-20260831-006/007 @ `889100c` | HIST-20260831-005 |
| 2026-08-31 | Microsoft certified exact PAULATIM-001; owner-authorized publication completed; signed-out Store page and $14.99 purchase action observed | HQ-04 / Bet A live | VER-20260831-001 | HIST-20260831-001 |
| 2026-08-28 | Exact Paulatim candidate passed both CI gates; independently verified package/screenshots staged; listing saved; Hearth package/name removed; submission entered certification under manual publication hold | PAULATIM-001 + HQ-02/HQ-04 | VER-20260828-003/004 @ `f2d2a417` | HIST-20260828-002/003 |
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

## 10. Proposed scope

Compact index — details in [PROPOSALS.md](docs/project/PROPOSALS.md). Only
entries marked pending or conditional are unapproved scope; do not start those
without the stated approval.

- PROP-001 reconcile working tree with `origin/main` (executed 2026-07-24)
- PROP-002 branch hygiene: duplicate/superseded branches (pending; destructive)
- PROP-003 branch strategy (partially executed 2026-08-25; remaining branch
  deletion belongs to pending PROP-002)
- PROP-004 landing deployment (pending owner approval; live gate met; HQ-06)
- PROP-005 Bet B Electron kit (pending/conditional — revenue/OPPORTUNITIES.md A4.6;
  either/or vs 60-min queue budget in D038)
- PROP-006 privacy-first positioning proposal (superseded by D043)
- PROP-007 mission-target retirement (pending owner decision; AGENTS.md controls)

## 11. Next recommended actions

**PAULATIM-001 is the sole certified/public package. Every other package is
historical and never-submit. Do not create another package for documentation or
post-publication work.**

1. **Complete HQ-03:** install from the public Store on physical x64 Windows
   and record the 15-minute keyboard/Narrator/presentation validation honestly.
2. **Monitor signal:** inspect Store views/acquisitions/purchases without
   inventing zeros; apply the first five-day gate on 2026-09-05.
3. **Owner-controlled Store-listing correction:** before outreach, the owner
   must separately authorize/execute HQ-08. SupportUri must point to public
   Paulatim support, `appWebsiteUrl` needs an explicit destination decision,
   and four public copy surfaces must clarify that Paulatim has no separate
   in-app account. The listing-only update may require a new
   submission/publication cycle; do not infer authority from the completed
   PAULATIM-001 release. No package-byte change is needed.
4. **Optional owner distribution:** HQ-05 may send reviewed launch drafts;
   HQ-06 may deploy the now-live-aware static landing after host approval.
5. **Preserve the evidence chain:** never replace exact PAULATIM-001 or treat a
   public purchase action as proof of a completed sale, payout, or accessibility
   pass.

## 12. Ledger and archive links

- History: [docs/project/REPO_HISTORY.md](docs/project/REPO_HISTORY.md) (+ `history/commit-index.tsv`)
- Verification: [docs/project/VERIFICATION_LOG.md](docs/project/VERIFICATION_LOG.md)
- Decisions: [revenue/DECISIONS.md](revenue/DECISIONS.md)
- Proposals: [docs/project/PROPOSALS.md](docs/project/PROPOSALS.md)
- Docs index: [docs/project/DOCS_INDEX.md](docs/project/DOCS_INDEX.md)
- Migration map: [docs/project/MIGRATION_MAP.md](docs/project/MIGRATION_MAP.md)
- Archive: [docs/project/archive/](docs/project/archive/)
- Monetization evidence: [revenue/METRICS.md](revenue/METRICS.md)
