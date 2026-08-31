# Paulatim Terms

_Last updated: 2026-08-31_

_Visible-name correction — 2026-08-28: the intended Store terms are
substantively unchanged; only the visible product name is now Paulatim. No live
offer or publication is implied._

_Publication correction — 2026-08-31: Paulatim 1.1.1 is now available through
the Microsoft Store for $14.99 USD. The substantive product, privacy, warranty,
and support boundaries below are unchanged._

## Current status

Paulatim is available on the Microsoft Store for $14.99 USD at
<https://apps.microsoft.com/detail/9PLRSZZMFPJH>. These terms govern the
official Microsoft Store package.

## Product scope

Paulatim is personal organization and wellness software. Its primary function is
to help a user estimate task energy costs and plan against a daily energy budget
the user chooses from 4 to 24. Paulatim does not infer or change that capacity
from a diagnosis or check-in. Check-ins, trends, practices, and crisis-plan text
remain under the user's control. ERP, diary-card, medication-reference, and
legacy condition-label capabilities remain preserved but outside the default
experience pending a dedicated opt-in and safety review.

Paulatim is not a medical device, healthcare provider, emergency service,
diagnosis, treatment, or substitute for professional care. Do not rely on it to
detect, monitor, prevent, or respond to an emergency. In a US crisis, call or
text 988; in immediate danger, call the local emergency number.

## Local records

The user chooses what to enter and is responsible for access to the Windows
account, device, local backups, and exported files. SQLite runs in memory while
Paulatim is open. At rest, Paulatim uses authenticated AES-256-GCM snapshots and a
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
[privacy policy](PRIVACY.md). Do not use Paulatim for information you are not
comfortable storing under that policy.

## Source and official package

The source code is available under the repository's MIT license. The official
Microsoft Store package's one-time listed price pays for that packaged binary
and Store delivery. A purchase does not remove the source license, transfer
intellectual-property rights, create a healthcare relationship, or promise a
particular future feature or update.

Store billing, delivery, eligible refunds, and applicable consumer protections
remain governed by Microsoft and local law.

## Warranty

The software is provided as described in the MIT license, without warranty.
Nothing in these terms limits a right that cannot legally be limited.

## Support

The public support path is documented in [SUPPORT.md](SUPPORT.md). GitHub sign-in
is required to create an issue. It is not a private, clinical, crisis, or
emergency channel. Never post a Paulatim database, encrypted snapshot, key,
plaintext export, account detail, or private wellness record in a public support
request.
