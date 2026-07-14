# Exact-candidate Windows validation

This gate applies to the exact x64 AppX uploaded to Partner Center. Keep the
package, SHA-256 file, screenshots, Windows App Certification Kit report, and
this completed checklist together. A source build or extracted-package smoke
test does not replace an installed-package test.

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

The Windows workflow passed a sentinel-guarded real safeStorage/DPAPI lifecycle
matrix for fresh encrypted persistence, corrupt-primary recovery, plaintext
export warnings, key-first erase, interrupted erase, representative legacy
migration and retirement, consent gating, and missing-key fail-closed behavior.
Partner Center also marked this exact 1.1.0 AppX Validated.

Still required before certification: install this exact AppX through the
supported Windows package flow, complete the first-run smoke below, run WACK,
and perform the manual accessibility/presentation matrix. Do not treat the
automated lifecycle proof as those missing observations.

## 1. Establish candidate identity

On a supported Windows 11 system, copy the AppX and its CI-produced checksum
into one working directory. In PowerShell:

    Get-FileHash .\Hearth*.appx -Algorithm SHA256

The observed hash must exactly match `hearth-appx.sha256.txt`. Stop if it does
not. Record the Hearth version, Windows edition/build, architecture, test time,
and tester in the release evidence ledger.

## 2. Install and first-run smoke

Install the exact package through the supported AppX installation flow. Launch
it from Start, not from an extracted directory, and verify:

- the first window renders without a blank frame or preload error;
- consent is required before a new profile stores personal entries;
- declining leaves the profile at onboarding;
- accepting creates a profile and a user-selected 4–24 budget survives a full
  quit and relaunch;
- a task, check-in, practice, crisis-plan edit, JSON export, and PDF export work;
- both exports state that they are plaintext and contain only the records the
  user created; and
- **Erase all Hearth data** returns to onboarding and the prior records do not
  reappear after a full quit and relaunch.

Use fictional test data only. Never attach encrypted snapshots, keys, exports,
or screenshots containing real personal records to a public issue.

## 3. DPAPI and recovery matrix

Use a disposable Windows test account and app-data directory. Preserve a copy
of each test fixture before changing it.

- **Legacy migration:** start from a representative pre-encryption `hearth.db`,
  including committed WAL data. Verify the records migrate, `hearth.secure` and
  `hearth.secure.backup` both authenticate through a second persisted
  generation, and the plaintext DB/WAL/SHM/journal plus temporary
  `hearth.secure.migration-backup` are retired.
- **Corrupt primary:** after a clean close, corrupt only a copied
  `hearth.secure` fixture. Verify Hearth recovers from the authenticated rolling
  backup, does not create a replacement key, and does not silently discard the
  known-good records.
- **Missing key:** remove only a copied `hearth.key` fixture while encrypted
  snapshots remain. Verify Hearth fails closed and leaves every snapshot
  unchanged.
- **Wrong Windows account:** attempt the copied fixture from a separate
  disposable Windows account. Verify DPAPI cannot unlock it and Hearth fails
  closed without mutating the fixture.
- **Interrupted erase:** preserve a fixture representing an erase marker with
  remaining encrypted files, then relaunch. Verify startup destroys the old key
  first, finishes remnant cleanup, creates a new empty store, and never restores
  deleted records.

Hash fixtures before and after each failure-path test so “unchanged” is evidence,
not an impression.

## 4. Windows App Certification Kit

Microsoft documents the current WACK workflow at
<https://learn.microsoft.com/windows/uwp/debug-test-perf/windows-app-certification-kit>.
Run it from an active Windows desktop session with the current Windows SDK/WACK
installed. An interactive/admin step may be required by the kit.

From the kit's elevated command prompt, reset stale state and test the exact
candidate:

    appcert.exe reset
    appcert.exe test -appxpackagepath "C:\path\Hearth.appx" -reportoutputpath "C:\path\Hearth-WACK.xml"

Require a passing exit/result and inspect the report rather than relying on
process exit alone. Preserve the unedited XML report beside the matching AppX
and SHA-256 file. If the package changes for any reason, repeat every gate.

## 5. Manual accessibility and presentation

Against the installed candidate, complete the matrix in
`docs/ACCESSIBILITY.md`: keyboard-only use, visible focus, Narrator names and
state, Windows high-contrast themes, 200% text scaling, reduced motion, minimum
window size, light/dark themes, modal focus trapping/restoration, and all five
Store screenshot scenes. Reject clipped content, unreachable controls,
unannounced state, private data, debug UI, or claims not present in the build.

## Release evidence required

- exact AppX filename and SHA-256;
- successful CI run URL and commit SHA;
- Windows version/build and x64 architecture;
- completed fresh-install and lifecycle matrix;
- passing WACK report;
- accepted screenshot manifest and image hashes;
- completed accessibility/presentation checklist; and
- Partner Center submission ID and timestamp after owner review.
