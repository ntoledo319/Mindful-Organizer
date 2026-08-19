# Ample Terms

_Last updated: 2026-07-14_

## Current status

Ample is not currently listed as purchasable. These terms describe the intended
official Microsoft Store package and do not represent that a price, package, or
listing is live.

## Product scope

Ample is personal organization and wellness software. Its primary function is
to help a user estimate task energy costs and plan against a daily energy budget
the user chooses from 4 to 24. Ample does not infer or change that capacity
from a diagnosis or check-in. Check-ins, trends, practices, and crisis-plan text
remain under the user's control. ERP, diary-card, medication-reference, and
legacy condition-label capabilities remain preserved but outside the default
experience pending a dedicated opt-in and safety review.

Ample is not a medical device, healthcare provider, emergency service,
diagnosis, treatment, or substitute for professional care. Do not rely on it to
detect, monitor, prevent, or respond to an emergency. In a US crisis, call or
text 988; in immediate danger, call the local emergency number.

## Local records

The user chooses what to enter and is responsible for access to the Windows
account, device, local backups, and exported files. SQLite runs in memory while
Ample is open. At rest, Ample uses authenticated AES-256-GCM snapshots and a
random 256-bit key protected through the operating system's credential facility
(DPAPI on Windows). During a legacy migration, the original plaintext files are
removed only after encrypted copies verify; the encrypted migration backup is
temporary and is retired after two verified encrypted generations.

This does not make local storage an absolute security guarantee. Decrypted data
and the key exist in RAM while the app is open; the operating system may copy
memory into swap, hibernation, crash, or diagnostic storage; and a person who
controls the signed-in OS session may be able to use the same credential
facility. User-requested JSON and PDF exports are plaintext. File deletion
cannot guarantee removal from SSD recovery, snapshots, or backups. The exact
storage, migration, deletion, and transmission behavior is described in the
[privacy policy](PRIVACY.md). Do not use Ample for information you are not
comfortable storing under that policy.

## Source and official package

The source code is available under the repository's MIT license. If an official
Microsoft Store package becomes available, its one-time listed price pays for
that packaged binary and Store delivery. A purchase does not remove the source
license, transfer intellectual-property rights, create a healthcare
relationship, or promise a particular future feature or update.

Store billing, delivery, eligible refunds, and applicable consumer protections
remain governed by Microsoft and local law.

## Warranty

The software is provided as described in the MIT license, without warranty.
Nothing in these terms limits a right that cannot legally be limited.

## Support

The public support path is documented in [SUPPORT.md](SUPPORT.md). GitHub sign-in
is required to create an issue. It is not a private, clinical, crisis, or
emergency channel. Never post a Ample database, encrypted snapshot, key,
plaintext export, account detail, or private wellness record in a public support
request.
