"""
Security-critical tests for ContentManager.

Covers encryption round-trips, passcode verification, path-traversal
protection, and secure-folder lifecycle.
"""

from pathlib import Path

import pytest

try:
    from src.security.content_management import ContentCategory, ContentManager, SecurityLevel
    _HAS_MODULE = True
except ImportError:
    _HAS_MODULE = False

pytestmark = pytest.mark.skipif(not _HAS_MODULE, reason="content_management module not available")


class TestSecureFolderLifecycle:
    def test_create_secure_folder(self, tmp_data_dir: Path) -> None:
        manager = ContentManager(tmp_data_dir)
        folder = manager.create_secure_folder(
            name="Medical_Records",
            category=ContentCategory.MEDICAL,
            security_level=SecurityLevel.STANDARD,
            passcode="correct_horse_battery_staple",
        )
        assert folder.exists()
        assert folder.is_dir()

    def test_verify_correct_passcode(self, tmp_data_dir: Path) -> None:
        manager = ContentManager(tmp_data_dir)
        manager.create_secure_folder(
            name="Financials",
            category=ContentCategory.FINANCIAL,
            security_level=SecurityLevel.HIGH,
            passcode="secret123",
        )
        # Derive folder_id from metadata to test verify_access
        meta_files = list(manager.config_path.glob("*_meta"))
        assert len(meta_files) == 1
        folder_id = meta_files[0].stem.replace("_meta", "")
        assert manager.verify_access(folder_id, "secret123") is True

    def test_verify_wrong_passcode(self, tmp_data_dir: Path) -> None:
        manager = ContentManager(tmp_data_dir)
        manager.create_secure_folder(
            name="Secrets",
            category=ContentCategory.SENSITIVE,
            security_level=SecurityLevel.STANDARD,
            passcode="right",
        )
        meta_files = list(manager.config_path.glob("*_meta"))
        folder_id = meta_files[0].stem.replace("_meta", "")
        assert manager.verify_access(folder_id, "wrong") is False

    def test_path_traversal_rejected(self, tmp_data_dir: Path) -> None:
        manager = ContentManager(tmp_data_dir)
        with pytest.raises(ValueError, match="Invalid folder name"):
            manager.create_secure_folder(
                name="../../etc/passwd",
                category=ContentCategory.GENERAL,
                security_level=SecurityLevel.STANDARD,
                passcode="x",
            )

    def test_hidden_folder_in_vault(self, tmp_data_dir: Path) -> None:
        manager = ContentManager(tmp_data_dir)
        folder = manager.create_secure_folder(
            name="HiddenStuff",
            category=ContentCategory.SENSITIVE,
            security_level=SecurityLevel.MAXIMUM,
            passcode="hide_me",
            hide_folder=True,
        )
        # Hidden folders should live inside the vault path, not root_path
        assert manager.vault_path in folder.parents


class TestEncryptionRoundTrip:
    def test_metadata_decrypts_correctly(self, tmp_data_dir: Path) -> None:
        manager = ContentManager(tmp_data_dir)
        manager.create_secure_folder(
            name="Test",
            category=ContentCategory.GENERAL,
            security_level=SecurityLevel.STANDARD,
            passcode="pw",
        )
        meta_files = list(manager.config_path.glob("*_meta"))
        assert len(meta_files) == 1
        encrypted = meta_files[0].read_bytes()
        # Should not be plaintext JSON
        raw_text = encrypted.decode("utf-8", errors="replace")
        assert '"name": "Test"' not in raw_text
        # Decrypt via the manager's cipher
        decrypted = manager.cipher.decrypt(encrypted)
        data = __import__("json").loads(decrypted)
        assert data["name"] == "Test"
        assert data["category"] == "GENERAL"
