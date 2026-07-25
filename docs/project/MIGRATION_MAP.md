# Documentation Migration Map

_Created 2026-07-24 during first-run documentation consolidation. Records every
original preserved before material rewrite, where it went, and why. Archive
root: `docs/project/archive/pre-consolidation/2026-07-24/`._

No archived file below contains credentials. Partner Center product/submission
IDs and CI run IDs are public-ish identifiers and were intentionally retained;
no account, banking, tax, KYC, tester, or key material exists in any copy.

| # | Original (pre-consolidation) | Preserved at | Current replacement | Reason |
|---|---|---|---|---|
| M1 | `HANDOFF.md` working tree, 528-line local draft dated 2026-07-15 (uncommitted) | `archive/pre-consolidation/2026-07-24/HANDOFF.local-draft-2026-07-15.md` | `HANDOFF.md` rewritten as a ≤120-line cold-start launchpad | Consolidation rule: handoff is a launchpad, not a second tracker. Unique content re-homed to `revenue/METRICS.md` (evidence), `revenue/HUMAN_QUEUE.md` (owner actions), `store/README.md` (release playbook), `PROJECT_TRACKER.md` (current state). Supersedes decision D033's "self-contained handoff" design on explicit 2026-07-24 user instruction. |
| M2 | `HANDOFF.md` as published on `origin/main` (commit `0ff209e`, 400 lines) | Git history (`0ff209e`, reachable from `origin/main` and `origin/handoff-cycle-3` lineage) | Same as M1 | The published cycle-3 handoff differs from the local draft (400 vs 528 lines, same 15-section structure). Git is the authoritative record; no file copy needed. |
| M3 | `README.md` pre-edit working tree | `archive/pre-consolidation/2026-07-24/README.md` | `README.md` with continuation pointer updated to `PROJECT_TRACKER.md` | Only the continuation note changed; all product/release content preserved. |
| M4 | `store/README.md` pre-edit | `archive/pre-consolidation/2026-07-24/store-README.md` | `store/README.md` with condensed certification/publication playbook merged from the retired long handoff | Preserve unique operational procedure from handoff §9 before compression. |
| M5 | `docs/strategy/HANDOFF.md` pre-edit | `archive/pre-consolidation/2026-07-24/strategy-HANDOFF.md` | Unchanged pointer file (already correct) | Archived for completeness of the handoff cluster; no rewrite required. |
| M6 | `revenue/PLAN.md` pre-edit | `archive/pre-consolidation/2026-07-24/revenue-PLAN.md` | `revenue/PLAN.md` with line-1 `WORKSPACE_ROOT` corrected | AGENTS.md §1 law requires line 1 to be the current workspace root. Host moved from macOS (`/Users/nicholastoledo/...`) to Linux (`/home/nick/...`). |
| M7 | `docs/strategy/BLIND-SPOTS-LEDGER.md` pre-edit | `archive/pre-consolidation/2026-07-24/BLIND-SPOTS-LEDGER.md` | Same file with historical banner and item-3 correction note | Item 3 ("database is not application-level encrypted") is stale — contradicted by D014 / `docs/ARCHITECTURE.md` (AES-256-GCM snapshots). Contradiction resolved, not erased. |
| M8 | `AGENTS.md` pre-edit | `archive/pre-consolidation/2026-07-24/AGENTS.md` | `AGENTS.md` with appended §14 project-state protocol | Additive only; revenue-loop doctrine untouched. |
| M9 | `docs/strategy/MONETIZATION-DECISION.md`, `FOUR-WEEK-FORECAST.md`, `PRIOR-ATTEMPTS-TRIAGE.md`, `BROWSER-SUBAGENT-RECORDING.md` pre-edit | `archive/pre-consolidation/2026-07-24/strategy/` | Same files with one-line historical/superseded banners | Content already consistent with `revenue/` canon; banners add classification and canonical links. |

## Reclassifications without rewrite

- `docs/strategy/PRESS-THESE-BUTTONS.md` and `FIVE-SYSTEM-PITCHES.md` are already
  pure pointer documents to `revenue/` canon; classified "superseded-pointer"
  in `DOCS_INDEX.md`, left byte-identical.
- `revenue/DECISIONS.md` (D001–D034) is reused as the canonical decision
  ledger. No competing `docs/project/DECISIONS.md` was created.
- The uncommitted working-tree draft state (8 modified files + untracked
  `HANDOFF.md`, diff fingerprint `1cbebb903119c043`) is a local draft of the
  cycle-3 content already published on `origin/main` (`0ff209e` + `e0fc9e0`).
  It is preserved untouched in the working tree and partially in this archive;
  reconciliation is tracked as task RECON-001 / proposal PROP-001.

## Coverage statement

Every file materially rewritten on 2026-07-24 has a complete pre-edit copy in
the archive or in reachable Git history. No document was deleted. No content
was sanitized; stale claims were reclassified with correction notes.
