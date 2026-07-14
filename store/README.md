# Microsoft Store release path

This directory holds Hearth's reserved Partner Center identity and draft listing
copy. The identity is real; the listing is not verified live and no current
package is purchasable.

## Commercial model

The current hypothesis is a one-time **$14.99** official Windows package. The
source remains MIT-licensed. A purchase pays for a built package and Store
delivery, not exclusive code or a clinical capability.

The previous automated publisher failed while mutating metadata and downloaded
an unpinned Store CLI. It was removed. Price, metadata, package upload, and final
submission belong in Partner Center. `.github/workflows/windows-store.yml`
produces a review artifact only; it does not publish.

## Build

The `appx` target must run on Windows:

```powershell
npm ci
npm run licenses
npm run build:winstore
```

`npm run store:check` must print `true`. A fresh package must pass the full Node
quality gate and Microsoft certification; expired historical artifacts are not
release evidence.

## Pre-submission blockers

- [ ] Decide and document protection for sensitive local SQLite data; the
      current database is not application-level encrypted.
- [ ] Confirm ownership/provenance and redistribution rights for both PNG brand
      assets, including any AI assistance.
- [ ] Enable the working support channel referenced by the listing.
- [ ] Run a fresh Windows package build and smoke test on supported Windows.
- [ ] Capture screenshots from that exact build.
- [ ] Confirm Partner Center account, tax, payout, age rating, privacy, terms,
      and the one-time $14.99 price.
- [ ] Manually enter/review the listing copy in Partner Center.
- [ ] Upload and submit only after every item above is complete.

The owner-only steps are maintained in `revenue/HUMAN_QUEUE.md`; technical work
must not silently turn those unchecked items into claims of readiness.
