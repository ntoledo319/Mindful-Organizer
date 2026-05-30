# Security Review

**Purpose:** Audit of authentication, encryption, secrets handling, and risk areas.  
**Intended audience:** Security reviewers, auditors, buyers.  
**Confidence:** Confirmed from source code. Inferred concerns are labeled.  
**Source references:** `src/security/content_management.py`, `src/core/subscription_manager.py`, `src/core/database.py`, `src/main.py`  
**Last updated:** 2026-05-02

## Executive Summary

Hearth is a **single-user offline desktop app**. The security model assumes the attacker has access to the user's OS account. Defenses are focused on **opportunistic protection** (passcode-protected folders, local encryption) rather than **high-assurance security**.

**Confirmed risk:** The encryption key for secure folders is stored alongside the encrypted data. A compromised user account yields both key and ciphertext.

## Authentication

- **No application-level authentication.** The app boots directly to the main window.
- **Content-level authentication:** `ContentManager.verify_access(folder_id, passcode)` uses scrypt to hash passcodes. This is a single-factor local passcode, not multi-factor despite the `SecurityLevel.MAXIMUM` label.

## Sessions

- **No sessions.** The app is a single-process desktop application. There is no session token, cookie, or timeout.

## Secrets Handling

| Secret | Location | Risk |
|--------|----------|------|
| License public key | Embedded in `src/core/subscription_manager.py` | **Low** — public verification key by design; private signing key must remain out of repo |
| Fernet key for secure folders | OS keyring, with `~/.mindful_organizer/.content_config/key.bin` fallback | **Medium** — fallback stores key near ciphertext when keyring is unavailable |
| Folder passcode hashes | `~/.mindful_organizer/.content_config/*_meta` (encrypted with Fernet) | **Medium** — protected by Fernet, but local key fallback is possible |
| User's SQLite DB | `~/.mindful_organizer/mindful_organizer.db` | **Low** — unencrypted; assumes OS account security |

## Access Control

- **No RBAC or ACLs.** All features are available to the single user, gated only by subscription tier.
- **Subscription gating** is enforced locally via `SubscriptionManager.has_feature()`. This is bypassable by modifying local source/runtime state, which is accepted for an offline desktop app.

## Input Validation

| Surface | Validation | Risk |
|---------|-----------|------|
| Task title/notes | No length limits or sanitization | Low — local only, no XSS vector |
| Folder name in `ContentManager` | Path traversal rejected (`len(Path(name).parts) != 1`) | **Medium fixed** — previously allowed traversal |
| Database `where` clauses | Parameterized SQL required by convention | **Medium** — no runtime guard against interpolation |
| License key | Ed25519 signature validated | Low — invalid keys rejected |

## Data Exposure Risk

- **Local data is unencrypted by default** (except secure folders).
- **Shareable reports** are self-contained HTML files. They contain all exported data in plaintext. If shared via email/cloud, the data leaves the device unencrypted.
- **No cloud sync** means no third-party data exposure, but also no backup unless user manually copies files.

## Insecure Defaults

| Default | Issue | Recommended Fix |
|---------|-------|-----------------|
| Private license key ops | Issuance controls are not documented | Store private key only in release secrets and document rotation |
| Fernet key fallback file | Encryption provides limited value without keyring | Make fallback opt-in and warn in app |
| No passcode on app launch | Anyone with OS access can open the app | Document as accepted risk for single-user desktop software |

## Dependency Risk Points

| Package | Risk | Mitigation |
|---------|------|------------|
| PyQt6 | Large C++ surface, potential memory safety issues | Keep updated, no custom C++ extensions |
| cryptography | Security-critical; must stay current | Pin to `>=38.0.0`, monitor CVEs |
| numpy | C extensions, potential memory issues | Standard package, well-maintained |
| scikit-learn | Optional; same risks as numpy | Graceful degradation if absent |

## Client/Server Trust Boundaries

- **No server.** The app is entirely client-side.
- **Optional network calls:**
  - GitHub API for update checking (read-only, no auth)
  - Chart.js CDN loaded in HTML reports (read-only, no user data sent)
  - Meditation MP3 downloads via `fetch_meditations.py` (optional script, not runtime)

## Third-Party Integration Risks

- **Chart.js CDN:** If the CDN is compromised, reports could load malicious JS. Reports are opened in the user's default browser, not an embedded WebView, which provides some isolation.
- **GitHub API:** Update check fetches release metadata. No credentials are sent.

## Missing Protections

For a system handling sensitive mental health data, the following protections are **not implemented**:

| Protection | Status | Impact |
|------------|--------|--------|
| Database encryption at rest | **Missing** | SQLite DB is plaintext |
| Automatic screen lock / timeout | **Missing** | App stays open indefinitely |
| Audit log of access | **Missing** | No record of who viewed what |
| Secure deletion (shredding) | **Missing** | Deleted files may be recoverable from filesystem |
| Backup encryption | **Missing** | `.db` backups are plaintext copies |

## Recommendations

1. **P1:** Document and lock down Ed25519 private-key handling before commercial distribution.
2. **P1:** Make secure-folder keyring fallback explicit to the user.
3. **P2:** Add optional database encryption (SQLCipher or similar).
4. **P2:** Add an optional app-level passcode for launch.
5. **P3:** Encrypt shareable report HTML with a user-provided password if they contain sensitive data.
