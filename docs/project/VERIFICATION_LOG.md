# Hearth Verification Log

_Append-only register of meaningful verification events, each tied to an exact
Git ref or an honestly-labeled dirty working tree. Established 2026-07-24 from
`revenue/METRICS.md` (which remains the monetization evidence ledger; rows here
reference rather than duplicate its detail). One row per meaningful gate, not
per command. Raw output stays in CI run pages or local artifacts, never in this
file. The tracker shows only the latest result per gate._

ID format: `VER-YYYYMMDD-NNN`. Result vocabulary: pass / fail / blocked /
partial. Times are UTC; "time n/o" = not observed in source evidence.

| ID | UTC timestamp | Task(s) | Scope | Method / command | Ref | Env | Result | Counts / summary | Duration | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| VER-20260714-001 | 2026-07-14 (time n/o) | pre-tracker (release candidate) | release | GH Actions Quality Gate | `8172603b62c2457696608c145511bd3fe92429d4` | CI ubuntu | pass | locked install, secret scan, store validation, lint, both typechecks, 9 files / 30 tests, renderer+electron builds, licenses, prod audit | n/o | [run 29322423682](https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29322423682); revenue/METRICS.md 2026-07-14 | Accepted-candidate gate. |
| VER-20260714-002 | 2026-07-14 (time n/o) | pre-tracker (release candidate) | release+windows | GH Actions Windows Store (MSIX) | `8172603b62c2457696608c145511bd3fe92429d4` | CI windows | pass | MSIX build, MakeAppx semantic validation, 5 exact-candidate 1920×1080 screenshots, sentinel-guarded safeStorage/DPAPI lifecycle (fresh persistence, corrupt-primary recovery, export warning, key-first + interrupted erase, legacy migration retirement, missing-key fail-closed) | n/o | [run 29322423622](https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29322423622); artifact `hearth-msix` 8306541856 | Produces the accepted AppX (SHA-256 `4900f382…facdb1`). Not certification. |
| VER-20260714-003 | 2026-07-14 (time n/o) | pre-tracker | full local gate | lint, typecheck, vitest, builds, store:validate, audit, secrets | working tree of cycle-1 (dirty, pre-`d01c013`) | local (macOS host) | pass | 30 tests; store validation 246 checks; prod audit 0 high; 155-path secret scan | n/o | revenue/METRICS.md 2026-07-14 | Local screenshot run intentionally skipped (macOS key storage outside jail). |
| VER-20260714-004 | 2026-07-14 (time n/o) | pre-tracker (launch hardening) | docs+release | GH Actions Quality Gate | `d01c013fd8beec91014c37d27a9a310cf5dd0470` | CI ubuntu | pass | full quality gate on public launch-hardening commit | n/o | [run 29345864617](https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29345864617) | Confirms support/landing/issue-form changes. |
| VER-20260714-005 | 2026-07-14 (time n/o) | pre-tracker (launch hardening) | release+windows | GH Actions Windows Store (MSIX) | `d01c013fd8beec91014c37d27a9a310cf5dd0470` | CI windows | pass | full gate incl. native rebuild, screenshots, AppX packaging+validation, artifact upload | 4m57s | [run 29345863949](https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29345863949); artifact 8316167277 | Verification-only build; bytes differ from accepted package and must not replace it (D032). |
| VER-20260714-006 | 2026-07-14 (time n/o) | pre-tracker | full local gate | form YAML parse, store:check, store:validate, lint, typecheck, vitest, builds, secrets, licenses, brand assets | working tree (dirty, cycle-2 close) | local (macOS host) | pass | 3 YAML forms; identity true; 263 store checks; 0 lint warnings; 9 files / 30 tests; 160-file secret scan; notices for 54 pkgs | n/o | revenue/METRICS.md 2026-07-14 cycle-2 | First green run of the deletion-safe secret scanner (D030). |
| VER-20260715-001 | 2026-07-15 (time n/o) | pre-tracker | docs+state | GH Actions Quality Gate | `4a32b7306ab9ca76a09fb3fae399649c07543e5a` | CI ubuntu | pass | state-only close commit | n/o | run 29346492274 per revenue/METRICS.md 2026-07-15 | Latest observed CI result for the main line. |
| VER-20260715-002 | 2026-07-15 | pre-tracker | environment | local shell probe (`pwd`, `true`) | local environment | local (macOS host) | fail | every subprocess exited 137 | n/o | revenue/METRICS.md 2026-07-15; D034 | Recorded as incident HIST-20260715-001; local verification impossible that day. |

| VER-20260724-001 | 2026-07-24T09:20Z | DOCS-001 | docs | `python3 scripts/project_docs/validate_project_docs.py` | working-tree:`4a32b73`+dirty:`451945c517e87554` | local (linux) | pass | 12 structural checks over tracker, history, verification log, index, proposals, migration map, handoff | <1s | this log + script | Validator created this session. Two initial findings were validator-scoping bugs (cross-references counted as duplicate definitions); fixed and re-run green. |
| VER-20260724-002 | 2026-07-24T09:16Z | DOCS-001 | docs+security | `npm run secrets` | working-tree:`4a32b73`+dirty:`451945c517e87554` | local (linux) | pass | 181 readable files scanned | ~2s | script output | Includes all newly written project-control files. |
| VER-20260724-003 | 2026-07-24T09:19Z | DOCS-001 | store+docs | `npm run store:validate` | working-tree:`4a32b73`+dirty:`451945c517e87554` | local (linux) | pass | 269 checks (263 at cycle 2; delta from new project docs) | ~3s | script output | Covers README/store/README/HANDOFF edits. |
| VER-20260724-004 | 2026-07-24T09:18Z | DOCS-001 | code baseline | `npm run typecheck` | working-tree:`4a32b73`+dirty:`451945c517e87554` | local (linux) | pass | `tsconfig.json` + `tsconfig.electron.json`, 0 errors | ~15s | script output | Confirms code tree unaffected by docs work. |
| VER-20260724-005 | 2026-07-24T09:23Z | DOCS-001 | code baseline | `npm test` (vitest run) | working-tree:`4a32b73`+dirty:`451945c517e87554` | local (linux) | pass | 9 files / 30 tests, matches CI baseline | 3.38s | script output | First attempt failed: `node_modules` carried macOS native builds from the previous host (missing `@rollup/rollup-linux-x64-gnu`). Repaired via locked `npm ci` with in-jail caches (HIST-20260724-003). Electron binary and 3 install-script approvals still pending on this host — packaging/`npm run dev` not verified here. |

| VER-20260724-006 | 2026-07-24T09:45Z | RECON-001 | docs+reconciliation | `validate_project_docs.py`, `npm run secrets`, `npm run store:validate`; commit index regenerated | `59787f4ae77901424947c3fb504f96dfce11e4a9` (clean tree) | local (linux) | pass | validator PASS; secrets 181 files; store 269 checks; index at 124 commits | ~8s | this log + script output | Post-merge gate after resolving 7 conflicts (5 → published remote versions, 2 hand-merged). Validator re-run green after state-sync edits. |

## Dirty-tree reference format

`working-tree:<HEAD>+dirty:<fingerprint>` where the fingerprint is the first 16
hex chars of `git diff HEAD | sha256sum`, accompanied by the diff stat. A
dirty-tree pass proves that tree only — never a later commit.
