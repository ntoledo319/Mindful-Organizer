# Ample capability vault

_Last updated: 2026-07-14_

The launch experience is intentionally narrower than the source tree. A
capability marked **vaulted** is preserved, not deleted: its types, storage,
main-process methods, preload contract, renderer, and export path remain in the
repository so it can be reviewed or restored without reconstructing lost work.
It is absent from default navigation or collection because its current safety,
clarity, or product value does not meet the launch bar.

## Preserved capabilities

| Capability | Preserved implementation | Why it is not in the launch flow | Restoration gate |
|---|---|---|---|
| Diary cards | `diary_cards` table, typed IPC/repository methods, `Diary.tsx`, JSON export | Includes a self-harm urge field and DBT-style terminology | Deliberate opt-in, specialist safety review, contextual support copy, accessibility and Windows tests |
| ERP notes | `erp_sessions` table, typed IPC/repository methods, `Erp.tsx`, JSON export | Exposure work should not be presented as a generic self-guided default | Deliberate opt-in, specialist review, non-treatment positioning, accessibility and Windows tests |
| Medication reference | medication tables, typed IPC/repository methods, `Meds.tsx`, JSON export | A static reference can be mistaken for reminders or adherence monitoring | Deliberate opt-in, unmistakable reference-only boundary, accessibility and Windows tests |
| Legacy condition labels | `Settings.conditions`, condition types, encrypted settings storage, JSON export | The labels did not change behavior, so collecting diagnosis metadata added sensitivity without user value | Restore only with a specific user-controlled function, privacy review, and proof that it never infers capacity or treatment |

`src/renderer/capabilities.ts` is the executable route registry. Its tests ensure
the five core routes stay visible and the three specialist screens remain
vaulted and renderable. Legacy condition-label compatibility is intentionally
kept outside that route registry because it is stored metadata, not a screen.

## Asset vault

Earlier PNG artwork with incomplete provenance is preserved byte-for-byte under
`resources/vault/unverified-2026-07-14/` and excluded from packaging. Shipping
art is generated deterministically by `scripts/generate-brand-assets.mjs`; see
`resources/BRAND_PROVENANCE.md`.

## Preservation evidence

Release candidate 8172603b62c2457696608c145511bd3fe92429d4 retains the vaulted
schema, contracts, renderers, exports, and archived artwork while omitting the
specialist routes from default navigation. The capability-registry tests in the
green Quality run verify both sides of that boundary:
<https://github.com/ntoledo319/Mindful-Organizer/actions/runs/29322423682>.

This vault is deliberately source-level safe keeping, not a promise that the
features are appropriate to re-enable. Restoration means satisfying the gate in
the table, adding the route back explicitly, rerunning privacy/security and
accessibility review, and generating a new release candidate.

## Non-destructive rule

Do not delete a vaulted schema table, type, renderer, or archived asset in a
cleanup pass. Any permanent removal requires a separately reviewed migration,
export compatibility decision, and an update to this document. Vaulted records
remain covered by consent, encryption, export, and erase behavior.
