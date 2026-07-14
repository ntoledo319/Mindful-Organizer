# Microsoft Store screenshot plan

Status: **planned, not captured from an accepted release candidate**

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
| 2 | 02-tasks.png | Tasks, light | Give work a priority, expected duration, and energy demand; Hearth estimates a spoon cost for the plan. |
| 3 | 04-rhythm.png | Rhythm, dark | Review your own mood, energy, and sleep across 7, 14, or 30 days, then request a local PDF summary. |
| 4 | 03-reflect.png | Check in, light | Record mood, energy, anxiety, sleep, or a private journal entry in the local desktop app. |
| 5 | 05-onboarding.png | First run, light | Start without an account and review local-data consent before Hearth stores the information you enter. |

The filenames follow the driver output; the Store upload order intentionally
puts Rhythm before Reflect.

## Capture contract

1. Start from the exact release commit and record that commit as
   HEARTH_SHOT_BUILD_REF.
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

    HEARTH_SCREENSHOT=1 \
    HEARTH_SHOT_BUILD_REF="$(git rev-parse HEAD)" \
    HEARTH_SHOT_DIR="$PWD/screenshots/candidate" \
    npm run dev

Review manifest.json rather than reconstructing hashes from memory. A null build
reference rejects the set for release use.

## Visual acceptance checklist

- [ ] Every file is exactly 1920 × 1080 PNG and under 50 MB.
- [ ] Every frame comes from the same accepted candidate commit.
- [ ] The displayed data matches the fictional seed and contains no customer
      identifiers.
- [ ] Today communicates the primary energy-planning job without relying on the
      caption.
- [ ] No frame claims that all tasks are energy-sorted; only the Today
      recommendations are filtered to tasks that fit.
- [ ] No clipped content, unexpected onboarding gate, broken utility class,
      missing icon, blank chart, hidden focus state, or scrollbar collision is
      visible.
- [ ] Light and dark frames both pass a manual readability and contrast check.
- [ ] The top two-thirds contains the important UI.
- [ ] Captions describe only behavior visible in the accepted release.
- [x] Shipping asset provenance is documented through the deterministic brand
      generator and `resources/BRAND_PROVENANCE.md`; vaulted unverified assets
      are excluded.
- [ ] The exact candidate reproduces the documented assets without an
      unexpected diff before any image is uploaded.

## Rejection conditions

Reject and recapture the entire set if the package commit changes, consent or
encryption behavior changes, listing claims change materially, a frame exposes
real data, or Windows smoke testing finds a visual difference from the captured
build.
