#!/usr/bin/env python3
# =============================================================================
# WARNING: PRIVATE SIGNING MATERIAL
# =============================================================================
# This script handles the Ed25519 private key used to sign Hearth license keys.
# The private key MUST NEVER be committed to version control, shipped in any
# binary, or shared via insecure channels. It should live ONLY in:
#   - A hardware security module (HSM) or secure enclave, OR
#   - A password manager / secrets manager (1Password, AWS Secrets Manager,
#     Azure Key Vault, etc.), OR
#   - The build/release host with restrictive filesystem permissions (0600).
# =============================================================================
"""Issue a Hearth license key.

This is the issuer-side tool. It requires the Ed25519 private signing key,
which lives ONLY on the build/release host — never in the repo, never in any
shipped binary.

Usage:
    MINDFUL_LICENSE_PRIVATE_KEY=<base64> \\
        python scripts/issue_license.py --tier pro --days 365

    MINDFUL_LICENSE_PRIVATE_KEY_FILE=/secure/path/to/key.pem \\
        python scripts/issue_license.py --tier pro --days 365

To bootstrap a new project, generate a keypair once and store the private
key in a password manager + the build host:

    python scripts/issue_license.py --generate-keypair

Then paste the public key into src/core/subscription_manager.py as
_PUBLIC_KEY_B64.
"""

from __future__ import annotations

import argparse
import base64
import logging
import os
import stat
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from core.subscription_manager import SubscriptionManager, SubscriptionTier

logger = logging.getLogger(__name__)


def generate_keypair() -> None:
    priv = Ed25519PrivateKey.generate()
    priv_b64 = base64.b64encode(
        priv.private_bytes(
            serialization.Encoding.Raw,
            serialization.PrivateFormat.Raw,
            serialization.NoEncryption(),
        )
    ).decode()
    pub_b64 = base64.b64encode(
        priv.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    ).decode()
    print("# New keypair generated. Store the private key SECURELY.")
    print(f"PUBLIC_KEY_B64  = {pub_b64}")
    print(f"PRIVATE_KEY_B64 = {priv_b64}")


def _is_inside_git_repo(path: Path) -> bool:
    """Return True if *path* resides inside a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        repo_root = Path(result.stdout.strip()).resolve()
        return repo_root in path.resolve().parents or repo_root == path.resolve()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _load_private_key() -> str:
    """Load the private key from env or file, enforcing security controls."""
    priv_b64 = os.environ.get("MINDFUL_LICENSE_PRIVATE_KEY")
    key_file = os.environ.get("MINDFUL_LICENSE_PRIVATE_KEY_FILE")

    if priv_b64:
        return priv_b64

    if key_file:
        key_path = Path(key_file).resolve()
        if _is_inside_git_repo(key_path):
            logger.warning(
                "SECURITY WARNING: The private key file %s appears to be inside a "
                "git repository. It should be stored OUTSIDE version control to "
                "prevent accidental commits.",
                key_path,
            )

        mode = key_path.stat().st_mode
        if stat.S_IMODE(mode) != 0o600:
            sys.exit(
                f"Private key file {key_path} has permissions "
                f"{oct(stat.S_IMODE(mode))}. Expected 0600. "
                "Refusing to read."
            )
        return key_path.read_text(encoding="utf-8").strip()

    sys.exit("MINDFUL_LICENSE_PRIVATE_KEY or MINDFUL_LICENSE_PRIVATE_KEY_FILE env var is required.")


def _validate_payload(tier: str, days: int) -> None:
    """Validate license payload parameters before signing."""
    if tier not in {t.value for t in SubscriptionTier}:
        raise ValueError(f"Invalid tier: {tier}")
    if days < 1:
        raise ValueError(f"Days must be positive, got {days}")
    if days > 365 * 10:
        raise ValueError(f"Days exceeds maximum (10 years): {days}")


def issue(tier: str, days: int) -> None:
    priv_b64 = _load_private_key()
    _validate_payload(tier, days)

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        mgr = SubscriptionManager(data_dir=Path(tmp), private_key_b64=priv_b64)
        key = mgr.generate_key(SubscriptionTier(tier), days=days)
    print(key)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier", choices=[t.value for t in SubscriptionTier], default="pro")
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument(
        "--generate-keypair",
        action="store_true",
        help="Generate a new signing keypair (run once at project bootstrap).",
    )
    args = parser.parse_args()

    if args.generate_keypair:
        generate_keypair()
    else:
        issue(args.tier, args.days)


if __name__ == "__main__":
    main()
