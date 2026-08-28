# Microsoft Store screenshot plan

> **Paulatim correction — 2026-08-28:** every AMPLE-001 image and hash below
> remains historical and must never accompany Paulatim. The fresh Paulatim
> workflow must capture a new exact-SHA five-image set. Use the Paulatim caption
> table added below only after its manifest is downloaded and independently
> verified; nothing in this correction claims those images exist yet.

> **Current candidate correction — 2026-08-26:** the status line and
> "Accepted candidate evidence" section below record the historical Hearth
> draft observed on 2026-07-14. AMPLE-001 has a new exact set from source
> `3b8d225`, screenshots artifact `9561704379`, staged under
> `tmp/AMPLE-001-3b8d225/downloads/screenshots/`. All five files are 1920 ×
> 1080 and their hashes match that artifact's manifest. They have **not** been
> uploaded or saved in Partner Center. Only this AMPLE-001 set may accompany
> AppX `7d6ca584…61866b`; the older hashes remain history, not upload choices.

Status: **captured, accepted, hash-recorded, and uploaded to the held Partner
Center draft; not public**

The source driver in electron/screenshot.ts creates five desktop PNG files at
1920 × 1080. The data is a deterministic fictional demo owned by the screenshot
process; customer records must never be used. It also writes manifest.json with
the candidate reference, dimensions, byte counts, SHA-256 hashes, captions, and
an explicit fictional-data marker.

Microsoft requires at least one screenshot and recommends at least four desktop
screenshots. Desktop frames must be PNG, at least 1366 × 768, and no larger than
50 MB. Critical content belongs in the top two-thirds because Store overlays can
cover the lower portion. Do not add marketing text, badges, logos, or claims over
the captured application.

Official requirements:
<https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/screenshots-and-images>

## Final order and captions

| Order | File | Screen | Caption |
|---:|---|---|---|
| 1 | 01-today.png | Today, light | See the energy left today, a plain-language briefing, and open tasks whose recorded cost fits the remaining budget. |
| 2 | 02-tasks.png | Tasks, light | Give work a priority, expected duration, and energy demand; Ample estimates a spoon cost for the plan. |
| 3 | 04-rhythm.png | Rhythm, dark | Review your own mood, energy, and sleep across 7, 14, or 30 days, then request a local PDF summary. |
| 4 | 03-reflect.png | Check in, light | Record mood, energy, anxiety, sleep, or a private journal entry in the local desktop app. |
| 5 | 05-onboarding.png | First run, light | Start without an account and review local-data consent before Ample stores the information you enter. |

The filenames follow the driver output; the Store upload order intentionally
puts Rhythm before Reflect.

## Paulatim upload order and captions — 2026-08-28

| Order | File | Screen | Caption |
|---:|---|---|---|
| 1 | 01-today.png | Today, light | See the energy left today, a plain-language briefing, and open tasks whose recorded cost fits the remaining budget. |
| 2 | 02-tasks.png | Tasks, light | Give work a priority, expected duration, and energy demand; Paulatim estimates a spoon cost for the plan. |
| 3 | 04-rhythm.png | Rhythm, dark | Review your own mood, energy, and sleep across 7, 14, or 30 days, then request a local PDF summary. |
| 4 | 03-reflect.png | Check in, light | Record mood, energy, anxiety, sleep, or a private journal entry in the local desktop app. |
| 5 | 05-onboarding.png | First run, light | Start without an account and review local-data consent before Paulatim stores the information you enter. |

## Accepted candidate evidence

- Candidate: 8172603b62c2457696608c145511bd3fe92429d4
- Capture time: 2026-07-14T09:40:09.782Z
- GitHub artifact ID: 8306519500
- Artifact digest:
  sha256:b03e6e42b771da7f693575d79473275e90723adbeea23801d08f8de380e7c905
- Manifest: tmp/artifacts/final-screenshots/manifest.json
- Partner Center verification: all five uploaded image hashes matched the local
  accepted files byte-for-byte, and the final captions/order were saved.

| File | SHA-256 |
|---|---|
| 01-today.png | e1294c9c6bf869cc13e903932feac540da9122f46af40aa2d776a24ce2d64979 |
| 02-tasks.png | 67708bf4165b4cc9e8be027dfdc3342b33b3b76b84dcd3a983b6573cfdd153af |
| 03-reflect.png | 76e3888e666f2a9f3ed9effc7cc15072621551259274b98ac31723bfb3db93cc |
| 04-rhythm.png | 208e9cca284fec8bf284706f670f698a5e5cd64dc497bea7cbbbc16afb40c483 |
| 05-onboarding.png | 6f49b190a72913d32a83c3e8f2f4f6bb4812a1938a2cf1c051b0372abbbffe99 |

## Capture contract

1. Start from the exact release commit and record that commit as
   AMPLE_SHOT_BUILD_REF.
2. Use a fresh screenshot-only app-data directory. Never point the driver at a
   real user profile.
3. Confirm the seed records a screenshot-only privacy-consent timestamp. The
   driver must fail if a product frame cannot clear the consent gate.
4. Capture only after fonts, the illustration, data, and route transitions have
   settled.
5. Keep raw captures free of added copy, logos, frames, cursor artifacts, OS
   notifications, and private information.
6. Record dimensions, file sizes, SHA-256 hashes, candidate commit, and capture
   time beside the package evidence.

Example from the workspace root, with the output path kept inside the jail:

    AMPLE_SCREENSHOT=1 \
    AMPLE_SHOT_BUILD_REF="$(git rev-parse HEAD)" \
    AMPLE_SHOT_DIR="$PWD/screenshots/candidate" \
    npm run dev

Review manifest.json rather than reconstructing hashes from memory. A null build
reference rejects the set for release use.

## Visual acceptance checklist

- [x] Every file is exactly 1920 × 1080 PNG and under 50 MB.
- [x] Every frame comes from the same accepted candidate commit.
- [x] The displayed data matches the fictional seed and contains no customer
      identifiers.
- [x] Today communicates the primary energy-planning job without relying on the
      caption.
- [x] No frame claims that all tasks are energy-sorted; only the Today
      recommendations are filtered to tasks that fit.
- [x] No clipped content, unexpected onboarding gate, broken utility class,
      missing icon, blank chart, hidden focus state, or scrollbar collision is
      visible.
- [x] Light and dark frames both pass a manual readability and contrast check.
- [x] The top two-thirds contains the important UI.
- [x] Captions describe only behavior visible in the accepted release.
- [x] Shipping asset provenance is documented through the deterministic brand
      generator and `resources/BRAND_PROVENANCE.md`; vaulted unverified assets
      are excluded.
- [x] The exact candidate reproduces the documented assets without an
      unexpected diff before any image is uploaded.

## Rejection conditions

Reject and recapture the entire set if the package commit changes, consent or
encryption behavior changes, listing claims change materially, a frame exposes
real data, or Windows smoke testing finds a visual difference from the captured
build.
