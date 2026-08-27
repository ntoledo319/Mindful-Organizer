# Get Ample listed — owner runbook (2026-08-07)

> **Correction — 2026-08-25:** with owner authorization, the agent reobserved
> existing product `9PLRSZZMFPJH`. Product identity reports
> `ToledoTechnologies.Hearth`; Manage app names reports only `Hearth` as
> currently in use. No name was reserved or changed. The package-identity gate
> is therefore resolved with the existing product's observed identity, while
> reserving the Ample display name remains an owner-only pre-submission action.
> Step 0's older assumption that adding the display name would assign a new
> Ample-shaped package identity is retained below as historical guidance, not
> current package-build instruction.

> **Correction — 2026-08-19:** this runbook and the Ample identity reset landed
> on 2026-08-19; the heading retained the 2026-08-07 research date. The opening
> claim below that all agent work was done is also superseded: rename-gate,
> screenshot-harness, license-notice, listing-copy, and state-reconciliation
> fixes are prepared locally but remain uncommitted until the observed Partner
> Center identity is supplied. No Ample AppX exists yet.

Everything the agent can do is done. This is the remaining path, in order, with
the reason each step blocks the next. Nothing here can be done by an agent:
every item is a legal attestation, a financial credential, a commercial
commitment, or a Partner Center action tied to your identity.

**Total clicking time: roughly 50–60 minutes.** Wall-clock is longer and mostly
outside your control — see "What actually sets the date" at the bottom.

> **Time correction — 2026-08-26:** the preceding estimate omitted the
> separate five-minute Ample reservation and the renamed listing/package/
> screenshot work. Using this runbook's ten-minute IARC estimate plus the
> grounded 13-minute prepared listing and 15-minute non-duplicative HQ-03 pass,
> the full remaining queue is approximately 79 minutes with HQ-07's full screen
> or 70 minutes with its one-minute informed-risk path. See
> `revenue/HUMAN_QUEUE.md` and D047 for the sole conditional batching path that
> stays at the 60-minute full-run ceiling. This is not a recommendation to waive
> screening.

---

## Step 0 — Reserve the name "Ample" (5 min) — BLOCKS EVERYTHING

> **Execution correction — 2026-08-25:** this heading and the build-blocking
> explanation below record the superseded assumption. The Ample display-name
> reservation does **not** block AMPLE-001 build or CI: use the observed
> existing-product identity `ToledoTechnologies.Hearth`. Reservation remains an
> owner-only gate before submission and must never trigger another guessed
> package-identity rewrite.

Partner Center → your product → **Product identity** / **Manage app names**.

Reserve **Ample**. Then read the **Package/Identity/Name** value Partner Center
assigns and paste it into `store/identity.json` → `identityName`, and set
`identityVerified` to `true`.

**Why this blocks the build, not just the listing:** Partner Center assigns the
package identity from the reservation — it is not author-chosen. The rename
sweep wrote `ToledoTechnologies.Ample` as a placeholder because that is the
pattern, not because anyone observed it. If the built AppX identity does not
match the reservation exactly, submission is rejected. **No submittable package
can be produced until you paste the real value.**

Also decide here whether Ample is a *new* product or an added name on
`9PLRSZZMFPJH`. If Partner Center forces a new product reservation, the existing
Submission 1 (pricing, copy, categories, certification notes) does not carry
over and has to be re-entered. Ask support in the same session as Step 1 if it
is not obvious.

## Step 1 — Payout and tax (10 min, then up to 48h latency) — START TODAY

Partner Center → **Account settings → Payout and tax**.

Complete the payout account and tax profile. **Start this first regardless of
where you are in the rest of the list** — it has the longest and least
predictable latency.

**Known problem:** the "Payout and tax" section has previously been *absent*
from Account settings, which usually means the developer-profile role is wrong.
If it is still missing, open a Partner Center support ticket immediately. That
is a multi-day path, and it is the single most likely thing to push the launch
date. Do not discover this on Sunday.

## Step 2 — IARC age rating (10 min)

Partner Center → submission → **Age ratings** → complete the IARC
questionnaire.

Answer honestly about the mood, energy, and crisis-plan content. Saving requires
attesting you are of majority age in your jurisdiction — a legal declaration in
your name, which is why no agent can do it.

## Step 3 — Trademark check on "Ample" (1 min)

> **Screening correction — 2026-08-26:** do not rely on the older
> "food brands, not software" sentence below. A read-only public sweep surfaced
> [Amplenote](https://www.amplenote.com/), an adjacent productivity product
> covering tasks, goals, mood, and planning. The available agent interface did
> not yield an authoritative live-status USPTO clearance or a reliable
> Microsoft Store result. The current state is **follow-up-needed**: the owner
> must run the official searches and make the legal-risk decision. No name was
> reserved or changed during this screen.

<https://tmsearch.uspto.gov/> — search **Ample** in classes 009 and 042.

The known collisions are food brands (Ample Foods, Ample Hills Creamery), not
software. This is screening confirmation, not clearance. While you are there,
also look up serial **97524800** (HEARTH DISPLAY) — it is the reason for the
rename and the record status has never been observed directly.

Microsoft's policy: a rights holder can report an infringement, and after
publication the app is removed from the Store until every instance of the name
is changed in the app, its content, and the listing, and it is submitted for
certification again.

## Step 4 — Candidate build (agent, ~16 min, unattended)

> **Candidate outcome — 2026-08-25:** AMPLE-001 is complete. Exact source
> `3b8d225` passed Quality run 32844120492 and Windows run 32844120483. The only
> current AppX is SHA-256 `7d6ca584…61866b`, staged with artifact 9561704379's
> screenshots at `tmp/AMPLE-001-3b8d225/`. This supersedes both same-day build
> instructions below; do not upload anything until the owner completes Step 0
> and the remaining submission gates.

> **Execution correction — 2026-08-25:** Step 0 no longer gates this build.
> The exact existing-product identity is recorded and the full local gate is
> green; AMPLE-001 proceeds with the canonical push and exact-SHA CI. Step 0
> still must be completed by the owner before submission.

Once Step 0 lands, tell the agent. It will commit the verified identity, fire
the Windows Store MSIX workflow, download the artifact, recompute the AppX
SHA-256, record it in `store/WINDOWS-VALIDATION.md`, and stage the package plus
screenshots for you.

CAND-002 (`a5d2cf36…b18f`) is now **historical** — the rename changed the AppX
manifest. Do not upload it. There are six non-candidate MSIX artifacts in CI
history; the register is in `store/WINDOWS-VALIDATION.md`.

## Step 5 — Upload package and finalize the listing (15 min)

> **Time correction — 2026-08-26:** the heading is the historical estimate.
> Because the exact AppX, full hash, five ordered screenshots/captions, copy,
> features, keywords, price, categories, URLs, notes, and release hold are all
> prepared, budget **13 active owner minutes** as allocated in HQ-04. Passive
> transfer and Microsoft validation wait are excluded; stop on any mismatch.

Upload the new AppX. Confirm the hash matches what the agent recorded.

Refresh the listing copy and keywords — see
`store/DISCOVERY-REVIEW-2026-08-07.md`. Lead with the platform, not privacy:
**nobody else ships energy-budgeted planning on Windows.** Every competitor
(Spoons, SpoonieDay, SpoonDo, Visible, Tiimo) is Apple-only. Privacy is now
table stakes in this niche — use it as proof, not as the pitch, and note that
SpoonieDay collects usage data and diagnostics while your source is MIT-licensed
and auditable.

Also reconsider the **Health + fitness** secondary category. It puts you beside
apps you compete poorly against and may invite closer content review of a
product that repeatedly disclaims being a medical device.

## Step 6 — Submit (2 min) + certification (days, not yours to control)

Submit. Microsoft certification takes days. Nothing you do changes that.

## Step 7 — After certification

- Install the Store-signed build and run the accessibility pass
  (`docs/ACCESSIBILITY.md`). This needs an x64 Windows machine — confirm you
  have one before you get here.
- Deploy the landing page (`landing/`) only once the listing is genuinely live
  and purchasable.
- Run `store/POST_PUBLICATION_DOC_SWEEP.md`.

---

## What actually sets the date

Not the 50 minutes of clicking. These three:

1. **Payout role resolution** — unknown, possibly a multi-day support ticket
2. **Microsoft certification** — days
3. **First payment** — the Store pays monthly against a $50 threshold, so August
   sales pay around mid-September regardless of when you list

Day 28 is 2026-08-10. **$4,000 collected by then is not reachable** and has not
been since before this session. Carrying it as a live gap manufactures urgency
that `AGENTS.md` §2 forbids — see PROP-007. The honest replacement target is a
live purchasable listing plus a first real demand signal.
