# Hearth 1.0.0 — Submission Day Checklist

*Legal name: **The Hearth Project**. Spoken brand: **Hearth**.*
*Primary domain: `hearthproject.io` (alt: `thehearthproject.io`).*

Everything below is **external action** I could not perform on your behalf —
credit card, identity verification, or physical Windows hardware required.
Items are ordered so each step unblocks the next.

---

## Step 1 — Brand decision: DONE ✅

The product ships as **Hearth**. Legal entity: **The Hearth Project**.
Primary domain: **hearthproject.io** (~$50/yr). Backup: **thehearthproject.io**.

Trademark surface is unique enough to file in USPTO class 9 (software) —
the bare word "Hearth" was blocked by Shogun Enterprises and Hearth
Display, but "The Hearth Project" creates clean registrable surface.

---

## Step 2 — Microsoft Partner Center account (~$19, same day)

1. Go to [partner.microsoft.com/dashboard](https://partner.microsoft.com/dashboard).
2. Sign up as **Individual** ($19 one-time) unless you plan to publish under a company name ($99).
3. Verify identity (email + phone + ID upload). Approval is usually same-day.
4. After approval, you'll get a **publisher identity string** like
   `CN=12345ABC-6789-0DEF-1234-567890ABCDEF`. Copy it.
5. Replace `Publisher="CN=NicholasToledo"` in
   `windows_store/AppxManifest.xml` with that exact string.

## Step 3 — Reserve the app name (5 min, in Partner Center)

1. In Partner Center, **Products → Create new → MSIX or PWA app**.
2. Reserve the name **Hearth** (and/or **The Hearth Project**).
3. Confirm the `Name="TheHearthProject"` value in `AppxManifest.xml`
   matches what Partner Center generated. They must be byte-identical.

## Step 4 — Publish the privacy policy URL (10 min)

1. Push this branch to GitHub.
2. In repo Settings → Pages → Source: `GitHub Actions`.
3. The `.github/workflows/pages.yml` workflow I added will deploy on the
   next push to `main`.
4. After ~1 minute, your privacy policy will be live at:
   `https://ntoledo319.github.io/Mindful-Organizer/privacy.html`
5. Paste that URL into Partner Center → Product → Properties → Privacy
   policy URL.

## Step 5 — Capture real screenshots (30 min, on a Windows machine)

1. Boot a Windows 10/11 machine (or VM).
2. `git clone`, `python -m venv venv`, `pip install -e ".[dev]"`,
   `pip install Pillow`.
3. Run: `python scripts/capture_screenshots.py`.
4. The script will save `screenshot_01..06_*.png` into `windows_store/assets/`
   at 1920×1080.
5. Review for any PII (the script seeds non-PII sample data, but verify).
6. Upload the 6 PNGs in Partner Center → Product → Store listings → Screenshots.

If the script produces empty/broken captures (no display, theme issue),
take them manually with `Win+Shift+S` while running the app.

## Step 6 — Save the license private key to GitHub Secrets (5 min)

The Ed25519 private signing key is currently at
`~/.config/mindful-organizer-keys/private_signing_key.b64`. Copy its
contents and:

1. Copy the contents:
   `cat ~/.config/mindful-organizer-keys/private_signing_key.b64`
2. GitHub repo → Settings → Secrets and variables → Actions → New repository secret.
3. Name: `MINDFUL_LICENSE_PRIVATE_KEY`. Value: paste the base64 string.
4. The `.github/workflows/release.yml` workflow I added will inject this
   into release builds.
5. **Also store the key in your password manager** as a backup. If you
   ever lose it, every license already issued is permanently unverifiable.

## Step 7 — End-to-end Windows build verification (45 min)

On the Windows machine from Step 5:

```bat
build_windows.bat
cd windows_store
.\build_msix.ps1 -Sign -CertPath <your-cert.pfx>
.\build_msix.ps1 -Validate
```

The `-Validate` step runs the Windows App Certification Kit (WACK). Fix
any failures it reports. Common ones:

- Missing visual assets → re-run `scripts/generate_store_assets.py`.
- Unsigned binary → make sure your code-signing cert is loaded.
- Capability mismatch → check `AppxManifest.xml` capability declarations.

## Step 8 — Push the v1.0.0 tag (5 min)

Once all of the above works:

```bash
git add -A
git commit -m "Release: 1.0.0"
git tag v1.0.0
git push && git push --tags
```

The `release.yml` workflow will build MSIX + .app artifacts and create
the GitHub release automatically.

## Step 9 — Submit to Partner Center (15 min)

1. Partner Center → Product → Packages → Upload the signed `.msix` from
   the GitHub release artifacts.
2. Fill out the rest of the Store listing using `windows_store/store_listing.md`.
3. Age rating: complete the IARC questionnaire (12+ per the listing).
4. Categories: Health & Fitness (primary), Productivity (secondary).
5. Pricing: Free (with in-app subscriptions).
6. Markets: Worldwide (or whichever subset you want).
7. **Submit for certification.**

Microsoft review typically takes 24–72 hours. They will email you with
either an approval or a list of certification failures.

---

## Step 10 — When it ships

Optional but valuable:

- Issue a press release / Show HN.
- Email the people you've quoted in `docs/BUSINESS_PLAN.md` first.
- Set up basic monitoring: GitHub Releases download counts, Partner Center
  acquisition reports, GitHub Issues for crash reports.
- Tag a `v1.0.1` milestone in the repo to collect post-launch bug reports.

---

## Hard dependencies summary

| Step | Cost | Time | Blocks |
|---|---|---|---|
| 1. Brand decision | $10–60 (domain) | 30 min | Step 9 |
| 2. Partner Center account | $19 | Same day | Steps 3, 9 |
| 3. Name reservation | Free | 5 min | Step 9 |
| 4. Privacy URL | Free | 10 min | Step 9 |
| 5. Screenshots | Free (need Windows) | 30 min | Step 9 |
| 6. GitHub secret | Free | 5 min | Step 8 |
| 7. Windows build test | Free (need Windows) | 45 min | Steps 8, 9 |
| 8. Tag & push | Free | 5 min | Step 9 |
| 9. Store submission | Free | 15 min + 24–72h review | Launch |

**Critical path total:** ~3 hours of your time + Microsoft's 1–3 day review.

You can ship in a week if you sprint, or coast through it in 2–3 weeks.
