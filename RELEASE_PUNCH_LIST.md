# Hearth 1.0.0 — Release Punch List

**Status:** Code-complete. 674 / 674 fast tests pass. Lint clean on all
changed files. Every blocker that can be fixed in-repo has been fixed in
the `1.0.0` work. What remains is external — money, paperwork, or
hardware-bound — and is captured below.

---

## ✅ Resolved in code (this release)

| Blocker | Resolution |
|---|---|
| Hardcoded HMAC license secret (anyone could forge keys) | Replaced with Ed25519; private key held by issuer. See `scripts/issue_license.py`. |
| Encryption key on disk next to ciphertext | Moved to OS keyring via `keyring` lib; legacy file auto-migrated. |
| No log rotation | `RotatingFileHandler`, 5 MB × 5 files. |
| Legacy JSON tasks orphaned from SQLite | First-launch migration auto-runs once. |
| Windows Store assets folder empty | 66 PNG variants + multi-resolution ICO generated. |
| AppxManifest placeholder PhoneProductId GUID | Replaced with a real UUID. |
| Version drift (1.1.0 vs 1.0.0 vs 1.0.0.0) | All pinned to 1.0.0. |
| `Development Status :: 4 - Beta` classifier | Bumped to `5 - Production/Stable`. |

---

## ❌ Still required before public Store submission

### 1. Code-signing certificate — **HARD BLOCKER**

The Microsoft Store will not accept an MSIX signed by `CN=NicholasToledo`
(the current dev identity). Options:

| Option | Cost | Time to acquire |
|---|---|---|
| **Microsoft Partner Center "Standard" account** | $19 one-time (individual) / $99 (company) | Same day approval typical |
| **Sectigo / DigiCert EV code-signing cert** | $250–$450/year | 1–5 business days |

Then update `windows_store/AppxManifest.xml` line `Publisher="CN=..."` to
match the Partner Center publisher identity exactly. Mismatch → submission
rejected.

### 2. Trademark search & filing — **RECOMMENDED BEFORE LAUNCH MARKETING**

"Mindful Organizer" and the brand name "Adaptive" (referenced in business
plan) are both common-word combinations. Before spending on launch
marketing:

- USPTO TESS search for both names in Class 9 (software) and Class 44
  (mental health services).
- File USPTO Form TEAS Plus ($250 per class) if available.

### 3. Domain registration

The business plan assumes `adaptive.app` exists. Either:
- Register `adaptive.app` ($14/yr on Namecheap, ~$2k+ on aftermarket).
- Or use the unambiguous `mindfulorganizer.com` / `.app` (cheaper).

### 4. Privacy-policy URL hosting

`windows_store/privacy_policy.html` exists but needs a live URL — the
Store listing requires a public link. Cheapest path: GitHub Pages on
the repo (free) or Cloudflare Pages (free).

### 5. Real screenshots

`store_listing.md` describes 6 screenshots but `windows_store/assets/`
contains zero `screenshot_*.png`. Required: 6 PNGs at 1920×1080 captured
on Windows 10/11 with realistic non-PII sample data.

### 6. Microsoft Partner Center reservations

- Reserve app name "Hearth" (legal: "The Hearth Project") in Partner Center.
- Update `windows_store/AppxManifest.xml` `Name="MindfulOrganizer"` to
  match the reserved name exactly.
- Complete age rating questionnaire (IARC).
- Set pricing & markets.

### 7. End-to-end Windows build verification

`build_windows.bat` and `windows_store/build_msix.ps1` have not been
executed on a clean Windows machine. Before submission:

1. Boot a clean Windows 10 22H2 or Windows 11 VM.
2. Install Python 3.11+, run `build_windows.bat`.
3. Confirm `.msix` produced.
4. Run Windows App Certification Kit (`MakeAppx.exe` + `signtool.exe`).
5. Sideload-test on a second machine.

### 8. Real signing-key handling at build time

The Ed25519 private signing key is currently saved to
`~/.config/mindful-organizer-keys/private_signing_key.b64` on this
developer machine (mode 0600, **not** in the repo). For production:

- Copy that file to a password manager.
- Inject as `MINDFUL_LICENSE_PRIVATE_KEY` environment variable in the
  GitHub Actions release workflow secrets.
- Never echo or commit it.

The public key in `src/core/subscription_manager.py:_PUBLIC_KEY_B64` is
the verification half — safe to ship.

---

## 🟡 Nice-to-have (not blockers)

| Item | Effort | Value |
|---|---|---|
| GUI test coverage (pytest-qt) | 3–5 days | High — currently 0% on widgets |
| Crash reporting (Sentry, free tier) | 1 day | Medium — store listing implies it exists |
| macOS PlatformBackend testing on real hardware | 1 day | Medium — automation only stub-tested |
| Windows PlatformBackend implementation (PowerShell/WMI) | 3–5 days | High for Win release of automation |
| Remove `voice_journal.py` (honest stub, but invites confusion) | 1 hour | Low |
| Tighten `Topic ::` PyPI classifiers in pyproject (current value isn't a real classifier) | 5 min | Trivial |

---

## Test & lint state at the time of this release

```
pytest -m "not gui and not slow"   →  674 passed, 29 skipped
ruff check (modified files)         →  All checks passed
mypy                                 →  Pre-existing GUI errors only (unchanged)
```

The 29 skips are PyQt6 GUI tests excluded from CI by design.

---

## TL;DR

You are about **3–10 business days of non-coding work** away from a Store
submission. The code is shippable. What you need: a publisher account
($19), a code-signing cert (or just the Store cert via Partner Center),
six real screenshots, a public URL for the privacy policy, and a clean
Windows machine to run the build once end-to-end.

Everything else is optional polish.
