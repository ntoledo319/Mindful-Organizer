"""Tests for the auto-updater."""

from __future__ import annotations

from pathlib import Path

import pytest

from core.auto_updater import AutoUpdater


@pytest.fixture
def updater(tmp_path: Path) -> AutoUpdater:
    return AutoUpdater("1.0.0", owner="test", repo="test", data_dir=tmp_path)


class TestVersionComparison:
    def test_newer_version(self, updater: AutoUpdater) -> None:
        assert updater._is_newer("1.1.0", "1.0.0")
        assert updater._is_newer("2.0.0", "1.9.9")

    def test_same_version(self, updater: AutoUpdater) -> None:
        assert not updater._is_newer("1.0.0", "1.0.0")

    def test_older_version(self, updater: AutoUpdater) -> None:
        assert not updater._is_newer("0.9.0", "1.0.0")

    def test_patch_version(self, updater: AutoUpdater) -> None:
        assert updater._is_newer("1.0.1", "1.0.0")


class TestSkipVersion:
    def test_skip_and_check(self, updater: AutoUpdater) -> None:
        updater.skip_version("1.2.0")
        assert updater.is_skipped("1.2.0")
        assert not updater.is_skipped("1.3.0")
