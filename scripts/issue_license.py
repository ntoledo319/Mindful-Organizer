#!/usr/bin/env python3
"""Issue a Hearth license key.

This is the issuer-side tool. It requires the Ed25519 private signing key,
which lives ONLY on the build/release host — never in the repo, never in any
shipped binary.

Usage:
    MINDFUL_LICENSE_PRIVATE_KEY=<base64> \\
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
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from core.subscription_manager import SubscriptionManager, SubscriptionTier


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
        priv.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )
    ).decode()
    print("# New keypair generated. Store the private key SECURELY.")
    print(f"PUBLIC_KEY_B64  = {pub_b64}")
    print(f"PRIVATE_KEY_B64 = {priv_b64}")


def issue(tier: str, days: int) -> None:
    priv_b64 = os.environ.get("MINDFUL_LICENSE_PRIVATE_KEY")
    if not priv_b64:
        sys.exit("MINDFUL_LICENSE_PRIVATE_KEY env var is required.")

    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        mgr = SubscriptionManager(data_dir=Path(tmp), private_key_b64=priv_b64)
        key = mgr.generate_key(SubscriptionTier(tier), days=days)
    print(key)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tier", choices=[t.value for t in SubscriptionTier], default="pro"
    )
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
