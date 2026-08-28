# Launch destination list (owner-posted only)

Status: **candidate list — nothing posted; every send is a Human Queue action**

Built 2026-07-28 under AGENTS.md §4: an agent-built, TOS-compliant target
list from public data is permitted; autonomous contact with real humans is
forbidden. The owner reviews and posts personally (HQ-05; its 5-minute budget
covers reviewing the drafts and posting to one or two destinations, not all
of them). Reddit blocked direct rule-page fetches during preparation, so
Reddit rule summaries below cite third-party rule checks dated as shown and
are **starting points, not clearances** — re-read each community's current
rules in full immediately before posting (rules change).

Standing rules for every destination:

1. Re-read the destination's current rules in full immediately before
   posting.
2. Disclose the maker relationship in the first line: "I built Paulatim."
3. Post only after the Store page is observed live and purchasable in a
   private browser (HQ-04 step 6); use the destination's campaign ID from
   `store/CAMPAIGNS.md` (`owner-approved-community-<slug>`).
4. Obey the claims blacklist in `store/LAUNCH_KIT.md`: no AI/clinical/
   therapeutic claims, no "best/first/revolutionary/guaranteed", no user
   counts or outcomes, privacy claims only in the exact documented
   protection boundary, no fake engagement, no mass-posting, no cold DMs.
5. One post per destination; do not cross-post identical text (Reddit spam
   detection flags duplicate content across subreddits).

## 1. r/SideProject — Reddit

- URL: <https://www.reddit.com/r/SideProject/>
- Rules: <https://www.reddit.com/r/SideProject/about/rules>
- Self-promotion summary: purpose-built for sharing your own project.
  Third-party rule checks (2026-07) report self-promotion explicitly
  permitted with "share your project, not just a link", no repeated posting
  of the same project, and engagement with commenters expected.
- Required disclosure: "I built Paulatim" in the opening line; never present
  the post as a user review.
- Draft post body:

> **I built Paulatim: energy planning, finally on Windows**
>
> I built Paulatim to bring energy-budget planning to Windows for days when your
> capacity does not match your calendar: give each task an energy cost and
> duration, choose a daily budget from 4 to 24, and Today shows up to three
> open tasks whose recorded cost fits what is left. Check-ins, 7/14/30-day
> trends, and a PDF export you choose to save are all local.
>
> Privacy model: no account, cloud API, advertising, record sync, or app
> telemetry. SQLite runs in memory while it is open; at rest it uses
> authenticated AES-256-GCM snapshots with a random key protected by Windows.
> Exports you request are plaintext. It is personal organization software,
> not medical care.
>
> The source is MIT licensed. The $14.99 Microsoft Store purchase covers the
> maintained packaged app and Store delivery.
> [verified Store link with owner-approved-community-sideproject campaign ID]

## 2. r/indiehackers — Reddit

- URL: <https://www.reddit.com/r/indiehackers/>
- Rules: <https://www.reddit.com/r/indiehackers/about/rules>
- Self-promotion summary: founder-oriented community; third-party rule
  checks (2026-05) report project and launch posts welcome with full founder
  disclosure. Re-verify before posting.
- Required disclosure: "I built Paulatim" in the opening line.
- Draft post body: same facts as destination 1, reframed around the build —
  what was built, the local-encryption design, and the one-time-price
  choice — with one paragraph of genuine build detail before the link. Do
  not reuse destination 1's text verbatim.

## 3. r/productivity — Reddit

- URL: <https://www.reddit.com/r/productivity/>
- Rules: <https://www.reddit.com/r/productivity/about/rules>
- Self-promotion summary: conditional. Third-party rule databases (2026-07)
  classify r/productivity as restricting self-promotion to designated
  threads or formats; a standalone launch post may be removed. Post only
  inside the currently designated self-promotion thread, if one exists, and
  follow its format exactly.
- Required disclosure: "I built Paulatim" plus exact thread-format compliance.
- Draft post body: a two-to-three-sentence version of destination 1 — what
  it does, who it is for, the privacy model in one clause, the disclosure,
  and the campaign link.

## 4. r/spoonies — Reddit (conditional: modmail first)

- URL: <https://www.reddit.com/r/spoonies/>
- Rules: <https://www.reddit.com/r/spoonies/about/rules>
- Self-promotion summary: **unverified.** This is a support community for
  people living with chronic illness — the spoon-theory home niche — not a
  marketing channel. Do not post a project link without prior written
  moderator approval via modmail; accept "no" without argument. If approval
  is granted, follow every condition the moderators set.
- Required disclosure: "I built Paulatim" and, if asked, that the app is a
  paid $14.99 one-time purchase with MIT-licensed source.
- Draft modmail (not a post):

> Hello moderators — I built Paulatim, a Windows energy planner based on a
> user-chosen 4–24 daily budget with spoon-style task costs. It is local and
> encrypted at rest, with no account or cloud API. May I share it once with the
> community under your rules? I will follow any format or disclosure you
> require, and I will not post without your approval.

## 5. AlternativeTo — software directory

- URL: <https://alternativeto.net/>
- Self-promotion summary: a public software directory of the AlternativeTo
  class; listing or suggesting your own software through a normal account is
  the site's core mechanic. Strictly no fake reviews, no multiple accounts,
  no vote manipulation. Verify current listing terms before submitting.
- Required disclosure: list under the owner's real account; describe the app
  factually; never solicit or fabricate reviews.
- Draft listing summary (short, factual):

> Paulatim brings energy-budget planning to Windows for ADHD and other
> variable-capacity days. Tasks get an energy cost; you choose a 4–24 daily
> budget and see what fits. Supporting proof: local, encrypted-at-rest storage
> with no account, cloud API, ads, record sync, or app telemetry. One-time
> purchase; MIT-licensed source.

## 6. Product Hunt — launch platform

- URL: <https://www.producthunt.com/>
- Self-promotion summary: launching your own product is the platform's core
  mechanic; the maker posts under their real identity with the built-in
  Maker badge, which satisfies disclosure by design. Expect to answer
  comments on launch day — schedule it only when the owner can respond.
- Required disclosure: automatic via the Maker badge; still say "I built
  Paulatim" in the first comment.
- Draft first comment: the destination-1 facts minus the Reddit framing,
  plus one sentence on why local-first (records stay on the user's machine;
  requested exports are plaintext). Include the Store campaign link with
  `owner-approved-community-producthunt`.

## Checked and excluded

- **r/ADHD** (<https://www.reddit.com/r/ADHD/about/rules>): the public rules
  prohibit self-promotion (third-party rule check, 2026-06-14). Do not post
  and do not modmail a workaround. Recorded here so no owner minutes are
  spent on it.
- **GitHub Pages for the landing page**: excluded for commercial hosting by
  D007; reconsider only after a current-terms re-check recorded in
  `revenue/DECISIONS.md`.

## After posting

Record each post URL and timestamp in `revenue/METRICS.md`, then watch the
campaign-ID rows in Partner Center's acquisitions report. One reposition at
the five-day gate per the menu in `revenue/PLAN.md` (artifacts in
`store/REPOSITION_KIT.md`); no second post wave without a new owner
decision.
