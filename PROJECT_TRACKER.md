# Paulatim — Project Tracker

- **Schema:** project-tracker/v1 (2026-07-24)
- **Last updated:** 2026-08-28 (Paulatim reserved; PAULATIM-001 rename in progress)
- **Workspace root:** `/home/nick/Development/active/mindful_organizer` (REPO-01)
- **Branch / HEAD:** `main` at `886314e` before the current dirty Paulatim rename; `origin/main` matched at session start. Historical AMPLE-001 source is `3b8d225`
- **Working tree:** visible-brand rename plus compatibility guards, listing metadata, and durable state corrections; this tree intentionally triggers a fresh Windows package after gates/push
- **Operating mode:** PAULATIM CANDIDATE / CERTIFICATION SUBMISSION
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
| Product state | Visible product name is Paulatim; exact name reserved on product `9PLRSZZMFPJH` and set as dashboard name. Verified package identity stays `ToledoTechnologies.Hearth`. Prior Hearth submission was canceled to draft; no Paulatim package is submitted/certified/published | 2026-08-28 | VER-20260828-001; D049 |
| Default-branch candidate source | none yet — PAULATIM-001 is a gated dirty-tree preparation over `main` `886314e`; historical AMPLE-001 source is `3b8d225` | 2026-08-28 | live `git`; VER-20260825-003 historical |
| Live release | none — not submitted, certified, published, or purchasable | 2026-07-14 | HIST-20260714-003 |
| Current candidate | none until fresh PAULATIM-001 CI. AMPLE-001 `7d6ca584…61866b`, CAND-002, and every Hearth package are historical/never-submit | 2026-08-28 | D049; store/WINDOWS-VALIDATION.md |
| Candidate CI verification | pending exact pushed PAULATIM-001 SHA; AMPLE-001 runs 32844120492 / 32844120483 remain historical evidence only | 2026-08-28 | VER-20260825-003; D049 |
| Candidate local verification | full gate green: identity preflights; lint; typecheck ×2; 15 files/52 tests; renderer 764 modules + Electron bundles; secrets 199; Store 277; docs PASS; notices 54; audit 0; deterministic assets; diff clean | 2026-08-28 | VER-20260828-002; dirty fingerprint in log |
| Documentation-close local verification | full non-packaging gate green: lint 0, typecheck ×2, 14 files/49 tests, renderer 764 modules + Electron bundles, secrets 197, Store 277, docs PASS, diff clean | 2026-08-26 | VER-20260826-001 |
| Local test environment | `better-sqlite3` alternates between node and Electron ABIs depending on whether `electron-builder` last ran. In the Electron state 16/46 tests fail with `NODE_MODULE_VERSION` mismatch — environmental, CI unaffected. `npm rebuild better-sqlite3` restores `npm test` | 2026-08-07 | VER-20260807-001 |
| Candidate package | pending PAULATIM-001; no filename, size, hash, run, artifact, or kit may be recorded before exact-SHA CI | 2026-08-28 | D049 |
| Collected revenue | $0.00; gap $4,000.00; 0 live listings; Day-15 gate assessment executed (D035) | 2026-07-28 | revenue/METRICS.md |
| Major open blocker | Machine sequence only: commit/push the fully gated Paulatim tree once, bind PAULATIM-001 to exact-SHA green CI, then replace the draft and submit. Hearth name deletion waits until Store listing references are removed | 2026-08-28 | VER-20260828-002; D049; section 11 |
| Next recommended action | Commit/push the verified rename tree once, then select only that exact SHA's `paulatim-msix` and screenshot artifacts | 2026-08-28 | VER-20260828-002; section 11 |

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
| WS-REL | Microsoft Store release (Bet A, $14.99) | in-progress — Paulatim reserved and submission authorized; fresh candidate/listing replacement pending | 1 in-progress, 2 reconciliation/post-certification | VER-20260828-001 | PAULATIM-001, HQ-02…HQ-04 |
| WS-REV | Monetization portfolio ($4,000 / Day 28) | blocked — Bet A = WS-REL; Day-15 gate executed (D035); reposition menu + kit ready; Bet B either/or pending owner (D038) | 0 active, 1 proposed | revenue/METRICS.md 2026-07-28 | — |
| WS-DOCS | Documentation control system | done 2026-07-24 (on public main @ `59787f4`) | 2 done | VER-20260724-001…006 | — |
| WS-READY | Market-readiness council + remediation | done; landed before rename | 1 done | VER-20260804-001 | — |

## 4. Active task table

| Task | Title | Source | Status | Priority | Owner | Deps | Acceptance | Verification | Last touched | Resume from |
|---|---|---|---|---|---|---|---|---|---|---|
| HQ-00 | Provide observed Package/Identity/Name | revenue/HUMAN_QUEUE.md | done | critical | agent (owner-authorized) | — | Exact Partner Center string observed; no guess | VER-20260825-001; `identityVerified:true` | 2026-08-25 | — |
| HQ-01 | Manual IARC retake with legal attestation | revenue/HUMAN_QUEUE.md | done | critical | human | — | Partner Center records Age ratings Complete; do not reconstruct or retake the questionnaire | VER-20260828-001; METRICS 2026-08-28 | 2026-08-28 | Exact regional ratings still need non-destructive observation only if the final review screen exposes them |
| HQ-02 | Seller/tax/payout readiness (+ threshold/first-payout-date note) | revenue/HUMAN_QUEUE.md | ready | critical | human | — | Payout-ready boolean + non-sensitive note in METRICS | METRICS entry | 2026-07-28 | HUMAN_QUEUE HQ-02 steps; allow 48h validation |
| HQ-03 | Choose test route; Store-signed Windows pass | revenue/HUMAN_QUEUE.md | blocked | high | human | HQ-04 (certification); route-choice sub-step is ready now | `store/WINDOWS-VALIDATION.md` + accessibility matrix completed on signed build, fictional data (incl. forced-colors focus + 200% text-scaling line items, council CPO G6) | Validation record (build, route, pass/fail, footprint, date) | 2026-07-29 | Unblock = HQ-04 certification complete; decide Public→Private audience route beforehand |
| HQ-04 | Finalize Paulatim listing and submit for certification | revenue/HUMAN_QUEUE.md | in-progress | critical | agent (owner-authorized) | PAULATIM-001 exact CI artifact; reconcile payout status before final submit | Replace historical draft with exact Paulatim package/listing/screenshots; delete Hearth display name when enabled; submit, but do not claim publication | VER-20260828-001 then exact CI/submission result | 2026-08-28 | Full submission authority granted; package preparation active |
| HQ-05 | Approve and send first audience batch | store/LAUNCH_KIT.md + store/LAUNCH_TARGETS.md | blocked | medium | human | live purchasable page | Owner-posted launch batch with URLs + timestamps in METRICS | METRICS entry | 2026-07-28 | Unblock = signed-out checkout verification; destinations pre-vetted in LAUNCH_TARGETS.md |
| HQ-06 | Approve PROP-004 sequencing + deploy landing at certification time | revenue/HUMAN_QUEUE.md | ready | medium | human | owner approval of amended PROP-004 | Public prelaunch URL resolves signed-out; host + URL + timestamp in METRICS | METRICS entry | 2026-07-28 | HUMAN_QUEUE HQ-06 steps (host TOS re-check first — D007) |
| HQ-07 | Name-risk decision after exact `Ample` unavailability | revenue/HUMAN_QUEUE.md | done | low | human | — | Owner chooses/reserves an available launch name and records decision | VER-20260828-001; D049 | 2026-08-28 | Paulatim selected and reserved |
| CAND-002 | Historical Hearth replacement candidate | D040/D041 | superseded | high | agent | — | Replaced by AMPLE-001 after rename; never submit its AppX | VER-20260807-001 → AMPLE-001 | 2026-08-19 | Historical evidence only |
| AMPLE-001 | First exact Ample Store candidate | user instruction 2026-08-19 | superseded | critical | agent | — | Historical evidence complete; never submit after Paulatim rename | VER-20260825-001…003 @ `3b8d225`; hash `7d6ca584…61866b` | 2026-08-28 | Replaced by PAULATIM-001; historical evidence only |
| PAULATIM-001 | First exact Paulatim 1.1.1 Store candidate | owner authorization 2026-08-28 | in-progress | critical | agent | stable identity preserved; exact-SHA CI | Visible Paulatim branding; unique 1.1.1 package full name; stable Store/data internals; green full local gate and exact-SHA Windows run; new AppX/screenshot hashes and kit | VER-20260828-002 local; CI pending | 2026-08-28 | Commit/push once, then exact-SHA CI/artifact verification |
| COUNCIL-001 | 7-seat market-readiness council + full remediation | user instruction 2026-07-28 | done | high | agent | — | All agent-fixable gaps M1–M10 / D1 / D2 / R1 / R2 closed; every local gate green on the remediated tree | VER-20260729-001 @ working-tree:`246baac`+dirty:`f6edf2f2b6cff045` | 2026-07-29 | — |
| RECON-001 | Working tree vs `origin/main` draft drift | HIST-20260724-001 | done | high | agent | — | Draft committed + remote merged + pushed; single authoritative tree on `main` @ `59787f4` | VER-20260724-006 @ `59787f4` | 2026-07-24 | — |
| DOCS-001 | Documentation consolidation + control system | user instruction 2026-07-24 | done | high | agent | — | Tracker, index, history, verification log, proposals, migration map, archive, validator all green | VER-20260724-001…005 @ working-tree:`4a32b73`+dirty:`451945c517e87554` | 2026-07-24 | — |

Status vocabulary: proposed / todo / ready / in-progress / paused / blocked /
needs-reconciliation / done / verified-stale / superseded / cancelled.

## 5. Active task details

### HQ-04 — Paulatim certification submission (in progress, highest risk)

- Immediate dependency: fresh PAULATIM-001 exact candidate accepted by CI and
  Partner Center; reconcile payout readiness before the final submit click.
  AMPLE-001 and every Hearth AppX are historical after the rename.
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
| B1 | Certification + publication | Private payout/tax readiness has not yet been reobserved; IARC is complete | Reconcile HQ-02, then submit the exact PAULATIM-001 draft under the manual publication hold | HQ-04 → HQ-05, WS-REL, WS-REV |
| ~~B4~~ | ~~Owner-action batch~~ | **Resolved 2026-08-28:** the owner completed IARC, selected Paulatim, and explicitly delegated reservation, draft replacement, and certification submission to the agent. D047 remains the true historical time model. | — | Remaining human-only payout reconciliation and post-certification Windows observation stay within the 60-minute ceiling |
| ~~B3~~ | ~~First Ample candidate identity~~ | **Resolved 2026-08-25:** Partner Center product `9PLRSZZMFPJH` reports exact identity `ToledoTechnologies.Hearth`; repository now has `identityVerified:true` | — | AMPLE-001 completed at VER-20260825-003 |
| ~~B2~~ | ~~Replacement candidate (CAND-002)~~ | **Resolved 2026-08-02…08-04** — the tree was committed (`fe0fc4a`…`270e650`) and CI built the candidate. This row survived five days after its own unblock condition was met; removed from active blockers 2026-08-07 | — | — |

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| R1 — zero demand after launch (no demand evidence exists) | high | Bet A falsifier path | 5-day signal gate → pre-built reposition menu RP-1…RP-4 + `store/REPOSITION_KIT.md` (revenue/PLAN.md, D037) | agent+owner |
| R2 — certification failure (runFullTrust, content review) | medium | delay; new candidate cycle | Truthful disclosures; preserve report; narrow fix only | owner (submit), agent (fix) |
| R3 — Partner Center listing facts partly stale | **medium** | decisions on old listing fields | Paulatim reservation/dashboard name and the canceled Hearth draft were observed 2026-08-28. Paulatim package/listing/screenshots remain repository-only until the agent replaces and saves the draft from exact PAULATIM-001 evidence | agent |
| ~~R4~~ | — | — | **Resolved 2026-08-04** — remediation is committed and landed. Row retired 2026-08-07 | — |
| R5 — wrong MSIX submitted | high | historical Hearth or Ample bytes submitted as Paulatim | No current package exists. Submit only the future PAULATIM-001 1.1.1 AppX after exact-SHA CI and independent full-hash verification; AMPLE-001, CAND-002, and every AppX currently in `tmp/` are never-submit | agent |
| R6 — HQ-03 has no verified Windows machine (new 2026-08-07) | **low** (downgraded same day) | delays post-certification validation only | **Corrected:** HQ-03 depends on HQ-04, not the reverse — the Microsoft-signed build does not exist until after certification, so this never blocked submission. CI `windows-store.yml` already exercises the packaged AppX on `windows-latest` (DPAPI lifecycle matrix + renderer smoke + screenshots). Residual need is a human ear on Narrator | owner (post-certification) |
| ~~R8 — "Hearth" collision~~ | resolved by rename 2026-08-19 | forced candidate reset | Historical analysis retained in `revenue/NAME-RISK-2026-08-07.md` | owner+agent |
| ~~R9 — display name not reserved~~ | resolved | **Resolved 2026-08-28:** exact Paulatim is reserved and set as dashboard name on product `9PLRSZZMFPJH`; package identity remains `ToledoTechnologies.Hearth` | Preserve that identity and replace remaining Hearth listing references before deleting the Hearth display name | agent |
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
| Partner Center draft | product `9PLRSZZMFPJH` | EXT-PC | name gate pass / draft | Paulatim reserved/dashboard name; identity exact; old submission canceled; Hearth deletion waits on listing refs | 2026-08-28 | VER-20260828-001 |
| Store candidate/certification | PAULATIM-001 pending | local / CI / EXT-PC | in progress / not submitted | no candidate hash or Partner Center upload yet | 2026-08-28 | D049 |
| Installed Windows pass | — | physical Windows | not observed | blocked behind HQ-03/HQ-04 | — | — |

Historical green runs remain valid only for their exact refs. The prior
`c0eb360` failure and AMPLE-001 success remain history; neither supplies
Paulatim candidate bytes. See store/WINDOWS-VALIDATION.md.

## 8. Environment and release state

| Surface | Ref / version | State | Last verified | Evidence | Drift |
|---|---|---|---|---|---|
| Working tree | `main` `886314e` + dirty Paulatim rename | package-triggering visible rename with compatibility guards and docs | 2026-08-28 | git status; D049 | full gate/commit pending |
| Local `cycle-2-shipped` | `246baac` | stale; behind current `main` | 2026-08-26 | git | historical branch |
| Local `main` | `886314e` + dirty | canonical checked-out branch; matched origin before edits | 2026-08-28 | git | commit pending |
| `origin/main` | `886314e` | canonical remote before Paulatim rename | 2026-08-28 | git + gh | awaiting one gated push |
| CI | no Paulatim run; AMPLE-001 runs remain historical | PAULATIM-001 pending exact pushed SHA | 2026-08-28 | VER-20260825-003 historical | fresh runs required |
| Partner Center | Product `9PLRSZZMFPJH`; exact identity `ToledoTechnologies.Hearth`; Paulatim reserved/dashboard name; canceled draft | $14.99 retained; package/listing replacement not yet performed | 2026-08-28 | VER-20260828-001 | Hearth name deletion waits on listing refs |
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

**Paulatim is reserved and PAULATIM-001 is in progress. AMPLE-001, CAND-002,
and every Hearth/Ample package are historical and never-submit.**

1. **Agent:** commit/push the fully gated Paulatim rename once and bind the new
   package/screenshots to that exact SHA. Download,
   hash, inspect, and stage only the resulting `paulatim-*` artifacts.
2. **Agent (owner-authorized):** replace the canceled Hearth draft package,
   listing, and screenshots with PAULATIM-001; reconcile payout readiness;
   remove Hearth listing references and delete its display name when enabled;
   submit for certification. Do not conflate submission with publication.
3. **After publication only:** execute `store/README.md` "Certification and
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
