# Paulatim — Project Tracker

- **Schema:** project-tracker/v1 (2026-07-24)
- **Last updated:** 2026-08-28 (PAULATIM-001 submitted; Microsoft certification in progress under a manual publication hold)
- **Workspace root:** `/home/nick/Development/active/mindful_organizer` (REPO-01)
- **Branch / HEAD:** `main` and `origin/main` at exact PAULATIM-001 source `f2d2a4177fcb05d5b24405c598d0eb9b9d7f01e6` (tree `320490a5cfc1d5e409e8ce0ea2fb05147dc97e4d`)
- **Working tree:** documentation evidence close plus three landing screenshots copied from the exact PAULATIM-001 screenshot artifact; no package-trigger path is intentionally changed
- **Operating mode:** MICROSOFT CERTIFICATION WAIT / MANUAL PUBLICATION HOLD
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
| Product state | Paulatim submission `1152921505701225649` for product `9PLRSZZMFPJH` is **In certification** at Pre-processing. The manual hold says Microsoft cannot publish until **Publish now** is clicked. It is not certified, published, live, or purchasable | 2026-08-28 | VER-20260828-004; D049 |
| Default-branch candidate source | PAULATIM-001 source `f2d2a4177fcb05d5b24405c598d0eb9b9d7f01e6`; tree `320490a5cfc1d5e409e8ce0ea2fb05147dc97e4d` | 2026-08-28 | VER-20260828-003 |
| Live release | none — the submission is in certification under a manual publication hold | 2026-08-28 | VER-20260828-004 |
| Current candidate | PAULATIM-001: `Paulatim 1.1.1.appx`, 175,489,702 bytes, SHA-256 `af8b458149d4c00de7f02d4f4c73a4b786d14dbbd391b0db7e1750d4bf4b5146`. AMPLE-001, CAND-002, and every other package are historical/never-submit | 2026-08-28 | VER-20260828-003; store/WINDOWS-VALIDATION.md |
| Candidate CI verification | Quality 33169087812 and Windows 33169087811 passed on exact source `f2d2a417`; artifacts 9684903207 / 9684887490 independently verified | 2026-08-28 | VER-20260828-003 |
| Candidate local verification | full gate green: identity preflights; lint; typecheck ×2; 15 files/52 tests; renderer 764 modules + Electron bundles; secrets 199; Store 277; docs PASS; notices 54; audit 0; deterministic assets; diff clean | 2026-08-28 | VER-20260828-002; dirty fingerprint in log |
| Documentation-close local verification | full non-packaging gate green: identity strict; lint 0; typecheck ×2; 15 files/52 tests; renderer 764 modules + Electron bundles; secrets 199; Store 277; docs PASS; notices 54; audit 0; diff clean | 2026-08-28 | VER-20260828-005 |
| Local test environment | `better-sqlite3` alternates between node and Electron ABIs depending on whether `electron-builder` last ran. In the Electron state 16/46 tests fail with `NODE_MODULE_VERSION` mismatch — environmental, CI unaffected. `npm rebuild better-sqlite3` restores `npm test` | 2026-08-07 | VER-20260807-001 |
| Candidate package | Exact kit: `tmp/PAULATIM-001-f2d2a41/`; AppX hash `af8b4581…b5146`; screenshot ZIP hash `a4bc6785…45e50`; only this AppX is present in the submitted draft | 2026-08-28 | VER-20260828-003/004 |
| Collected revenue | $0.00; gap $4,000.00; 0 live listings; Day-15 gate assessment executed (D035) | 2026-07-28 | revenue/METRICS.md |
| Major open blocker | Microsoft certification result. After certification, the Store-signed Windows/accessibility pass remains required before any separate **Publish now** decision | 2026-08-28 | VER-20260828-004; section 11 |
| Next recommended action | Wait for certification without changing package bytes; preserve Microsoft's result, then complete HQ-03 on the signed build. Do not click **Publish now** | 2026-08-28 | VER-20260828-004; section 11 |

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
| Decisions (D001–D050) | `revenue/DECISIONS.md` |
| Repository/release history | `docs/project/REPO_HISTORY.md` |
| Verification events | `docs/project/VERIFICATION_LOG.md` |
| Documentation map | `docs/project/DOCS_INDEX.md` |
| Unapproved scope | `docs/project/PROPOSALS.md` |

## 3. Workstream index

| ID | Workstream | Derived status | Tasks (ready/blocked/other) | Last verified ref | Active tasks |
|---|---|---|---|---|---|
| WS-REL | Microsoft Store release (Bet A, $14.99) | blocked — exact Paulatim submission is in Microsoft certification under a manual publication hold | 1 blocked post-certification validation, 2 optional/post-live tasks | VER-20260828-003/004 | HQ-03, HQ-05, HQ-06 |
| WS-REV | Monetization portfolio ($4,000 / Day 28) | blocked — Bet A = WS-REL; Day-15 gate executed (D035); reposition menu + kit ready; Bet B either/or pending owner (D038) | 0 active, 1 proposed | revenue/METRICS.md 2026-07-28 | — |
| WS-DOCS | Documentation control system | done 2026-07-24 (on public main @ `59787f4`) | 2 done | VER-20260724-001…006 | — |
| WS-READY | Market-readiness council + remediation | done; landed before rename | 1 done | VER-20260804-001 | — |

## 4. Active task table

| Task | Title | Source | Status | Priority | Owner | Deps | Acceptance | Verification | Last touched | Resume from |
|---|---|---|---|---|---|---|---|---|---|---|
| HQ-00 | Provide observed Package/Identity/Name | revenue/HUMAN_QUEUE.md | done | critical | agent (owner-authorized) | — | Exact Partner Center string observed; no guess | VER-20260825-001; `identityVerified:true` | 2026-08-25 | — |
| HQ-01 | Manual IARC retake with legal attestation | revenue/HUMAN_QUEUE.md | done | critical | human | — | Partner Center records Age ratings Complete; do not reconstruct or retake the questionnaire | VER-20260828-001; METRICS 2026-08-28 | 2026-08-28 | Exact regional ratings still need non-destructive observation only if the final review screen exposes them |
| HQ-02 | Seller/tax/payout readiness (+ threshold/first-payout-date note) | revenue/HUMAN_QUEUE.md | done | critical | human | — | Partner Center shows tax and payment profiles Complete; no private values recorded | VER-20260828-004; METRICS 2026-08-28 | 2026-08-28 | Recheck only if Microsoft later reports a payout blocker |
| HQ-03 | Choose test route; Store-signed Windows pass | revenue/HUMAN_QUEUE.md | blocked | high | human | HQ-04 (certification); route-choice sub-step is ready now | `store/WINDOWS-VALIDATION.md` + accessibility matrix completed on signed build, fictional data (incl. forced-colors focus + 200% text-scaling line items, council CPO G6) | Validation record (build, route, pass/fail, footprint, date) | 2026-07-29 | Unblock = HQ-04 certification complete; decide Public→Private audience route beforehand |
| HQ-04 | Finalize Paulatim listing and submit for certification | revenue/HUMAN_QUEUE.md | done | critical | agent (owner-authorized) | — | Exact Paulatim package/listing/screenshots saved; Hearth package/name removed; submitted under manual publication hold | VER-20260828-003/004 | 2026-08-28 | Certification is external; publication remains a separate later action |
| HQ-05 | Approve and send first audience batch | store/LAUNCH_KIT.md + store/LAUNCH_TARGETS.md | blocked | medium | human | live purchasable page | Owner-posted launch batch with URLs + timestamps in METRICS | METRICS entry | 2026-07-28 | Unblock = signed-out checkout verification; destinations pre-vetted in LAUNCH_TARGETS.md |
| HQ-06 | Approve PROP-004 sequencing + deploy landing at certification time | revenue/HUMAN_QUEUE.md | ready | medium | human | owner approval of amended PROP-004 | Public prelaunch URL resolves signed-out; host + URL + timestamp in METRICS | METRICS entry | 2026-07-28 | HUMAN_QUEUE HQ-06 steps (host TOS re-check first — D007) |
| HQ-07 | Name-risk decision after exact `Ample` unavailability | revenue/HUMAN_QUEUE.md | done | low | human | — | Owner chooses/reserves an available launch name and records decision | VER-20260828-001; D049 | 2026-08-28 | Paulatim selected and reserved |
| CAND-002 | Historical Hearth replacement candidate | D040/D041 | superseded | high | agent | — | Replaced by AMPLE-001 after rename; never submit its AppX | VER-20260807-001 → AMPLE-001 | 2026-08-19 | Historical evidence only |
| AMPLE-001 | First exact Ample Store candidate | user instruction 2026-08-19 | superseded | critical | agent | — | Historical evidence complete; never submit after Paulatim rename | VER-20260825-001…003 @ `3b8d225`; hash `7d6ca584…61866b` | 2026-08-28 | Replaced by PAULATIM-001; historical evidence only |
| PAULATIM-001 | First exact Paulatim 1.1.1 Store candidate | owner authorization 2026-08-28 | done | critical | agent | — | Visible Paulatim branding; unique 1.1.1 package; stable Store/data internals; exact-SHA green CI; independently verified AppX/screenshots; staged kit | VER-20260828-002/003 @ `f2d2a417`; AppX `af8b4581…b5146` | 2026-08-28 | Preserve exact bytes through certification |
| COUNCIL-001 | 7-seat market-readiness council + full remediation | user instruction 2026-07-28 | done | high | agent | — | All agent-fixable gaps M1–M10 / D1 / D2 / R1 / R2 closed; every local gate green on the remediated tree | VER-20260729-001 @ working-tree:`246baac`+dirty:`f6edf2f2b6cff045` | 2026-07-29 | — |
| RECON-001 | Working tree vs `origin/main` draft drift | HIST-20260724-001 | done | high | agent | — | Draft committed + remote merged + pushed; single authoritative tree on `main` @ `59787f4` | VER-20260724-006 @ `59787f4` | 2026-07-24 | — |
| DOCS-001 | Documentation consolidation + control system | user instruction 2026-07-24 | done | high | agent | — | Tracker, index, history, verification log, proposals, migration map, archive, validator all green | VER-20260724-001…005 @ working-tree:`4a32b73`+dirty:`451945c517e87554` | 2026-07-24 | — |

Status vocabulary: proposed / todo / ready / in-progress / paused / blocked /
needs-reconciliation / done / verified-stale / superseded / cancelled.

## 5. Active task details

### HQ-04 — Paulatim certification submission (completed 2026-08-28)

- Outcome: exact PAULATIM-001 was accepted by CI and Partner Center; tax and
  payment profiles were observed Complete; the Paulatim listing and five exact
  screenshots were saved; the Hearth package and display-name reservation were
  removed; submission `1152921505701225649` entered certification.
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
| B1 | Certification + publication | Microsoft certification is in progress; publication remains deliberately held | Preserve the certification result, complete HQ-03 against the Store-signed build, then make a separate publication decision | HQ-03 → HQ-05, WS-REL, WS-REV |
| ~~B4~~ | ~~Owner-action batch~~ | **Resolved 2026-08-28:** the owner completed IARC, selected Paulatim, and explicitly delegated reservation, draft replacement, and certification submission to the agent. D047 remains the true historical time model. | — | Tax/payment readiness and submission are complete; only post-certification Windows observation and later publication work remain |
| ~~B3~~ | ~~First Ample candidate identity~~ | **Resolved 2026-08-25:** Partner Center product `9PLRSZZMFPJH` reports exact identity `ToledoTechnologies.Hearth`; repository now has `identityVerified:true` | — | AMPLE-001 completed at VER-20260825-003 |
| ~~B2~~ | ~~Replacement candidate (CAND-002)~~ | **Resolved 2026-08-02…08-04** — the tree was committed (`fe0fc4a`…`270e650`) and CI built the candidate. This row survived five days after its own unblock condition was met; removed from active blockers 2026-08-07 | — | — |

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| R1 — zero demand after launch (no demand evidence exists) | high | Bet A falsifier path | 5-day signal gate → pre-built reposition menu RP-1…RP-4 + `store/REPOSITION_KIT.md` (revenue/PLAN.md, D037) | agent+owner |
| R2 — certification failure (runFullTrust, content review) | medium | delay; new candidate cycle | Truthful disclosures; preserve report; narrow fix only | Microsoft (result), agent (narrow fix if needed) |
| R3 — Partner Center listing facts partly stale | **low** | decisions on old listing fields | Package, listing, screenshots, Additional Testing Info, Submission Options, age-rating status, tax/payment readiness, app names, and certification state were reobserved 2026-08-28 | agent |
| ~~R4~~ | — | — | **Resolved 2026-08-04** — remediation is committed and landed. Row retired 2026-08-07 | — |
| R5 — wrong MSIX submitted | resolved | historical Hearth or Ample bytes submitted as Paulatim | Partner Center contains only PAULATIM-001 `af8b4581…b5146`; preserve it unchanged. AMPLE-001, CAND-002, and every other AppX remain never-submit | agent |
| R6 — HQ-03 has no verified Windows machine (new 2026-08-07) | **low** (downgraded same day) | delays post-certification validation only | **Corrected:** HQ-03 depends on HQ-04, not the reverse — the Microsoft-signed build does not exist until after certification, so this never blocked submission. CI `windows-store.yml` already exercises the packaged AppX on `windows-latest` (DPAPI lifecycle matrix + renderer smoke + screenshots). Residual need is a human ear on Narrator | owner (post-certification) |
| ~~R8 — "Hearth" collision~~ | resolved by rename 2026-08-19 | forced candidate reset | Historical analysis retained in `revenue/NAME-RISK-2026-08-07.md` | owner+agent |
| ~~R9 — display name not reserved~~ | resolved | **Resolved 2026-08-28:** exact Paulatim is reserved and set as dashboard name on product `9PLRSZZMFPJH`; package identity remains `ToledoTechnologies.Hearth` | Hearth listing references were removed and its display-name reservation was deleted; preserve the stable package identity | agent |
| R7 — session-to-session document drift (new 2026-08-07) | **high** | agents act on stale state; owner acts on wrong hash/commit | Re-derive the resume point from `git`/`gh` every session rather than trusting the prior summary. This risk has now materialised three times (RECON-001, B2/R4 survival, the 08-04 resume point) | agent |

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
| Evidence close local gate | working-tree:`f2d2a417`+dirty (21 docs/landing paths) | local linux | pass | full non-packaging suite; no package command; Windows-trigger exclusion checked separately | 2026-08-28 | VER-20260828-005 |
| Installed Windows pass | — | physical Windows | not observed | blocked behind HQ-03/HQ-04 | — | — |

Historical green runs remain valid only for their exact refs. The prior
`c0eb360` failure and AMPLE-001 success remain history; neither supplies
Paulatim candidate bytes. See store/WINDOWS-VALIDATION.md.

## 8. Environment and release state

| Surface | Ref / version | State | Last verified | Evidence | Drift |
|---|---|---|---|---|---|
| Working tree | `main` `f2d2a417` + docs/landing evidence close | exact candidate source is cleanly committed; current changes do not alter candidate bytes | 2026-08-28 | git status; VER-20260828-003/004 | docs close pending |
| Local `cycle-2-shipped` | `246baac` | stale; behind current `main` | 2026-08-26 | git | historical branch |
| Local `main` | `f2d2a417` + docs/landing evidence close | canonical checked-out branch; exact candidate commit matches origin | 2026-08-28 | git | evidence commit pending |
| `origin/main` | `f2d2a417` | canonical exact PAULATIM-001 source | 2026-08-28 | git + gh | candidate CI green |
| CI | exact source `f2d2a417` | Quality 33169087812 and Windows 33169087811 green | 2026-08-28 | VER-20260828-003 | none |
| Partner Center | Product `9PLRSZZMFPJH`; submission `1152921505701225649`; exact identity `ToledoTechnologies.Hearth`; only Paulatim name/package | In certification / Pre-processing; $14.99; manual publication hold | 2026-08-28 | VER-20260828-004 | certification result pending |
| Microsoft Store live | — | does not exist | — | — | no listing |
| Landing host | — | not deployed | — | landing/README.md | PROP-004 (HQ-06 proposes certification-time deploy) |

Implemented ≠ committed ≠ pushed ≠ tagged ≠ built ≠ submitted ≠ certified ≠
published ≠ live-verified. The only tag is `v1.0.0` (2026-06-11); no `v1.1.0`
tag exists because tags trigger the Release Build and the Store path is manual.

## 9. Recently completed

| Date | Item | Task | Verification | History |
|---|---|---|---|---|
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

**PAULATIM-001 is the sole submitted candidate and is in certification. The
manual publication hold remains active. Every other package is historical and
never-submit.**

1. **Wait for Microsoft:** do not change candidate bytes or create another
   package while submission `1152921505701225649` is in certification.
2. **After certification:** preserve the report and complete HQ-03 against the
   Microsoft-signed build. Fix only a concrete certification defect, if any.
3. **Separate owner action:** click **Publish now** only after the signed-build
   check and an explicit publication decision; then verify signed-out checkout.
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
