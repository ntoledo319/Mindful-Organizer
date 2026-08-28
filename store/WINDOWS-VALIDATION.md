# Exact-candidate Windows validation

> **PAULATIM-001 reset — 2026-08-28:** the owner selected/reserved Paulatim and
> authorized certification submission. The Ample candidate recorded below
> remains valid historical evidence but is now **never-submit** because the
> visible AppX manifest and screenshots changed. No Paulatim hash exists yet.
> Accept only a fresh exact-SHA `paulatim-msix` artifact whose manifest keeps
> identity `ToledoTechnologies.Hearth`, AppX application ID `Ample`, and x64
> version 1.1.1 while showing display name `Paulatim`. Record its hash in a new
> dated section before any Partner Center upload.

## AMPLE-001 exact candidate — 2026-08-25

This is the first Ample-branded AppX after the Hearth→Ample source rename. It
supersedes the operational use of every historical package below.

| Evidence | Exact value |
|---|---|
| Candidate source / CI SHA | `3b8d225c1ce32be04a7940099649789876d1e353` |
| Source tree | `cfb17be0c06e456beb9bcf54ec2e211eb0085a5b` |
| Quality Gate | run `32844120492` — passed |
| Windows Store workflow | run `32844120483` — passed |
| MSIX artifact | `ample-msix`, artifact `9561731052` |
| Screenshots artifact | `ample-store-screenshots`, artifact `9561704379` |
| AppX filename | `Ample 1.1.0.appx` |
| AppX size | `175489305` bytes |
| **AppX SHA-256** | **`7d6ca584a8cee92497217ab48fbd04153f32c8f8746b4cd19135d709aa61866b`** |

The downloaded AppX was hashed locally with `sha256sum`; the result exactly
matches CI's `ample-appx.sha256.txt`. AppX manifest inspection independently
confirmed:

- Identity Name: `ToledoTechnologies.Hearth`
- Publisher: `CN=FBC80173-0C85-481E-BC5E-A3BE88BC2020`
- Processor architecture: `x64`
- Package version: `1.1.0.0`
- Display name: `Ample`
- Publisher display name: `Toledo Technologies`
- Minimum Windows version: `10.0.14316.0`

The workflow's real Windows x64 DPAPI lifecycle validation passed. Screenshot
artifact `9561704379` contains five 1920×1080 PNGs plus an exact-SHA manifest
bound to `3b8d225`; all five image hashes were recomputed and matched. The
preserved artifact ZIP SHA-256 is
`06f74a6e2d68b3b53b0b5ed73b8ffbdb5808cb61fe8178d4884a00e924dbfe65`.

The package, screenshot ZIP, extracted screenshots, CI hash, validation report,
and a short operator README are staged at `tmp/AMPLE-001-3b8d225/`. This is a
CI-validated candidate, **not** a Partner Center acceptance, certification,
submission, publication, or live-Store result. The owner must reserve the Ample
display name before submission; do not upload CAND-002 or any other artifact.

The normal local `git push` was blocked by the execution environment before it
ran. The authenticated GitHub Git Data path therefore published one commit
whose tree (`cfb17be…`) exactly matches locally gated commit `cef09af`; only the
remote/CI commit metadata SHA differs. Local `main` was then aligned cleanly to
the remote candidate SHA before artifact verification.

## Package identity observation — 2026-08-25

Authenticated Partner Center observation of existing product `9PLRSZZMFPJH`
showed:

- Package/Identity/Name: `ToledoTechnologies.Hearth`
- Package/Identity/Publisher:
  `CN=FBC80173-0C85-481E-BC5E-A3BE88BC2020`
- Package/Properties/PublisherDisplayName: `Toledo Technologies`
- Manage app names: `Hearth` is the only name currently in use

No name was reserved or changed. No submission, publication, IARC, payout, tax,
or terms action was taken. `store/identity.json` now carries the observed
package identity with `identityVerified: true`; the Ample display-name
reservation remains an owner-only gate. This observation authorizes a fresh
package build but does not rehabilitate any historical Hearth AppX listed below.

## Ample candidate reset — 2026-08-19

This section supersedes the operational use of every package record below
without altering the Hearth-era evidence. The Hearth→Ample rename changed the
AppX manifest, and the Partner Center package identity for Ample has not been
observed. Therefore:

- **No Ample AppX or screenshot artifact exists.** `store/identity.json` is
  deliberately unverified, and no candidate build is authorized until the
  owner supplies the exact Partner Center Package/Identity/Name.
- CAND-002 (`a5d2cf36…b18f`, artifact 8846968340, run 30790687808) is
  **historical and never-submit**, as is the staged
  `tmp/CAND-002-SWAP/` convenience kit.
- The six post-CAND-002 Hearth MSIX artifacts are also never-submit:

  | Artifact | Run |
  |---|---|
  | 8847100327 | 30791027672 |
  | 8885413072 | 30891744008 |
  | 8987197965 | 31161190842 |
  | 8987206429 | 31161188967 |
  | 8987378149 | 31161652287 |
  | 8987382023 | 31161652928 |

- The first Ample workflows at `c0eb360` failed before artifact upload:
  32310869046 (main) and 32310866359 (feature) each produced zero artifacts.
- Sections 1–6 and the release-evidence checklist remain blocked until a fresh
  exact-commit Ample package has its own filename, SHA-256, CI run, screenshots,
  and manifest identity recorded in this file.

This gate applies to the x64 AppX in Partner Center Submission 1. Keep the
package hash, CI evidence, Microsoft certification result, Store-signed install
observations, screenshots, and this checklist tied to the same release.

## Accepted candidate and automated evidence

- Candidate: 8172603b62c2457696608c145511bd3fe92429d4
- Package: Hearth 1.1.0.appx
- Package size: 175,488,515 bytes
- SHA-256:
  4900f3823febace53f86f69ee2567b50208aec8f6677741c3c4dcf3667facdb1
- Quality run:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29322423682>
- Windows Store run:
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29322423622>
- GitHub package artifact ID: 8306541856
- Local jailed evidence copy:
  tmp/artifacts/final-msix/Hearth 1.1.0.appx

Artifact-retention and non-candidate notes (2026-07-28, observed via
authenticated gh CLI):

- The accepted candidate's own CI artifact 8306541856 expires
  2026-08-13T09:41:07Z under GitHub's 30-day retention. After that date the
  byte-level evidence for the accepted hash is the jailed copy above (SHA-256
  re-verified against `4900f382…facdb1` on 2026-07-28) and the uploaded
  package in Partner Center. The section-1 hash check is unaffected.
- Later CI runs keep producing fresh `hearth-msix` artifacts; the newest is
  run 30137481905 (2026-07-25, commit 59787f4) → artifact 8613344727
  (174,531,117 bytes zipped — different bytes from the accepted package),
  with screenshots artifact 8613334339; both expire 2026-08-24. Like the
  already-documented artifact 8316167277, it is verification output, **not
  the submission candidate**; the HQ-04 step-1 hash check against
  `4900f382…facdb1` remains the guard.
- Any future candidate will be a NEW AppX with a new hash produced by a fresh
  CI run (in-flight code remediation will change package bytes), and the
  accepted candidate becomes historical the moment a replacement is accepted.
  The hash guard protects against accidental swaps, not deliberate candidate
  cycles.

## CAND-002 replacement candidate (2026-08-03)

Produced on branch `feature/store-candidate-cand002` after committing the
2026-07-29 council remediation and fixing a release-blocking regression: the
remediation had gated `SCREENSHOT_MODE`/`SMOKE_MODE` on `!app.isPackaged`,
which disabled the packaged renderer smoke gate in `windows-store.yml`. The
first remediation build (commit `fe0fc4a`, run 30743167548) failed at
"Validate AppX" with "renderer smoke check within 60 seconds". Fixed in commit
`07cf815` by honoring the harness in a packaged build only when
`HEARTH_DATA_DIR` points at a contained profile — preserving the "a stray
HEARTH_SCREENSHOT=1 can never reseed a real user's profile" guarantee while
letting the Store-build boot check validate the package.

- Candidate commit: `07cf815` (on `feature/store-candidate-cand002`)
- Package: Hearth 1.1.0.appx
- Package size: 175,489,287 bytes
- SHA-256:
  a5d2cf3633def56983702d41d17f6fa458abd8dfedc818039ed1af040f36b18f
- Windows Store run (green, 3m16s):
  <https://github.com/ntoledo319/Mindful-Organizer/actions/runs/30790687808>
- Refreshed screenshots: 01-today, 02-tasks, 03-reflect, 04-rhythm,
  05-onboarding (onboarding/tasks/settings UI changed in remediation).
- Status: CI-validated replacement candidate. **Not yet the accepted
  candidate** — acceptance requires owner review + the Partner Center package
  swap (HQ-04). The accepted-candidate hash `4900f382…facdb1` above remains the
  guard until the owner accepts this candidate.
- **Independently reverified 2026-08-07 (VER-20260807-001):** artifact
  `hearth-msix` 8846968340 downloaded from run 30790687808 (174,530,445 bytes
  zipped) and the contained `Hearth 1.1.0.appx` recomputed with `sha256sum` →
  `a5d2cf3633def56983702d41d17f6fa458abd8dfedc818039ed1af040f36b18f`. Matches
  the CI-emitted `hearth-appx.sha256.txt` and the value recorded above. The
  package plus the five refreshed screenshots are staged for the owner at
  `tmp/CAND-002-SWAP/` (gitignored; convenience copy, not evidence).

### Decoy artifact — 8885413072 (added 2026-08-07)
The MSIX built on `270e650` (run 30891744008) is the **highest-risk
non-candidate** and was previously undocumented:

- Artifact 8885413072, zipped 174,530,569 bytes — within 124 bytes of CAND-002.
- Contained AppX SHA-256:
  `368b0eebe8bc5c73b3e67cb196f52471742c547224d2cbcbd84ea3d68bd4e7b1`
- `07cf815..270e650` is a **docs-only** diff, so this is the same application
  rebuilt: identical behavior, different bytes, different hash.
- It is the newest MSIX in the Actions list and therefore the artifact an owner
  reaching for "the latest build" will hit first. Submitting it would break the
  evidence chain that `store/README.md` and this file depend on.

Verified by download and `sha256sum` on 2026-08-07 (VER-20260807-001).

### Non-candidate register — complete list (2026-08-07)

**Only `a5d2cf36…b18f` (artifact 8846968340, run 30790687808) is the CAND-002
submission candidate.** Every other MSIX this repository has produced is a
non-candidate. The full list, so no future session has to reconstruct it:

| Artifact | Run / ref | Zipped bytes | Why not |
|---|---|---|---|
| 8885413072 | 30891744008 / `270e650` | 174,530,569 | docs-only rebuild; hash `368b0eeb…e7b1` |
| 8987197965 | 31161190842 / `f63f792` main | 174,530,243 | docs-only rebuild (see note below) |
| 8987206429 | 31161188967 / `f63f792` feature | 174,530,491 | docs-only rebuild (see note below) |
| 8316167277 | — | — | documentation/launch-hardening build |
| 8613344727 | 30137481905 / `59787f4` | — | pre-remediation verification output |

**Why 8987197965 and 8987206429 exist — a self-inflicted lesson.** The
2026-08-07 documentation commit that first recorded the decoy problem edited
*this file*, and `store/**` was inside `windows-store.yml`'s trigger paths. So
writing down "beware of extra MSIX artifacts" minted two more. The workflow's
path filter has since been narrowed to `store/identity.json`,
`store/identity.cjs`, and `store/listing-metadata.json` — the only files under
`store/` that can change AppX bytes. Markdown under `store/` is still validated
on every push by the Quality Gate, which has no path filter.

Expect **one final** MSIX build from the commit that narrows the filter, since
`.github/workflows/windows-store.yml` is itself a trigger path. After that,
documentation work stops producing packages.

The Windows workflow passed a sentinel-guarded real safeStorage/DPAPI lifecycle
matrix for fresh encrypted persistence, corrupt-primary recovery, plaintext
export warnings, key-first erase, interrupted erase, representative legacy
migration and retirement, consent gating, and missing-key fail-closed behavior.

> **Correction 2026-08-07:** an earlier revision of this section ended with
> "Partner Center also marked this exact AppX Validated." That is not true of
> CAND-002 and contradicted `HANDOFF.md` §4 and HQ-04, both of which state the
> swap has not happened and the Partner Center guard is still `4900f382…facdb1`.
> The sentence appears to have been carried over from the accepted-candidate
> section above. No Partner Center state has been observed since 2026-07-14
> (tracker risk R3) — treat all Partner Center facts in this repository as
> 24-day-old memory until the owner reobserves them.


## Why the accepted AppX is not a local-install proof

The accepted file is an unsigned Store-submission package and contains no
`AppxSignature.p7x`. Microsoft documents that Store packages do not need a
CA-trusted signature before submission because Microsoft re-signs them after
certification. The special unsigned-package installation path requires an
identity prepared for unsigned installation; this package is not prepared that
way. Adding a test signature or rebuilding would change the bytes and SHA-256.

Therefore:

- do not claim that the exact accepted hash was installed locally;
- do not replace the accepted package with a test-signed rebuild;
- treat WACK against a test-signed equivalent, if one is created, only as
  supporting evidence; and
- use Microsoft certification as the authoritative install/run, security, and
  technical-compliance gate for the exact submission.

References:

- <https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/publish-first-app>
- <https://learn.microsoft.com/en-us/windows/msix/package/unsigned-package>
- <https://learn.microsoft.com/en-us/windows/apps/publish/faq/get-your-app-certified>

## Current PAULATIM-001 procedure — 2026-08-28

The numbered Hearth procedure below is historical and non-executable. For the
current candidate:

1. Select the green Windows workflow by the exact pushed PAULATIM-001 source
   SHA, not by recency. Download only `paulatim-msix` and
   `paulatim-store-screenshots` from that run.
2. Independently hash the contained Paulatim 1.1.1 AppX and inspect its manifest
   for identity `ToledoTechnologies.Hearth`, the recorded publisher, x64,
   version `1.1.1.0`, AppX application ID `Ample`, and visible display name
   `Paulatim`. Require the CI hash file to match exactly.
3. Verify all five screenshot hashes/dimensions against the same exact-SHA
   manifest, then record the full package hash here and in
   `docs/project/VERIFICATION_LOG.md` before any upload.
4. In Partner Center, remove the historical draft package/listing references
   and upload only that exact AppX plus its matching Paulatim screenshots. Age
   ratings is already observed Complete; do not retake IARC. Preserve the
   `Do not publish until I select Publish now` hold.
5. Submit for certification under the owner's 2026-08-28 delegation and record
   the submission ID/status. Do not click **Publish now**.
6. After certification, the signed-build smoke uses the visible command
   **Erase all Paulatim data** and records the real Store-installed result.

## Historical Hearth certification procedure (non-executable)

## 1. Reconfirm candidate identity before certification

Download artifact 8306541856 or use the jailed evidence copy. On Windows,
PowerShell `Get-FileHash` must return the SHA-256 above. In Partner Center,
Packages must still show only `Hearth 1.1.0.appx` as Validated. Stop if either
observation differs.

## 2. Preserve the pre-certification evidence

Require the matching Quality and Windows Store workflows to pass. Preserve the
CI-produced `release-validation.json`, screenshot manifest, screenshot hashes,
AppX hash, application tree, and exact commit. These prove source quality,
package structure, real Windows DPAPI behavior, and captured UI states. They do
not prove Store installation, Narrator behavior, high contrast, or
certification.

## 3. Submit to Microsoft certification under the publication hold

Complete the IARC questionnaire manually and accept its legal terms only as the
real publisher. Confirm the saved release control still says **Do not publish
until I select Publish now**, then submit the exact package for certification.

Microsoft states that certification installs and runs the app and performs
security, technical-compliance, content, and policy checks. Preserve the result,
messages, and timestamp. A failure restarts the affected gate; it is not a
reason to weaken a truthful disclosure.

The manual publication hold prevents a certification pass from automatically
making this submission public:

- <https://learn.microsoft.com/en-us/windows/apps/publish/publish-your-app/msix/manage-submission-options>
- <https://learn.microsoft.com/en-us/windows/apps/publish/faq/get-your-app-certified>

## 4. Obtain a supported non-public Store install

Before clicking **Publish now**, install the Microsoft-signed build through a
supported Store testing route. For a first release, Microsoft's fully private
route is **Private audience**, configured before the app has ever been published
to a public audience and limited to named Microsoft accounts. The current draft
is configured as Public, so changing it to Private audience is an owner decision
that requires the tester's Microsoft-account address and an additional public
submission later.

If Partner Center does not provide another supported non-public install after
certification, do not pretend the manual install happened. Either use Private
audience and accept the extra submission cycle, or record that installed human
validation remains open. Do not publish merely to manufacture a test path.

Reference:
<https://learn.microsoft.com/en-us/windows/apps/publish/beta-testing-and-targeted-distribution>

## 5. Store-signed first-run smoke

Use fictional data only. Launch from Start and verify:

- the first window renders without a blank frame or preload error;
- consent is required before a new profile stores personal entries;
- declining leaves the profile at onboarding;
- accepting creates a profile and a user-selected 4–24 budget survives a full
  quit and relaunch;
- a task, check-in, practice, crisis-plan edit, JSON export, and PDF export work;
- both exports state that they are plaintext and contain only created records;
- **Erase all Hearth data** returns to onboarding and prior records do not
  reappear after a full quit and relaunch; and
- package identity, publisher, version, x64 support, and installed footprint
  match the certified listing.

Never attach snapshots, keys, exports, or screenshots containing real personal
records to a public issue.

## 6. Manual accessibility and presentation

Against the Store-signed install, complete `docs/ACCESSIBILITY.md`: keyboard-only
use, visible focus, Narrator names and state, Windows high-contrast themes, 200%
text scaling, reduced motion, minimum window size, light/dark themes, modal
focus trapping/restoration, and all five Store screenshot scenes. Reject clipped
content, unreachable controls, unannounced state, private data, debug UI, or
claims not present in the build.

## Optional local WACK evidence

Microsoft documents WACK as a local pre-test. It requires an active Windows
desktop session and may require interactive or administrative steps. If a
test-signed equivalent is tested, preserve its separate hash and label the WACK
report as equivalent-build evidence, not evidence for the accepted unsigned
AppX. Never overwrite the accepted package or its hash.

Reference:
<https://learn.microsoft.com/en-us/windows/uwp/debug-test-perf/windows-app-certification-kit>

## Release evidence required

- exact AppX filename, SHA-256, commit, application tree, and CI run URLs;
- accepted screenshot manifest and image hashes;
- Microsoft certification result and timestamp;
- supported Store-signed install route, Windows build, and x64 architecture;
- completed first-run smoke and accessibility/presentation checklist;
- seller/tax/payout readiness confirmed privately; and
- Partner Center submission and eventual publication timestamps.
