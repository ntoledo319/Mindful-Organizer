# Hearth Ethics and Claims Review

_Reviewed against the working tree on 2026-07-14._

## Current posture

Hearth is a personal local-first organizer, not a clinical product. Core
features and the PDF session summary have no in-app paywall or license-key gate.
The previous Stripe test link, arbitrary `PRO-` key acceptance, and unsupported
"clinical-grade" language were removed. No payment is collected in the app.

## Release safeguards now present

- Explicit consent is required before storing wellness-related categories.
- SQLite runs in memory and persists only authenticated AES-256-GCM snapshots;
  the random key is protected by the operating system and missing or unusable
  protected key material fails closed.
- A legacy plaintext database is migrated conservatively, with authenticated
  recovery generations verified before plaintext remnants and the temporary
  migration backup are retired.
- Export and key-first erase controls are available in Settings, with plaintext
  export and forensic-deletion limits disclosed.
- The session summary labels itself a personal reflection aid, not a diagnosis.
- Crisis actions use system `tel:` and `sms:` handlers and remain one click away.
- Medication times are reference data; the UI does not promise reminders.
- Voice dictation was removed so journal text is not handed to a browser speech
  service while the product claims local-only records.
- Smart Decompose replaces the original task and inserts children atomically.
- IPC calls are restricted to Hearth's own top-level renderer.
- Project and runtime dependency licenses ship with packaged builds.
- Shipping brand assets are generated deterministically from repository-owned
  code; provenance is recorded and the earlier undocumented files are vaulted
  outside the package.
- Diary, ERP, and medication-reference capabilities remain preserved and
  renderable but are absent from default navigation pending deliberate opt-in
  and specialist safety review.

## Remaining release gates

1. Exercise fresh install, legacy migration, corrupt-primary recovery, plaintext
   export, and interrupted erase against the exact packaged build in a real
   Windows user session using DPAPI.
2. Pass the Windows App Certification Kit and preserve the report for that same
   package hash.
3. Complete manual keyboard, Narrator, high-contrast, text-scaling, and
   reduced-motion checks against that package.
4. Enable and verify the advertised support channel.
5. Review the IARC/category/market/system-requirement/price fields and legal
   declarations as the signed-in owner, then submit the exact verified package
   through Partner Center.

## Commercial boundary

The source is MIT-licensed. The proposed $14.99 Microsoft Store edition would
sell packaging and Store convenience, not exclusive code or clinical outcomes.
No forecast, conversion claim, testimonial, or revenue result may be stated as
observed until it is actually observed.
