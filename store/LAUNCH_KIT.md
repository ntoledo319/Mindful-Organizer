# Ample launch kit

Status: **drafts only — not authorized for posting or sending**

## Positioning canon

**Audience:** Windows users with ADHD or other variable-capacity days who want a
private, calmer way to decide what realistically fits today.

**Primary job:** let the user choose a 4–24 daily energy budget and turn it into
a smaller, finishable task plan. Ample never infers or changes that budget from
a diagnosis or check-in.

**One sentence:** Ample is a privacy-first Windows energy planner that helps you
plan around the capacity you have, with no account, cloud, ads, or record sync.

**Proof available in the product:** task energy and duration inputs, estimated
spoon costs, a user-controlled remaining daily budget, up to three fitting open
tasks on Today, local check-ins, local trends, and user-requested PDF export.

**Secondary tools:** guided practices, focus hold, and a user-written crisis
plan. ERP-note, diary-card, and medication-reference modules remain preserved
outside the default navigation pending dedicated opt-in and safety review; do
not present them as part of the launch workflow.

## Claims boundary

Use:

- local-first or privacy-first, immediately paired with the exact storage
  disclosure;
- no account, cloud API, advertising, record sync, or app telemetry;
- SQLite in memory while open; versioned, authenticated AES-256-GCM snapshots at
  rest; and a random 256-bit key protected by Windows DPAPI through Electron
  `safeStorage`;
- temporary legacy-migration backup retired after two verified encrypted
  generations;
- the matching limits: decrypted records and key in process memory while open,
  possible OS swap/hibernation/crash/diagnostic copies, signed-in-session access
  risk, plaintext user-requested exports, and no guarantee that file deletion
  removes SSD/snapshot/backup copies;
- conservative local rules;
- personal organization and reflection;
- a user-controlled plaintext PDF summary.

Do not use:

- AI-powered, intelligent diagnosis, clinical-grade, therapeutic, treatment, or
  medical-device language;
- detects a crisis, prevents self-harm, protects a user, rewires the brain, or
  improves a condition;
- generic “secure,” “anonymous,” “zero data collection,” or “private by
  guarantee” language; encryption claims must use the exact protection boundary
  above and link to the privacy policy;
- best, first, revolutionary, guaranteed, effortless, or productivity claims
  without observed comparative evidence;
- user counts, outcomes, testimonials, ratings, or revenue not present in the
  evidence ledger.

## Owner-controlled launch note

Draft only:

> Ample is now available for Windows through the Microsoft Store. It is an
> energy planner for ADHD and other variable-capacity days: give work an energy
> cost, choose a daily budget from 4 to 24, and see what fits the day you have.
> Records are encrypted at rest with authenticated AES-256-GCM snapshots and a
> key protected by Windows; exports you request are plaintext. There is no
> account, cloud, advertising, or record sync. Ample is personal organization
> software, not medical care. [verified campaign link]

Before approval, replace “now available” only after the product page is visibly
purchasable and replace the bracketed text with the source-specific link from
store/CAMPAIGNS.md.

## GitHub release note

Draft only:

### Ample for Windows

This release prepares the official x64 Microsoft Store package for Ample, a
local-first energy planner for variable-capacity days.

Core loop:

- estimate a spoon cost from a task's energy demand and duration;
- choose a 4–24 daily energy budget and see what remains;
- surface open tasks whose recorded cost fits;
- review local mood, energy, and sleep trends;
- export a personal PDF summary only when requested.

While open, Ample runs SQLite in memory. At rest it uses authenticated
AES-256-GCM snapshots and a random key protected by the operating system. The
privacy policy documents memory, OS-session, export, deletion, and recovery
limits; requested JSON and PDF exports are plaintext.

The source remains MIT licensed. The Store purchase covers official packaging
and Store delivery. Ample is not a medical device or emergency service.

Do not publish this note until the package hash, public Store URL, certification,
support, privacy, price, and release date are all observed.

## Community note

Do not mass-post the launch note. For any community:

1. Read its current rules in full.
2. Confirm that developer promotion is allowed.
3. Rewrite the opening around a real discussion the community permits; do not
   impersonate a customer or conceal the maker relationship.
4. Disclose: “I built Ample.”
5. Use a unique owner-approved-community campaign ID.
6. Have the owner review and submit it.

No list of communities is included because eligibility and promotion rules must
be verified immediately before any post.

## Support response skeleton

Use only as a human-reviewed response:

> Thanks for reporting this. I have not reproduced or confirmed the cause yet.
> Please share the Ample version, Windows version, the steps immediately before
> the problem, and whether it repeats after a normal restart. Do not attach your
> Ample encrypted snapshots or key, plaintext JSON or PDF exports, journal
> text, crisis-plan text, medication information, or screenshots containing
> private records.

Never request the local database through a public issue.

## Launch-day truth check

- [ ] Public page loads in a private browser.
- [ ] Price and one-time purchase model match the approved submission.
- [ ] Package, publisher, x64 requirement, and minimum Windows version match.
- [ ] Privacy, terms, refund, and the support landing page work without sign-in;
      the support page clearly discloses that filing an issue requires GitHub
      sign-in.
- [ ] Screenshots and feature bullets match the live package.
- [ ] Campaign links land on the correct product.
- [ ] Partner Center acquisition, usage, health, reviews, and payout reports are
      available to the owner.
- [ ] Every owner-controlled post is separately approved.
