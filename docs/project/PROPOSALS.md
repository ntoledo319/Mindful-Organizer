# Hearth Proposals

_Unapproved scope. Nothing here is active work; promotion requires owner
approval (or an explicit user instruction). Monetization frame proposals live
in `revenue/OPPORTUNITIES.md`; this file covers repository-maintenance and
process scope. Established 2026-07-24._

| ID | Title | Size | Approval | Affected area |
|---|---|---|---|---|
| PROP-001 | Reconcile working tree with `origin/main` `e0fc9e0` | S | pending | git state |
| PROP-002 | Branch hygiene: remove duplicate-content and superseded branches | S | pending (destructive; explicit approval required) | git refs |
| PROP-003 | Branch strategy: fast-forward local `main`, retire `cycle-*` naming | S | pending | git workflow |
| PROP-004 | Deploy `landing/` to an eligible $0 static host after Store publication | S | pending (gated on live Store URL) | distribution |
| PROP-005 | Bet B — Hearth-to-Production Electron Kit (frame A4.6) | L | pending (conditional behind Bet A) | monetization |

## PROP-001 — Reconcile working tree with origin/main

- **What:** adopt the published cycle-3 state (`e0fc9e0`) into the checkout and
  retire the uncommitted local draft (8 modified files + untracked 528-line
  `HANDOFF.md`, fingerprint `1cbebb903119c043`).
- **Why:** the dirty tree is the pre-publication draft of content the remote
  already published in condensed form (`0ff209e` + `e0fc9e0`); both describe
  the same cycle-3 close. Keeping both invites double-truth drift.
- **Evidence:** content hashes differ on all 9 files; diffs are draft-vs-published
  wording (e.g., PLAN "prepared" vs "published"); draft preserved at
  `docs/project/archive/pre-consolidation/2026-07-24/HANDOFF.local-draft-2026-07-15.md`,
  published version in Git history.
- **Value:** single authoritative state; unblocks clean verification refs.
- **Risks:** losing draft-only nuance — mitigated by the archive; a final
  spot-diff of the two handoff iterations is part of execution.
- **Prerequisites:** owner approval for any `git checkout --` / clean of
  user-owned uncommitted files.

## PROP-002 — Branch hygiene

- **What:** delete local `cycle-1-published`, `cycle-1-release-state`, local
  `feature/monetization`, and (with owner approval) remote `handoff-cycle-3`
  and `feature/revenue-cycle-0`.
- **Why:** local duplicates have trees byte-identical to main-line commits
  (verified 2026-07-24, empty diffs vs `4a32b73` / `5bb2611` / `8172603`) and
  exist only as cycle bookkeeping; `handoff-cycle-3` content is already on
  `origin/main`; `feature/revenue-cycle-0` is declared diverged legacy.
- **Risks:** destructive ref removal — trees are preserved on main /
  `origin/feature/monetization`; explicit owner approval required; record a
  `remote-changed` / `branch-removed` history event if executed.

## PROP-003 — Branch strategy

- **What:** fast-forward local `main` to `origin/main` (0 ahead, 17 behind),
  work on `main` or short-lived feature branches, stop creating `cycle-*`
  bookkeeping branches; adjust workflow branch triggers only if conventions
  change.
- **Why:** local `main` currently points at a 2026-06-13 commit while the
  effective main line lives on `origin/main`; stale `main` misleads any tool
  or agent that assumes it is current.

## PROP-004 — Landing deployment (post-publication)

- **What:** deploy the scriptless `landing/` artifact to an eligible $0 static
  host (Cloudflare Pages / Netlify after a current-TOS re-check) once the Store
  page is observed live.
- **Why:** D007 rejected GitHub Pages for commercial hosting; the artifact is
  ready but has no purchase link until the listing exists.
- **Prerequisites:** live Store URL (HQ-04), campaign IDs (store/CAMPAIGNS.md).

## PROP-005 — Bet B: Hearth-to-Production Electron Kit

- **What:** genuinely new $249 developer kit (frame A4.6 in
  `revenue/OPPORTUNITIES.md`): clean demo, threat model, encrypted-storage
  migration pattern, sender-validated IPC, packaging, CI, tests. Not a paid
  copy of the MIT repo.
- **Status:** conditional; stays behind Bet A's certification path. Falsifier,
  arithmetic, and funnel are defined in `revenue/OPPORTUNITIES.md` and
  `revenue/PLAN.md`.
