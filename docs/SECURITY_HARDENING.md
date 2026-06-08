# Security Hardening Guide

**Scope:** Hearth (Mindful Organizer) desktop application — security controls for market readiness.  
**Audience:** Maintainers, security auditors, release engineers.  
**Last updated:** 2026-06-08

---

## 1. Threat Model Summary

Hearth stores and processes sensitive mental-health data. The primary threats we defend against are:

| Threat                                              | Mitigation                                                                                                              | Status      |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ----------- |
| **Physical device theft → plaintext data exposure** | Filesystem permissions (0700 data dir, 0600 DB), OS keyring for encryption keys, future SQLCipher upgrade documented.   | Partial     |
| **Malicious update binary**                         | HTTPS-only release URLs, pinned repository, Ed25519 signature verification hook ready for integration.                  | Implemented |
| **License forgery**                                 | Ed25519 signatures; private key never shipped; issuer-side hardening (permissions, repo-leak warnings).                 | Implemented |
| **Accidental secret leakage (private key)**         | 0600 file-permission enforcement, git-repo detection warning, env-var preference.                                       | Implemented |
| **Keyring unavailable → silent weak encryption**    | Fallback is now **opt-in by flag** (`force_keyring`), fallback state is logged and exposed via `keyring_fallback_used`. | Implemented |

---

## 2. Keyring Requirements and Fallback Behavior

### 2.1 Normal operation

`ContentManager` (in `src/security/content_management.py`) stores the Fernet encryption key in the OS credential store:

- **macOS** — Keychain
- **Windows** — Credential Manager
- **Linux** — freedesktop SecretService (e.g. GNOME Keyring, KWallet)

### 2.2 Fallback behaviour

If the `keyring` library is missing or the backend is locked / unavailable:

1. If `force_keyring=True` was passed to `ContentManager`, a `RuntimeError` is raised **immediately**. No disk fallback occurs.
2. Otherwise, the manager falls back to an on-disk `key.bin` file with **0600** permissions.
3. The flag `ContentManager.keyring_fallback_used` is set to `True`.
4. A prominent **WARNING** is logged:
   ```
   OS keyring unavailable (...). Falling back to on-disk key with restricted
   permissions. Encryption strength is reduced — consider enabling a keyring backend.
   ```

### 2.3 Recommended deployment controls

- **macOS / Windows:** Keyring works out-of-the-box in most environments. No action needed.
- **Linux (headless / CI):** Install `gnome-keyring` and launch `gnome-keyring-daemon` before the app, or set `force_keyring=True` and fail closed if keyring is unavailable.
- **Packaging:** Document keyring requirements in the installer / README so users know the fallback is occurring.

---

## 3. License Key Issuance Controls

### 3.1 Key material lifecycle

| Stage                       | Location                                                    | Protection                                   |
| --------------------------- | ----------------------------------------------------------- | -------------------------------------------- |
| **Private signing key**     | Build/release host only (password manager, HSM, or env var) | 0600 filesystem permissions, never committed |
| **Public verification key** | Embedded in `src/core/subscription_manager.py`              | Safe to ship — public by design              |

### 3.2 Issuer script (`scripts/issue_license.py`)

The script enforces the following controls:

1. **Input validation** — `tier` must be a known `SubscriptionTier`; `days` must be `1 … 3650` (10 years max).
2. **Permission check** — If the private key is loaded from a file (`MINDFUL_LICENSE_PRIVATE_KEY_FILE`), the file **must** have mode `0600`. The script exits with an error if permissions are looser.
3. **Git-repo leak warning** — If the private key file resides inside a git repository, a loud `WARNING` is emitted.
4. **Env-var preference** — `MINDFUL_LICENSE_PRIVATE_KEY` (inline base64) is accepted for CI/automation, but the file-based flow (`MINDFUL_LICENSE_PRIVATE_KEY_FILE`) is preferred for local development.

### 3.3 Rotation guidance

If the private key is ever suspected of compromise:

1. Generate a new keypair (`--generate-keypair`).
2. Replace `_PUBLIC_KEY_B64` in `src/core/subscription_manager.py`.
3. Re-issue all active licenses with the new key.
4. Revoke old licenses by distributing a minimum-app-version that drops support for the old public key.

---

## 4. Auto-Updater Security Notes

`AutoUpdater` (`src/core/auto_updater.py`) queries GitHub releases for updates.

### 4.1 Network hardening

- **Pinned repository** — `owner` and `repo` are hard-coded class constants (`ntoledo319/Mindful-Organizer`). They are **not** constructor parameters and cannot be overridden at runtime.
- **HTTPS enforcement** — Both the GitHub API URL and every `browser_download_url` are validated with `_ensure_https()`. Any non-HTTPS URL raises `ValueError` and aborts the operation.
- **Request timeout** — All HTTP operations use a `30` second timeout to prevent indefinite hangs.
- **SSL context** — Uses `certifi` CA bundle when available (required for PyInstaller-frozen builds that lack system trust stores).

### 4.2 Download integrity (future integration)

`AutoUpdater.verify_update_signature(file_path, signature_path, public_key_b64)` is a ready-to-use Ed25519 signature-verification hook. Once release artifacts are signed:

1. Download the update binary **and** its detached `.sig` file.
2. Call `verify_update_signature()` with the binary path, signature path, and the public key.
3. Only proceed with installation if the method returns `True`.

Until signatures are produced, the method returns `False` and logs the failure reason.

### 4.3 State file

Update check timestamps and skipped versions are stored in `<data_dir>/update_state.json`. The file inherits the data-directory permissions (0700 / 0600).

---

## 5. Data Directory Permissions

| Path                                    | Permission | Rationale                                          |
| --------------------------------------- | ---------- | -------------------------------------------------- |
| Data directory (`~/.mindful_organizer`) | `0700`     | Only the owning user can list or enter.            |
| SQLite database                         | `0600`     | Only the owning user can read or write.            |
| Secure vault (`key.bin` fallback)       | `0600`     | Fallback encryption key is restricted.             |
| Update downloads                        | `0600`     | Binaries downloaded by the updater are restricted. |

---

## 6. Checklist for Release Engineers

- [ ] Verify the build host has a working OS keyring or document the fallback warning.
- [ ] Confirm `MINDFUL_LICENSE_PRIVATE_KEY` is set only in the release CI pipeline, not in developer environments.
- [ ] If using a file for the private key, ensure mode `0600` and place it outside the git repo.
- [ ] Rotate test/demo keypairs so they are distinct from production signing material.
- [ ] Verify GitHub releases page uses HTTPS (enforced by code, but verify manually).
- [ ] Run `ruff check src/security/ scripts/issue_license.py src/core/auto_updater.py` and resolve all findings.
- [ ] Run security-focused unit tests (`pytest tests/unit/test_content_management.py -v`).
