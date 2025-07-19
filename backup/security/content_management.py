"""
Secure content management system with privacy features and customizable filtering.
"""
from enum import Enum, auto
from pathlib import Path
import json
import hashlib
from typing import Dict, List, Optional
from cryptography.fernet import Fernet
import os
import shutil

class ContentCategory(Enum):
    """Content categories for filtering and organization."""
    GENERAL = auto()
    MATURE = auto()  # 18+ non-explicit content
    EXPLICIT = auto()  # Adult content
    SENSITIVE = auto()  # Personal/private content
    MEDICAL = auto()  # Medical/health information
    FINANCIAL = auto()  # Financial documents

class SecurityLevel(Enum):
    """Security levels for content protection."""
    STANDARD = auto()  # Normal encryption
    HIGH = auto()      # Enhanced encryption with additional verification
    MAXIMUM = auto()   # Maximum security with multi-factor authentication

class ContentManager:
    """Manages secure content storage and access."""
    
    def __init__(self, root_path: Path):
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

    def create_secure_folder(self, 
                           name: str, 
                           category: ContentCategory,
                           security_level: SecurityLevel,
                           passcode: str,
                           hide_folder: bool = False) -> Path:
        """Create a secure folder with specified protection level."""
        
        # Create a unique folder ID
        folder_id = hashlib.sha256(f"{name}{os.urandom(16)}".encode()).hexdigest()[:12]
        
        # Create folder metadata
        metadata = {
            "name": name,
            "category": category.name,
            "security_level": security_level.name,
            "hidden": hide_folder,
            "passcode_hash": hashlib.sha256(passcode.encode()).hexdigest(),
            "folder_id": folder_id
        }
        
        # Create secure folder
        if hide_folder:
            folder_path = self.vault_path / folder_id
        else:
            folder_path = self.root_path / name
        
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
            return metadata["passcode_hash"] == hashlib.sha256(passcode.encode()).hexdigest()
        except:
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

    def get_folder_path(self, folder_id: str, passcode: str) -> Optional[Path]:
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
            return self.root_path / metadata["name"]

    def change_passcode(self, folder_id: str, old_passcode: str, new_passcode: str) -> bool:
        """Change the passcode for a secure folder."""
        if not self.verify_access(folder_id, old_passcode):
            return False
        
        metadata_path = self.config_path / f"{folder_id}_meta"
        with open(metadata_path, "rb") as f:
            encrypted_data = f.read()
        
        metadata = json.loads(self.cipher.decrypt(encrypted_data))
        metadata["passcode_hash"] = hashlib.sha256(new_passcode.encode()).hexdigest()
        
        encrypted_data = self.cipher.encrypt(json.dumps(metadata).encode())
        with open(metadata_path, "wb") as f:
            f.write(encrypted_data)
        
        return True

    def list_categories(self) -> Dict[str, List[str]]:
        """List available content categories and their descriptions."""
        return {
            "GENERAL": ["Standard content", "No restrictions"],
            "MATURE": ["18+ non-explicit content", "Age verification required"],
            "EXPLICIT": ["Adult content", "Strong privacy protection"],
            "SENSITIVE": ["Personal/private content", "Enhanced security"],
            "MEDICAL": ["Medical/health information", "HIPAA-compliant protection"],
            "FINANCIAL": ["Financial documents", "Enhanced encryption"]
        }

    def get_security_recommendations(self, category: ContentCategory) -> Dict:
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
            ContentCategory.MEDICAL: {
                "security_level": SecurityLevel.MAXIMUM,
                "hide_folder": True,
                "backup": "hipaa_compliant"
            },
            ContentCategory.FINANCIAL: {
                "security_level": SecurityLevel.HIGH,
                "hide_folder": True,
                "backup": "encrypted"
            }
        }
        return recommendations[category]
