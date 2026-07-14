# Hearth Ethics and Claims Review

_Reviewed against the working tree on 2026-07-14._

## Current posture

Hearth is a personal local-first organizer, not a clinical product. Core
features and the PDF session summary have no in-app paywall or license-key gate.
The previous Stripe test link, arbitrary `PRO-` key acceptance, and unsupported
"clinical-grade" language were removed. No payment is collected in the app.

## Release safeguards now present

- Explicit consent is required before storing wellness-related categories.
- The session summary labels itself a personal reflection aid, not a diagnosis.
- Crisis actions use system `tel:` and `sms:` handlers and remain one click away.
- Medication times are reference data; the UI does not promise reminders.
- Voice dictation was removed so journal text is not handed to a browser speech
  service while the product claims local-only records.
- Smart Decompose replaces the original task and inserts children atomically.
- IPC calls are restricted to Hearth's own top-level renderer.
- Project and runtime dependency licenses ship with packaged builds.

## Unresolved before public binary release

1. The SQLite database is not application-level encrypted despite holding
   potentially sensitive journal, crisis, ERP, and medication-reference text.
2. The two PNG brand assets need a durable rights/provenance record.
3. The advertised support channel must accept new requests.
4. A fresh signed/certified Windows build and the manual paid Store listing do
   not yet exist.

## Commercial boundary

The source is MIT-licensed. The proposed $14.99 Microsoft Store edition would
sell packaging and Store convenience, not exclusive code or clinical outcomes.
No forecast, conversion claim, testimonial, or revenue result may be stated as
observed until it is actually observed.
