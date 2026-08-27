# Microsoft Store release path

> **Candidate update — 2026-08-25:** AMPLE-001 is now bound to exact source
> `3b8d225`, Windows run 32844120483, artifact 9561731052, and AppX SHA-256
> `7d6ca584…61866b`. Five exact-SHA screenshots are artifact 9561704379. The
> verified kit is staged at `tmp/AMPLE-001-3b8d225/`. Nothing was uploaded,
> submitted, certified, published, or made purchasable; the owner must reserve
> the Ample display name before submission.

> **Current correction — 2026-08-25:** Partner Center product `9PLRSZZMFPJH`
> was reobserved with exact Package/Identity/Name
> `ToledoTechnologies.Hearth`; only `Hearth` is currently reserved. No name was
> reserved or changed, and the Ample listing copy remains repository-only.
> `store/identity.json` is now verified against that existing-product identity,
> so a fresh candidate may be built. Reserving the Ample display name remains
> owner-only and must happen before submission.

> **Current correction — 2026-08-19:** the opening paragraph and Partner Center
> state below are historical Hearth observations from 2026-07-14 that were
> mechanically renamed in prose. No Ample AppX exists, Partner Center has not
> been reobserved after the rename, and `store/identity.json` remains unverified.
> CAND-002 and all earlier packages are never-submit. Resume from
> `store/GET-LISTED-RUNBOOK.md` and the dated reset in
> `store/WINDOWS-VALIDATION.md`.

> **Execution correction — 2026-08-26:** AMPLE-001 is repository- and
> CI-complete, but no Ample package, copy, category, price, screenshot, or
> release-control field has been saved or revalidated in Partner Center. Any
> operative-looking statement or checked Partner Center item below describes
> either the historical Hearth draft observed on 2026-07-14 or repository/CI
> readiness. It is not current Ample submission evidence. Preserve those older
> statements as history and execute from the dated corrections plus
> `store/GET-LISTED-RUNBOOK.md`.

This directory is the manual submission source for Ample's reserved Microsoft
Store product. Submission 1 now contains the exact validated 1.1.0 AppX, saved
$14.99 US pricing, reviewed copy, categories, properties, certification notes,
and five hash-matched screenshots. It is deliberately held in draft and has not
been submitted, certified, published, or verified purchasable.

## Launch position

_Listing-copy correction 2026-08-19: the prepared Store copy now leads with
Ample's Windows availability; privacy remains supporting proof. The older
privacy-first sentence below records the pre-review framing._

Ample launches as a **privacy-first Windows energy planner for ADHD and other
variable-capacity days**.

The primary job is simple: let someone choose a 4–24 daily energy budget and put
a realistic amount of work into the day they actually have. Ample never infers
or changes that capacity from a diagnosis or check-in. Check-ins, practices,
rhythm, and crisis-plan text are secondary tools. ERP notes, diary cards,
medication-reference modules, and legacy condition-label metadata remain
preserved outside the default experience pending dedicated opt-in and safety
review.

The proposed offer is a one-time **$14.99** x64 Microsoft Store package. The
source remains MIT licensed. A purchase pays for an official packaged binary and
Store delivery, not exclusive source code, clinical capability, or guaranteed
future features.

## Current Partner Center state

> **State boundary — 2026-08-26:** the field-completion list below is the
> historical Hearth Submission 1 observation. On 2026-08-25 only product
> identity, app names, and the draft overview were reobserved: identity remains
> `ToledoTechnologies.Hearth`, only Hearth is reserved, and the displayed AppX
> is historical. The Ample listing fields remain repository-only.

- Product ID: 9PLRSZZMFPJH
- Submission ID: 1152921505701225649
- Pricing and availability: Complete
- Properties: Complete
- Age ratings: the existing low-rating draft is not accepted as accurate; the
  owner must manually retake IARC against all packaged crisis/self-harm and
  medication-reference content and accept IARC's legal terms
- Packages: Complete; only Ample 1.1.0.appx, marked Validated
- Store listings: Complete
- Submission options: Partner Center displays Incomplete even though the
  runFullTrust explanation and Additional Testing Information are saved;
  restricted-capability review is expected during certification
- Submit for certification: enabled, intentionally not clicked
- Release control: Do not publish until I select Publish now

## Submission sources

- listing-metadata.json — reviewed copy, product features, category, launch
  market, disclosures, and fields that must remain blank until verified
- SCREENSHOTS.md — exact capture order, captions, dimensions, and acceptance
  checks
- CAMPAIGNS.md — Store-link campaign IDs and measurement rules
- PRODUCT-PAGE-EXPERIMENTS.md — post-launch icon/screenshot test plan
- LAUNCH_KIT.md — drafts for owner-approved launch actions; nothing is sent
- WINDOWS-VALIDATION.md — exact-package automated evidence, Store certification,
  installed smoke, and accessibility evidence checklist
- POST_PUBLICATION_DOC_SWEEP.md — pre-drafted replacement paragraphs for every
  pre-release status line, applied on publication day (playbook step 4)
- identity.json — observed existing-product package identity; the Ample display
  name reservation is a separate owner gate

The static commercial landing artifact lives in landing/. It is intentionally
marked pre-release and can be deployed later to an eligible zero-cost static
host. It must not be deployed with a purchase button until the Store listing is
actually live.

## Build and package evidence

The AppX target is x64 and must run on Windows:

    npm ci
    npm run licenses
    npm run brand-assets
    npm run store:validate
    npm run build:winstore

`npm run store:check` must print `true`. `npm run brand-assets` regenerates the
shipping art deterministically; review the resulting diff and provenance file.
`npm run store:validate` checks listing limits, required documents, URLs, local
links, and static-landing invariants without adding a dependency. A successful
build or validator run proves only that specific result. The exact candidate is
an unsigned Store-submission package; Microsoft documents that it re-signs the
package after certification. Adding a local test signature would change the
package bytes and cannot become evidence for the accepted hash. Follow
WINDOWS-VALIDATION.md and preserve every observation against the matching
package and Store-signed release.

The Windows Store workflow also launches the extracted exact candidate against
real Windows `safeStorage`/DPAPI. Its sentinel-guarded validation covers fresh
encrypted persistence, corrupt-primary rollback, export contents, explicit and
interrupted erase, representative legacy migration with consent gating, and
missing-key fail-closed behavior. The resulting `release-validation.json` ships
beside the AppX artifact. This materially narrows the manual matrix; it does not
replace Microsoft certification or assistive-technology and presentation
testing in an active Windows desktop session.

## Verified source behavior

The source now runs SQLite in memory while Ample is open and persists
versioned, authenticated AES-256-GCM snapshots at rest. Each successful write
uses a fresh random IV. A random 256-bit key is protected by Electron
`safeStorage`—DPAPI on Windows—and the app fails closed if secure OS-backed key
storage is unavailable.

Legacy migration is deliberately conservative: Ample verifies an encrypted
migration backup and encrypted primary before removing plaintext database files.
The migration backup is temporary and is retired after two verified encrypted
generations. The rolling encrypted backup remains. This source-level result is
not a substitute for testing the exact packaged Windows migration path.

The limits remain part of every release claim: records and the key are decrypted
in process memory while Ample is open; the OS may copy memory to swap,
hibernation, crash, or diagnostic storage; control of the signed-in OS session
weakens the boundary; JSON and PDF exports are plaintext by user choice; and
deleting old files cannot guarantee removal from SSD recovery, snapshots, or
backups.

Shipping brand art is generated deterministically by
`scripts/generate-brand-assets.mjs`. Its authorship and MIT licensing are
recorded in `resources/BRAND_PROVENANCE.md`; earlier undocumented PNGs are
vaulted and excluded from packaging.

## Screenshot capture

The screenshot driver creates five 1920 × 1080 PNG files with seeded,
non-customer demo data. It now gives product frames an explicit screenshot-only
privacy-consent timestamp so they do not fall back to onboarding.

Set AMPLE_SHOT_BUILD_REF to the exact candidate commit when running the capture
process and save the output under a new directory. Do not mix frames from
different builds. Follow SCREENSHOTS.md and retain the generated files only after
all visual and content checks pass.

## Hard pre-submission blockers

> **Checklist boundary — 2026-08-26:** checked source/CI preparation remains
> valid where it is tied to AMPLE-001. Checked Partner Center entry or upload
> items below are historical Hearth observations and must be re-entered or
> explicitly reverified by the owner for Ample before submission.

### Product and data protection

- [x] Confirm every first-run consent and privacy disclosure against the exact
      release behavior.
- [x] Run the full quality gate, including `npm run store:validate`, against the
      exact release commit.
- [x] On supported Windows CI, test a representative legacy migration through two
      verified encrypted generations and confirm the temporary migration backup
      and all legacy plaintext files are retired as designed.
- [x] On supported Windows CI, verify fail-closed behavior for missing or unusable
      protected key material without destroying recoverable encrypted data.
- [ ] Submit the exact hash-recorded AppX to Microsoft certification after the
      IARC legal step; preserve the certification report and any failure detail.
- [ ] Before public release, smoke-test the Microsoft-signed build on supported
      Windows using fictional data and complete the manual accessibility matrix.

### Rights, safety, and support

- [x] Document ownership, provenance, redistribution rights, and AI-assistance
      status for the deterministically generated shipping brand assets; keep
      vaulted unverified assets excluded.
- [x] Reconfirm the generated assets and provenance file are unchanged in the
      exact package and screenshot candidate.
- [x] Enable GitHub Issues for all signed-in users and replace the unsafe legacy
      templates with privacy-guarded bug and feature forms.
- [x] Publish an unauthenticated support landing page; disclose that creating a
      GitHub issue requires a free account and sign-in.
- [ ] Review the IARC questionnaire disclosures in listing-metadata.json and
      complete the rating honestly in Partner Center.
- [x] Recheck all medical, emergency, privacy, security, and medication language
      against the exact app.

### Listing and conversion

- [x] Confirm Productivity as the primary category and Health + fitness as the
      secondary category.
- [x] Confirm a United States / en-US first release or complete additional
      localization and emergency-resource review before adding markets.
- [x] Generate at least four accepted desktop screenshots from the exact release
      commit, add captions, and confirm no private data or unshipped behavior is
      shown.
- [x] Verify the minimum OS, x64 architecture, AppX size, and supported input
      fields from the exact package.
- [ ] Measure the installed footprint and finish installed-Windows
      accessibility fields.
- [x] Merge the final privacy, terms, and refund documents to main and verify
      their public URLs.
- [x] Set the support URL to the public support page and link from there to the
      privacy-guarded issue forms.
- [ ] Confirm seller, tax, and payout readiness before certification; the
      proposed $14.99 one-time price is saved in the held draft but is not live.

### Partner Center

> **Current execution correction — 2026-08-26:** the two checked rows below
> record the old Hearth draft, not completed Ample work. The owner still must
> reserve Ample, upload only AMPLE-001, save/review the platform-first listing
> and screenshots, and confirm audience/release control before certification.

- [x] Select Public audience and Make this product available and discoverable in
      the Store.
- [x] Enter the reviewed description, product features, seven keywords,
      categories, markets, system requirements, declarations, and screenshots.
- [ ] Before certification, confirm the uploaded package is still the exact
      hash-recorded AppX accepted by the Windows workflow and Partner Center.
- [ ] Review every legal declaration and final URL as the signed-in owner.
- [ ] Submit manually and record the submission ID and time in the evidence
      ledger.

## Certification and publication playbook (owner-gated)

Condensed from the retired long handoff on 2026-07-24; owner-action detail
stays in `revenue/HUMAN_QUEUE.md`.

**While waiting on owner gates:** keep the draft, public policies, support
surface, and CI healthy; reverify current Store policies before any platform
change; do not build Bet B merely to avoid the certification task — start it
only when the active plan/falsifier or a recorded blocker justifies the pivot.
A docs-only or analysis cycle still needs a visible shipment and all six
revenue state files updated.

**Pre-submission (after HQ-01 and HQ-02):** re-read all six revenue files;
verify only the accepted package remains in the draft and is Validated; verify
the hold still reads **Do not publish until I select Publish now**; verify
policy/support/privacy/terms/refund URLs signed out; record the IARC outcome
and payout-ready boolean without private details; confirm the Private/Public
test-route choice (HQ-03).

**During certification:** Microsoft review time is machine wait — monitor
without changing the package or claims. On failure: preserve and redact the
report, log it in METRICS/DECISIONS, fix the narrow real cause, and create a
completely new candidate and evidence chain if runtime/package bytes change.
Never weaken a truthful disclosure to pass. On success: do not release the
hold yet.

**After certification, before publication:** install the Microsoft-signed build
through the HQ-03 route; run the smoke matrix — first render, consent
accept/decline, 4–24 capacity persistence, task, check-in, practice,
crisis-plan edit, JSON/PDF export with plaintext warnings, erase, full
quit/relaunch, identity/footprint; run the accessibility matrix — keyboard-only,
Narrator, focus, high contrast/forced colors, 200% text scaling, minimum
window, reduced motion, light/dark, modal focus. Make no formal accessibility
claim until that passes. Confirm payout readiness and the signed-out page
preview. The owner then clicks **Publish now**.

**Immediately after publication:**

1. Verify the exact public page and paid checkout in a signed-out browser
   (expected pattern `https://apps.microsoft.com/detail/9PLRSZZMFPJH`; do not
   distribute the URL before observation). Change no call to action to “Get
   Ample” until the page is visibly purchasable.
2. Record the observed Store URL, price, timestamp, package/version, and status
   in `revenue/METRICS.md`.
3. Replace the null Store URL in `store/listing-metadata.json` and set its live
   release state.
4. Update every pre-release status line to only what is observed: README.md,
   docs/SUPPORT.md, docs/TERMS.md, docs/REFUNDS.md, SECURITY.md, docs/PRIVACY.md
   (re-check for status lines even though none are known today), the store
   docs, and landing copy. Pre-drafted replacement paragraphs for each file
   live in store/POST_PUBLICATION_DOC_SWEEP.md — apply them same-day with the
   observed Store URL and price instead of writing fresh copy under time
   pressure.
5. Deploy `landing/` to an eligible zero-cost static host (never GitHub Pages —
   D007), then wire the source-specific links in CAMPAIGNS.md.
6. Run full verification, publish the doc/link changes, and record evidence.
7. Record Store page views, acquisitions, installs, usage, health, reviews,
   refunds, and payout evidence as they arrive. Do not install third-party
   analytics merely to create a launch chart, and do not run a product-page
   experiment until traffic can compare one asset change against the baseline
   (PRODUCT-PAGE-EXPERIMENTS.md).
8. The owner executes HQ-05. No agent posts or contacts humans.

Owner-only actions remain governed by revenue/HUMAN_QUEUE.md. Draft launch copy
does not authorize posting, messaging, promising, pricing, or publishing as the
owner.
