# Hearth Privacy Policy

_Last updated: 2026-07-14_

Hearth is a local-first personal organizer. This policy separates what the app
stores on your device from what the developer receives.

## Data you enter

Hearth can store your display name, settings, tasks, mood/energy/anxiety and
sleep check-ins, journal entries, practice and focus records, crisis-plan text,
ERP session notes, diary cards, and medication-reference entries. Onboarding
asks for explicit consent before these categories are stored.

## Where it is stored

Records are stored in SQLite in Hearth's operating-system app-data directory.
Because SQLite uses write-ahead logging, the database can consist of
`hearth.db`, `hearth.db-wal`, and `hearth.db-shm` while the app is running.
These files are not protected by application-level encryption. Anyone with
access to your operating-system account or storage may be able to read them.
Use your device's account security and full-disk encryption, and do not enter
information you are not comfortable storing locally.

Hearth does not provide cloud backup or sync. Your normal device backup system
may copy the files according to that system's settings.

## Session-summary exports

When you request a 7, 14, or 30 day session summary, Hearth shows a system Save
dialog and writes a PDF only to the location you select. The PDF is a personal
reflection aid, not a clinical record or diagnosis. Hearth does not upload it.
After export, the destination and any sharing are under your control.

## What the developer receives

The app has no account system, advertising identifiers, analytics, telemetry,
crash reporter, cloud API, or record-sync service. Hearth does not transmit the
records listed above to the developer or sell them. Links such as `tel:988`,
`sms:988`, and web links open through your operating system; your carrier,
browser, and destination service apply their own policies.

## Deleting or moving data

Quit Hearth completely before copying or deleting its database files so pending
WAL data is closed safely. To erase local Hearth records, remove Hearth's app-data
folder using your operating system's application-data controls. Delete exported
PDFs separately from wherever you saved them. There is no developer-held remote
copy to delete.

## Scope

Hearth is a personal wellness and organization tool, not a medical device,
healthcare provider, diagnosis, or substitute for professional or emergency
care. If you are in crisis in the United States, call or text 988; elsewhere,
use your local emergency number.

## Contact

The intended support channel is the repository's
[GitHub Issues](https://github.com/ntoledo319/Mindful-Organizer/issues). Issue
creation is not yet enabled, so this channel is a release blocker rather than a
currently available contact method.
