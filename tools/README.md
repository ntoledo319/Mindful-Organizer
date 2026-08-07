# tools/

Agent utilities that must **not** live in `scripts/`.

`scripts/**` is inside the path filter of `.github/workflows/windows-store.yml`.
Anything added there triggers a fresh MSIX build and mints another artifact that
is not a submission candidate — see the decoy problem recorded in
`store/WINDOWS-VALIDATION.md`. Nothing in `tools/` is in any workflow path
filter, so files here can be added and edited without disturbing the candidate
evidence chain.

## rename-product.mjs

Executes a product rename sweep. Dry run by default.

```
node tools/rename-product.mjs --to <NewName>
node tools/rename-product.mjs --to <NewName> --apply
node tools/rename-product.mjs --to <NewName> --identity ToledoTechnologies.<NewName> --apply
```

Current blast radius against `Hearth` (measured 2026-08-07):

- **rewrite** — 87 files, 489 occurrences
- **preserve** — 19 files, 125 occurrences

The preserve list is the point of the script. `revenue/METRICS.md`,
`revenue/DECISIONS.md`, `docs/project/REPO_HISTORY.md`,
`docs/project/VERIFICATION_LOG.md`, `store/WINDOWS-VALIDATION.md`, `HANDOFF.md`,
`PROJECT_TRACKER.md` and everything under `docs/project/archive/` record events
that happened to a product that **was** named Hearth. Rewriting them would
falsify the record. They keep the old name and get a hand-written forward note
instead.

`tools/` itself is excluded — this script carries `Hearth` string literals in its
own rules table, and letting the sweep rewrite them would corrupt it.

### What the script cannot do

1. Reserve a name in Partner Center. Owner action.
2. Decide whether `identityName` may change on reserved product `9PLRSZZMFPJH`
   or whether a new product reservation is needed. That determines whether the
   held submission is edited or replaced, and it is the expensive unknown.
3. Regenerate brand assets — run `npm run icons && npm run winstore-assets`.
4. Build, commit, or push.

After `--apply`: full gate suite, then a fresh CI candidate cycle. The rename
changes the AppX manifest, so **CAND-002 and its staged swap kit become
historical the moment this runs.** Context and cost:
`revenue/NAME-RISK-2026-08-07.md`.
