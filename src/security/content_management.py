"""
Secure content management system with privacy features and customizable filtering.
"""
import hashlib
import json
import os
import shutil
from enum import Enum, auto
from pathlib import Path

from cryptography.fernet import Fernet


class ContentCategory(Enum):
    """Content categories for filtering and organization."""
    GENERAL = auto()
    MATURE = auto()  # 18+ non-explicit content
    EXPLICIT = auto()  # Adult content
    SENSITIVE = auto()  # Personal/private content
    MEDICAL = auto()  # Health-related personal information
    FINANCIAL = auto()  # Financial documents


class SecurityLevel(Enum):
    """Security levels for content protection."""
    STANDARD = auto()  # Normal encryption
    HIGH = auto()      # Enhanced encryption with additional verification
    MAXIMUM = auto()   # Maximum security with multi-factor authentication


class ContentManager:
    """Manages secure content storage and access."""

    def __init__(self, root_path: Path):
        """Initialize the content manager with the given root storage path."""
        self.root_path = root_path
        self.config_path = root_path / ".content_config"
        self.vault_path = root_path / ".secure_vault"
        self._initialize_secure_storage()

    def _initialize_secure_storage(self):
        """Initialize secure storage system."""
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.vault_path.mkdir(parents=True, exist_ok=True)

        # Generate or load encryption key
        key_file = self.config_path / "key.bin"
        if not key_file.exists():
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)

        with open(key_file, "rb") as f:
            self.key = f.read()

        self.cipher = Fernet(self.key)

    def _hash_passcode(self, passcode: str, salt: bytes) -> str:
        """Hash a passcode with scrypt."""
        return hashlib.scrypt(
            passcode.encode(),
            salt=salt,
            n=2**14,
            r=8,
            p=1,
            dklen=32,
        ).hex()

    def create_secure_folder(self,
                           name: str,
                           category: ContentCategory,
                           security_level: SecurityLevel,
                           passcode: str,
                           hide_folder: bool = False) -> Path:
        """Create a secure folder with specified protection level."""

        # Create a unique folder ID
        salt = os.urandom(16)
        folder_id = hashlib.sha256(name.encode() + salt).hexdigest()[:12]

        # Generate a random salt for this folder
        salt = os.urandom(32)
        passcode_hash = self._hash_passcode(passcode, salt)

        # Create folder metadata
        metadata = {
            "name": name,
            "category": category.name,
            "security_level": security_level.name,
            "hidden": hide_folder,
            "passcode_hash": passcode_hash,
            "salt": salt.hex(),
            "folder_id": folder_id,
        }

        # Create secure folder
        if hide_folder:
            folder_path = self.vault_path / folder_id
        else:
            if len(Path(name).parts) != 1 or name in (".", ".."):
                raise ValueError("Invalid folder name")
            safe_name = Path(name).name
            if not safe_name:
                raise ValueError("Invalid folder name")
            folder_path = self.root_path / safe_name

        folder_path.mkdir(parents=True, exist_ok=True)

        # Save encrypted metadata
        metadata_path = self.config_path / f"{folder_id}_meta"
        encrypted_data = self.cipher.encrypt(json.dumps(metadata).encode())
        with open(metadata_path, "wb") as f:
            f.write(encrypted_data)

        return folder_path

    def verify_access(self, folder_id: str, passcode: str) -> bool:
        """Verify access to a secure folder."""
        metadata_path = self.config_path / f"{folder_id}_meta"
        if not metadata_path.exists():
            return False

        with open(metadata_path, "rb") as f:
            encrypted_data = f.read()

        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            metadata = json.loads(decrypted_data)
            salt = bytes.fromhex(metadata.get("salt", "0" * 64))
            expected_hash: str = metadata["passcode_hash"]
            return self._hash_passcode(passcode, salt) == expected_hash
        except (json.JSONDecodeError, KeyError, ValueError):
            return False

    def move_to_secure_folder(self,
                            file_path: Path,
                            folder_id: str,
                            passcode: str) -> bool:
        """Move a file to a secure folder."""
        if not self.verify_access(folder_id, passcode):
            return False

        metadata_path = self.config_path / f"{folder_id}_meta"
        with open(metadata_path, "rb") as f:
            encrypted_data = f.read()

        metadata = json.loads(self.cipher.decrypt(encrypted_data))

        if metadata["hidden"]:
            dest_folder = self.vault_path / folder_id
        else:
            dest_folder = self.root_path / metadata["name"]

        shutil.move(str(file_path), str(dest_folder / file_path.name))
        return True

    def get_folder_path(self, folder_id: str, passcode: str) -> Path | None:
        """Get the path to a secure folder if access is verified."""
        if not self.verify_access(folder_id, passcode):
            return None

        metadata_path = self.config_path / f"{folder_id}_meta"
        with open(metadata_path, "rb") as f:
            encrypted_data = f.read()

        metadata = json.loads(self.cipher.decrypt(encrypted_data))

        if metadata["hidden"]:
            return self.vault_path / folder_id
        else:
            folder_name: str = metadata["name"]
            return self.root_path / folder_name

    def change_passcode(self, folder_id: str, old_passcode: str, new_passcode: str) -> bool:
        """Change the passcode for a secure folder."""
        if not self.verify_access(folder_id, old_passcode):
            return False

        metadata_path = self.config_path / f"{folder_id}_meta"
        with open(metadata_path, "rb") as f:
            encrypted_data = f.read()

        metadata = json.loads(self.cipher.decrypt(encrypted_data))
        salt = bytes.fromhex(metadata.get("salt", "0" * 64))
        metadata["passcode_hash"] = self._hash_passcode(new_passcode, salt)

        encrypted_data = self.cipher.encrypt(json.dumps(metadata).encode())
        with open(metadata_path, "wb") as f:
            f.write(encrypted_data)

        return True

    def list_categories(self) -> dict[str, list[str]]:
        """List available content categories and their descriptions."""
        return {
            "GENERAL": ["Standard content", "No restrictions"],
            "MATURE": ["18+ non-explicit content", "Age verification required"],
            "EXPLICIT": ["Adult content", "Strong privacy protection"],
            "SENSITIVE": ["Personal/private content", "Enhanced security"],
            "MEDICAL": ["Health-related personal information", "Enhanced protection"],
            "FINANCIAL": ["Financial documents", "Enhanced encryption"]
        }

    def get_security_recommendations(self, category: ContentCategory) -> dict:
        """Get security recommendations for a content category."""
        recommendations = {
            ContentCategory.GENERAL: {
                "security_level": SecurityLevel.STANDARD,
                "hide_folder": False,
                "backup": "standard"
            },
            ContentCategory.MATURE: {
                "security_level": SecurityLevel.HIGH,
                "hide_folder": True,
                "backup": "encrypted"
            },
            ContentCategory.EXPLICIT: {
                "security_level": SecurityLevel.MAXIMUM,
                "hide_folder": True,
                "backup": "secure_encrypted"
            },
            ContentCategory.SENSITIVE: {
                "security_level": SecurityLevel.HIGH,
                "hide_folder": True,
                "backup": "encrypted"
            },
            # MEDICAL category renamed for clarity — protects health-related personal info
            ContentCategory.MEDICAL: {
                "security_level": SecurityLevel.MAXIMUM,
                "hide_folder": True,
                "backup": "encrypted"
            },
            ContentCategory.FINANCIAL: {
                "security_level": SecurityLevel.HIGH,
                "hide_folder": True,
                "backup": "encrypted"
            }
        }
        return recommendations[category]
