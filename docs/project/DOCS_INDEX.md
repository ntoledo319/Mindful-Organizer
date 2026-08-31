# Paulatim Documentation Index

_Canonical inventory of repository documentation. Established 2026-07-24
(first-run consolidation). Verified against working tree
`4a32b73+dirty:1cbebb903119c043` and `origin/main` `e0fc9e0`. Update the row when
a document's role, owner, or path changes._

Classification vocabulary: **canonical** (owns its truth), **supporting**
(context, audits, procedures subordinate to a canonical owner), **generated**
(machine-built; do not hand-edit), **superseded-pointer** (retained link
shell), **historical** (record only; may contain stale claims — banners say
so), **artifact** (raw evidence/output, not prose truth).

## Control system (this directory)

| Path | Purpose | Audience | Class | Action |
|---|---|---|---|---|
| `PROJECT_TRACKER.md` (root) | Current coordination surface: state, tasks, blockers, gates | agents, owner | canonical (current state) | keep ≤350 lines; reconcile each session |
| `docs/project/DOCS_INDEX.md` | This inventory + doc ownership | agents | canonical (doc map) | update on role/path change |
| `docs/project/REPO_HISTORY.md` | Repository registry, heads, milestone/release/incident ledger | agents, owner | canonical (history) | append-only events; refresh heads |
| `docs/project/VERIFICATION_LOG.md` | Verification events tied to exact refs | agents | canonical (verification) | append-only; tracker shows latest only |
| `docs/project/PROPOSALS.md` | Unapproved scope | agents, owner | canonical (proposals) | mutable until accepted/rejected |
| `docs/project/MIGRATION_MAP.md` | Pre-consolidation preservation record | agents | historical | immutable |
| `docs/project/archive/` | Preserved pre-consolidation originals | agents | historical | immutable after archival |
| `docs/project/history/commit-index.tsv` | Machine commit index (all refs) | agents, scripts | generated | regenerate via `refresh_repo_history.py` |

## Root documents

| Path | Purpose | Audience | Class | Action |
|---|---|---|---|---|
| `README.md` | Product front door: what Paulatim is, release status, dev/quality commands | users, devs, agents | canonical (product overview) | keep; visible rename recorded 2026-08-28 |
| `AGENTS.md` | Revenue-loop operating doctrine: jail, constraints, memory files, gates | agents | canonical (operating constraints) | keep; §14 project-state protocol appended 2026-07-24 |
| `CLAUDE.md` | Taste standards and brand identity | agents | canonical (taste/brand) | keep |
| `HANDOFF.md` | Cold-start launchpad | agents | canonical (launchpad) | compressed 2026-07-24 (see MIGRATION_MAP M1/M2) |
| `ETHICS-REVIEW.md` | Claims/ethics audit, 2026-07-14 | release reviewers | supporting (point-in-time audit) | re-audit after any publication change |
| `SECURITY.md` | Security policy, private vuln reporting | researchers, users | canonical (security policy) | keep |
| `THIRD_PARTY_NOTICES.md` | Runtime license notices | legal | generated (`npm run licenses`) | regenerate only |
| `LICENSE` | MIT license | legal | canonical | keep |

## `docs/` — product and legal

| Path | Purpose | Audience | Class | Action |
|---|---|---|---|---|
| `docs/ARCHITECTURE.md` | Electron boundary, state, heuristics, persistence, vault | devs | canonical (architecture) | keep; verified vs code 2026-07-14 |
| `docs/CAPABILITY_VAULT.md` | Vaulted-capability preservation/restoration contract | devs, release | canonical (vault) | keep; non-destructive rule applies |
| `docs/DESIGN_SYSTEM.md` | Earthenware & Vellum design tokens | devs, design | canonical (design system) | keep |
| `docs/PRIVACY.md` | Privacy policy incl. protection limits | users, Store | canonical (privacy) | keep; claims must match exact behavior |
| `docs/TERMS.md` | Terms of use | users, Store | canonical (terms) | keep |
| `docs/REFUNDS.md` | Purchase/refund policy | users, Store | canonical (refunds) | keep |
| `docs/ACCESSIBILITY.md` | Accessibility status + required pre-declaration matrix | users, release | canonical (accessibility status) | no conformance claim until HQ-03 pass |
| `docs/SUPPORT.md` | Intended public Paulatim support page | users | canonical (support) | live Store SupportUri mismatch observed 2026-08-31; owner-controlled HQ-08 requires fresh authority |

## `docs/strategy/` — monetization strategy (legacy layer)

All eight files are subordinate to `revenue/` canon. Banners added 2026-07-24
where the file asserts standalone truth.

| Path | Class | Canonical owner of its truth | Action |
|---|---|---|---|
| `docs/strategy/HANDOFF.md` | superseded-pointer | `HANDOFF.md` (root) | keep as pointer |
| `docs/strategy/MONETIZATION-DECISION.md` | superseded | `revenue/PLAN.md`, `revenue/OPPORTUNITIES.md` | banner added; archive M9 |
| `docs/strategy/PRESS-THESE-BUTTONS.md` | superseded-pointer | `revenue/HUMAN_QUEUE.md` | keep byte-identical |
| `docs/strategy/PRIOR-ATTEMPTS-TRIAGE.md` | historical | `revenue/DECISIONS.md` | banner added; archive M9 |
| `docs/strategy/FOUR-WEEK-FORECAST.md` | historical | `revenue/PLAN.md` (gap arithmetic) | banner added; archive M9 |
| `docs/strategy/FIVE-SYSTEM-PITCHES.md` | superseded-pointer | `revenue/OPPORTUNITIES.md` | keep byte-identical |
| `docs/strategy/BLIND-SPOTS-LEDGER.md` | historical (item 3 stale) | `docs/ARCHITECTURE.md`, D014 | banner + correction; archive M7 |
| `docs/strategy/BROWSER-SUBAGENT-RECORDING.md` | historical (invalidated test) | `revenue/DECISIONS.md` D002 | banner added; archive M9 |

## `revenue/` — monetization state (AGENTS.md-mandated)

| Path | Purpose | Class | Action |
|---|---|---|---|
| `revenue/ASSETS.md` | Asset audit and separable-asset map | canonical (monetization assets) | keep; loop-maintained |
| `revenue/OPPORTUNITIES.md` | 35 monetization frames, scoring, portfolio, falsifiers | canonical (monetization proposals) | keep; loop-maintained |
| `revenue/PLAN.md` | Active bets, arithmetic, critical path, gap | canonical (monetization plan) | line 1 root fixed 2026-07-24 (M6) |
| `revenue/METRICS.md` | Timestamped observed-evidence ledger | canonical (observed evidence) | keep; observed facts only |
| `revenue/HUMAN_QUEUE.md` | Owner/delegated Store actions HQ-00…HQ-08; current Paulatim outcome at top | canonical (owner queue) | HQ-03 ready; HQ-05/HQ-06 optional; HQ-08 owner-controlled; publication complete under D051 |
| `revenue/DECISIONS.md` | Decision ledger D001–D051 | canonical (decisions) | reused as the project decision log; no competing file created |
| `revenue/npm-audit-*.json` | Raw audit output | artifact (gitignored) | regenerate on demand |

## `store/` — Microsoft Store release

| Path | Purpose | Class | Action |
|---|---|---|---|
| `store/README.md` | Release path, Partner Center state, blockers, post-certification playbook | canonical (Store release) | playbook merged from handoff 2026-07-24 (M4) |
| `store/WINDOWS-VALIDATION.md` | Exact-candidate validation + installed smoke/accessibility procedure | canonical (Windows validation) | keep; execute at HQ-03 |
| `store/SCREENSHOTS.md` | Screenshot plan, hashes, acceptance checks | canonical (screenshots) | keep |
| `store/CAMPAIGNS.md` | Campaign link IDs and measurement rules | canonical (campaign plan) | Store link live; owner-authored sends remain gated |
| `store/LAUNCH_KIT.md` | Owner-approved launch drafts (nothing sent) | canonical (launch drafts) | owner sends only (HQ-05) |
| `store/PRODUCT-PAGE-EXPERIMENTS.md` | Post-launch page experiments | canonical (experiments) | gated on live traffic |
| `store/listing-metadata.json` | Structured listing copy/state | canonical (listing data) | live URL/price observed 2026-08-31 |
| `store/identity.json` / `identity.cjs` | Reserved package identity + checker | canonical (Store identity) | `npm run store:check` must print true |

## Remaining docs

| Path | Purpose | Class | Action |
|---|---|---|---|
| `landing/README.md` | Static landing artifact guide | canonical (landing) | Store-live copy ready; not deployed; see PROP-004 |
| `build/README.md` | electron-builder resources note | supporting | keep |
| `resources/BRAND_PROVENANCE.md` | Shipping-art provenance/rights | canonical (art rights) | keep |
| `resources/vault/README.md` | Asset-vault policy | canonical (asset vault) | keep |
| `.github/pull_request_template.md`, `.github/ISSUE_TEMPLATE/*` | PR/issue forms (privacy-guarded) | canonical (intake forms) | keep |
| `.github/workflows/*.yml` | Quality Gate, Release Build, Windows Store, Pages | canonical (CI definitions) | `pages.yml` must never point at commercial landing |
| `.claude/` (agents, commands, skills, memory — ~30 files) | Taste-enforcement tooling | supporting (agent tooling) | keep; tracked despite `.gitignore` entry |

## Excluded from the inventory

Dependency/build/cache/vendor output (`node_modules/`, `dist*/`, `release/`,
`tmp/`, `venv312/`, caches) and gitignored assistant state (`.aider*`,
`file_index.db`, `.qodo/`). These are not documentation of record.

## Maintenance commands

```bash
python3 scripts/project_docs/validate_project_docs.py   # structural gate
python3 scripts/project_docs/refresh_repo_history.py    # regenerate commit index + head rows
```
