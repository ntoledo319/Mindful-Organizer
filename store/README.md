# Microsoft Store release path

This directory is the manual submission source for Hearth's reserved Microsoft
Store product. Submission 1 now contains the exact validated 1.1.0 AppX, saved
$14.99 US pricing, reviewed copy, categories, properties, certification notes,
and five hash-matched screenshots. It is deliberately held in draft and has not
been submitted, certified, published, or verified purchasable.

## Launch position

Hearth launches as a **privacy-first Windows energy planner for ADHD and other
variable-capacity days**.

The primary job is simple: let someone choose a 4–24 daily energy budget and put
a realistic amount of work into the day they actually have. Hearth never infers
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

- Product ID: 9PLRSZZMFPJH
- Submission ID: 1152921505701225649
- Pricing and availability: Complete
- Properties: Complete
- Age ratings: Complete, with the existing IARC 3+ / ESRB Everyone result still
  requiring owner affirmation against packaged crisis/self-harm references
- Packages: Complete; only Hearth 1.1.0.appx, marked Validated
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
- WINDOWS-VALIDATION.md — exact-package install, DPAPI/recovery, WACK, and
  accessibility evidence checklist
- identity.json — reserved Partner Center package identity

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
build or validator run proves only that specific result. The exact candidate
still needs installation, launch, feature, accessibility, security, and Windows
App Certification Kit verification on supported Windows. Follow
WINDOWS-VALIDATION.md and preserve its evidence against the matching package
hash.

The Windows Store workflow also launches the extracted exact candidate against
real Windows `safeStorage`/DPAPI. Its sentinel-guarded validation covers fresh
encrypted persistence, corrupt-primary rollback, export contents, explicit and
interrupted erase, representative legacy migration with consent gating, and
missing-key fail-closed behavior. The resulting `release-validation.json` ships
beside the AppX artifact. This materially narrows the manual matrix; it does not
replace installed-package, separate-account, WACK, or assistive-technology
testing in an active Windows desktop session.

## Verified source behavior

The source now runs SQLite in memory while Hearth is open and persists
versioned, authenticated AES-256-GCM snapshots at rest. Each successful write
uses a fresh random IV. A random 256-bit key is protected by Electron
`safeStorage`—DPAPI on Windows—and the app fails closed if secure OS-backed key
storage is unavailable.

Legacy migration is deliberately conservative: Hearth verifies an encrypted
migration backup and encrypted primary before removing plaintext database files.
The migration backup is temporary and is retired after two verified encrypted
generations. The rolling encrypted backup remains. This source-level result is
not a substitute for testing the exact packaged Windows migration path.

The limits remain part of every release claim: records and the key are decrypted
in process memory while Hearth is open; the OS may copy memory to swap,
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

Set HEARTH_SHOT_BUILD_REF to the exact candidate commit when running the capture
process and save the output under a new directory. Do not mix frames from
different builds. Follow SCREENSHOTS.md and retain the generated files only after
all visual and content checks pass.

## Hard pre-submission blockers

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
- [ ] Install and smoke-test the exact hash-recorded x64 MSIX on supported
      Windows.
- [ ] Run the Windows App Certification Kit and preserve its passing result.

### Rights, safety, and support

- [x] Document ownership, provenance, redistribution rights, and AI-assistance
      status for the deterministically generated shipping brand assets; keep
      vaulted unverified assets excluded.
- [x] Reconfirm the generated assets and provenance file are unchanged in the
      exact package and screenshot candidate.
- [ ] Enable the planned GitHub Issues support channel and verify the new-issue
      flow in a private browser.
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
- [x] Keep the support URL blank until issue creation works.
- [ ] Confirm seller, tax, and payout readiness before certification; the
      proposed $14.99 one-time price is saved in the held draft but is not live.

### Partner Center

- [x] Select Public audience and Make this product available and discoverable in
      the Store.
- [x] Enter the reviewed description, product features, seven keywords,
      categories, markets, system requirements, declarations, and screenshots.
- [ ] Before certification, confirm the uploaded package is still the exact
      hash-recorded AppX that passes installed smoke and WACK.
- [ ] Review every legal declaration and final URL as the signed-in owner.
- [ ] Submit manually and record the submission ID and time in the evidence
      ledger.

## After certification

1. Wait until the public product page is visible and purchasable in a private
   browser before changing any call to action to “Get Hearth.”
2. Replace the null Store URL in listing-metadata.json with the observed public
   link.
3. Deploy the static landing page to an eligible zero-cost host, then use the
   source-specific links in CAMPAIGNS.md.
4. Record Store page views, acquisitions, installs, usage, health, reviews,
   refunds, and payout evidence. Do not install third-party analytics merely to
   create a launch chart.
5. Do not run a product-page experiment until there is enough traffic to compare
   one asset change against the baseline.

Owner-only actions remain governed by revenue/HUMAN_QUEUE.md. Draft launch copy
does not authorize posting, messaging, promising, pricing, or publishing as the
owner.
