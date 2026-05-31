"""
Auto-updater for Mindful Organizer.

Checks GitHub releases for newer versions and prompts the user to update.
Supports macOS (Sparkle-style), Windows (WinSparkle-style), and Linux
(custom download + replace).
"""

from __future__ import annotations

import json
import logging
import platform
import re
import subprocess
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

from core.paths import get_data_dir as _get_data_dir  # noqa: E402

DATA_DIR = _get_data_dir(create=False)
UPDATE_STATE_FILE = DATA_DIR / "update_state.json"

GITHUB_API_URL = "https://api.github.com/repos/{owner}/{repo}/releases/latest"


def _ssl_context():
    """Return an SSL context with a usable CA bundle.

    A PyInstaller-frozen app ships its own Python without the system trust store,
    so urllib's default context fails CERTIFICATE_VERIFY_FAILED. Prefer certifi's
    bundled CA file (also bundled into the app); fall back to the default context
    in a normal install where system certs exist.
    """
    import ssl

    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


@dataclass
class ReleaseInfo:
    version: str
    published_at: datetime
    release_notes: str
    download_url: str | None = None
    asset_name: str | None = None


class AutoUpdater:
    """Check for and manage application updates."""

    CHECK_INTERVAL_HOURS = 24

    def __init__(
        self,
        current_version: str,
        owner: str = "ntoledo319",
        repo: str = "Mindful-Organizer",
        data_dir: Path | None = None,
    ) -> None:
        self.current_version = current_version.lstrip("v")
        self.owner = owner
        self.repo = repo
        self._data_dir = data_dir or DATA_DIR
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = self._data_dir / "update_state.json"
        self._state = self._load_state()

    def _load_state(self) -> dict[str, Any]:
        if self._state_file.exists():
            try:
                return json.loads(self._state_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return {"last_check": None, "skipped_version": None}

    def _save_state(self) -> None:
        try:
            self._state_file.write_text(json.dumps(self._state, indent=2, default=str), encoding="utf-8")
        except OSError:
            logger.exception("Failed to save update state")

    def should_check(self) -> bool:
        """Return True if enough time has passed since last check."""
        last = self._state.get("last_check")
        if last is None:
            return True
        try:
            last_dt = datetime.fromisoformat(last)
            return datetime.now() - last_dt > timedelta(hours=self.CHECK_INTERVAL_HOURS)
        except (ValueError, TypeError):
            return True

    def check(self) -> ReleaseInfo | None:
        """Query GitHub API for the latest release."""
        if not self.should_check():
            logger.debug("Skipping update check — checked recently")
            return None

        url = GITHUB_API_URL.format(owner=self.owner, repo=self.repo)
        try:
            req = urllib.request.Request(
                url,
                headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "Mindful-Organizer-Updater"},
            )
            with urllib.request.urlopen(req, timeout=15, context=_ssl_context()) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logger.warning("Update check failed: %s", e)
            return None

        self._state["last_check"] = datetime.now().isoformat()
        self._save_state()

        tag = data.get("tag_name", "")
        version = re.sub(r"^v", "", tag)
        if not version or not self._is_newer(version):
            return None

        # Find best asset for current platform
        asset_url, asset_name = self._find_asset(data.get("assets", []))

        return ReleaseInfo(
            version=version,
            published_at=datetime.fromisoformat(data.get("published_at", "").replace("Z", "+00:00")),
            release_notes=data.get("body", ""),
            download_url=asset_url,
            asset_name=asset_name,
        )

    def skip_version(self, version: str) -> None:
        """Mark a version as skipped so it won't prompt again."""
        self._state["skipped_version"] = version
        self._save_state()

    def is_skipped(self, version: str) -> bool:
        return self._state.get("skipped_version") == version

    @staticmethod
    def _is_newer(remote: str, local: str | None = None) -> bool:
        """Compare semantic versions."""
        local = local or ""

        def parse(v: str) -> tuple[int, ...]:
            parts = re.split(r"[.+]", v)
            out: list[int] = []
            for p in parts:
                try:
                    out.append(int(p))
                except ValueError:
                    out.append(0)
            return tuple(out)

        return parse(remote) > parse(local)

    def _find_asset(self, assets: list[dict[str, Any]]) -> tuple[str | None, str | None]:
        system = platform.system().lower()
        machine = platform.machine().lower()
        keywords: list[str] = []

        if system == "darwin":
            keywords = ["macos", "mac", "dmg", "osx"]
            if "arm" in machine or "aarch64" in machine:
                keywords.insert(0, "arm64")
            else:
                keywords.insert(0, "x86_64")
        elif system == "windows":
            keywords = ["windows", "win", "exe", "msi", "msix"]
        elif system == "linux":
            keywords = ["linux", "appimage", "deb", "rpm"]

        for keyword in keywords:
            for asset in assets:
                name = asset.get("name", "").lower()
                if keyword in name:
                    return asset.get("browser_download_url"), asset.get("name")
        # Fallback to first asset
        if assets:
            return assets[0].get("browser_download_url"), assets[0].get("name")
        return None, None

    def download_update(self, release: ReleaseInfo, dest_dir: Path | None = None) -> Path | None:
        """Download the update asset to the given directory."""
        if not release.download_url or not release.asset_name:
            return None
        dest = (dest_dir or self._data_dir / "updates")
        dest.mkdir(parents=True, exist_ok=True)
        target = dest / release.asset_name

        try:
            urllib.request.urlretrieve(release.download_url, target)
            logger.info("Downloaded update to %s", target)
            return target
        except Exception as e:
            logger.error("Download failed: %s", e)
            return None

    def open_download_page(self) -> None:
        """Open the GitHub releases page in the default browser."""
        url = f"https://github.com/{self.owner}/{self.repo}/releases/latest"
        try:
            if platform.system() == "Darwin":
                subprocess.run(["open", url], check=False)
            elif platform.system() == "Windows":
                subprocess.run(["start", url], shell=True, check=False)
            else:
                subprocess.run(["xdg-open", url], check=False)
        except Exception as e:
            logger.warning("Could not open browser: %s", e)
