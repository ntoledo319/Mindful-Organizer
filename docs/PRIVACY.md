# Ample Privacy Policy

_Last updated: 2026-07-14_

Ample is a local-first personal organizer. This policy separates information
the app stores on your device from information the developer receives.

## Your consent

On a new profile, Ample asks for express consent before it stores personal
entries. The consent screen describes the categories below, local encrypted
storage, the absence of record upload and telemetry, plaintext exports, and the
in-app erase control. Ample records the time of consent in the encrypted
database. If you do not consent, the app does not store the name, optional
labels, or other personal entries entered during onboarding.

For a legacy profile, Ample first encrypts the records already stored by the
older app as described under **Migration from older Ample versions**. It then
requires express consent before the interface exposes those records or accepts
new personal writes. You can instead use the erase control to destroy them.

You can withdraw consent under **Settings → Privacy and your data → Erase all
Ample data**. Withdrawal deletes all app records and encrypted rollback
snapshots, destroys the key that decrypts them, creates a fresh empty store,
and then returns Ample to onboarding.

## Data you choose to enter

Ample can store:

- a display name and app settings;
- tasks, priorities, dates, categories, and energy estimates;
- mood, energy, anxiety, sleep, journal, practice, and focus records;
- crisis-plan text and contacts;
- ERP-session notes and diary cards, including self-harm or therapy-avoidance
  ratings you choose to record; and
- medication names, doses, frequencies, and usual times used as a reference.

An older Ample profile may also contain optional condition-label metadata.
This release preserves that legacy field for compatibility and export, but does
not ask new users to provide diagnosis or condition labels.

Ample is a personal organization and reflection tool. It is not a medical
device, healthcare service, diagnosis, treatment, or emergency monitor.

## How local records are protected

Ample runs SQLite in memory while the app is open. At rest, it persists only a
versioned, authenticated **AES-256-GCM** encrypted database envelope. Every
successful write uses a new random initialization vector and is written through
an atomic replace operation. A rolling encrypted backup protects against an
interrupted or corrupt write.

The database uses a random 256-bit key. Ample protects that key with Electron's
operating-system credential facility:

- Windows Data Protection API (DPAPI) on Windows;
- Keychain on macOS; and
- Secret Service or KWallet on Linux.

Ample refuses to create or open personal records when secure OS-backed key
storage is unavailable. It also refuses Linux's plaintext fallback. The key is
not embedded in the app, repository, database file, or exports. It is decrypted
only in app memory while Ample is running. Ample best-effort clears its
retained key buffer when the database closes, but language/runtime and
system-managed memory copies may outlive that buffer.

The encrypted files live in Ample's operating-system app-data directory under
`data/`:

- `ample.secure` — current authenticated database snapshot;
- `ample.secure.backup` — previous authenticated snapshot;
- `ample.secure.migration-backup` — temporary original snapshot retained only
  until the migrated primary and rolling backup both authenticate; and
- `ample.key` — the database key encrypted by the operating system.

These protections reduce exposure from copied app-data files. They do not
replace your operating system's account security, screen lock, updates, malware
protection, or full-disk encryption. Someone controlling your signed-in OS
session may be able to use the same OS credential facility as applications in
that session. While Ample is open, decrypted records and the database key exist
in the app process's memory. The operating system may copy process memory into
swap, hibernation, crash, or diagnostic storage; Ample cannot guarantee
forensic erasure of those system-managed copies. Full-disk encryption reduces
that exposure.

## Migration from older Ample versions

Older versions stored `ample.db` and possible SQLite WAL/SHM files without
application-level encryption. On first secure startup, Ample:

1. opens the legacy database read-only and runs SQLite integrity checks;
2. serializes its committed state;
3. writes and authenticates an encrypted migration backup;
4. writes, decrypts, and revalidates the encrypted primary and rolling backup;
   and
5. only then removes the legacy database, WAL, SHM, journal, and temporary
   migration-backup files.

If any verification or write fails, Ample leaves the legacy files in place and
does not silently create an empty replacement. During an unfinished migration,
Ample can recover from the authenticated rolling backup and then the temporary
migration backup. After migration completes, it retires that migration backup;
normal recovery uses the rolling backup. It never replaces an unreadable
database with a new key.

Deleting a legacy file cannot guarantee removal of historical copies held by an
SSD, filesystem snapshot, backup service, or disk image. Device full-disk
encryption and management of your own backups remain important, particularly if
you used a pre-encryption Ample version.

## Exports

Ample exports only after you choose a destination in an operating-system Save
dialog.

- **Export all data** writes a readable JSON copy of records and settings.
- **Session summary** writes a 7, 14, or 30 day PDF of selected trends.

These user-requested JSON and PDF files are **not encrypted by Ample**. Once an
export is saved, its location, backup, protection, deletion, and any sharing are
under your control. Erasing Ample's database does not erase previous exports.

## What the developer receives

The app has no account system, advertising identifiers, analytics, telemetry,
crash reporter, cloud API, or record-sync service. Ample does not transmit the
records above to the developer and does not sell them.

Links such as `tel:988`, `sms:988`, and web links open through your operating
system. Your carrier, browser, and destination service apply their own privacy
policies. Ample does not transmit your database contents when opening a link.

## Access, deletion, and recovery limits

Use **Export all data** to access a portable copy of every record stored by
Ample. Use **Erase all Ample data** to remove all in-app records and
cryptographically withdraw access by deleting the protected key. Deletion is
irreversible unless you separately kept an export or device backup.

The developer cannot view, decrypt, reset, or recover the database. If the OS
credential store or `ample.key` is lost, Ample fails closed rather than
discarding the encrypted database. Export before moving data to another OS
account or device.

## Contact

The public support page is [SUPPORT.md](SUPPORT.md). Reproducible software
reports use privacy-guarded
[GitHub Issue forms](https://github.com/ntoledo319/Mindful-Organizer/issues/new/choose),
which require a free GitHub account and sign-in. Never post private Ample
records, exports, databases, snapshots, keys, or account details there.
