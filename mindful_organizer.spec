# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for Hearth.
#
#   macOS:    produces dist/Hearth.app (windowed .app bundle)
#   Windows:  produces dist/Hearth/hearth.exe (one-dir, windowed)
#
# Usage:  pyinstaller mindful_organizer.spec --clean --noconfirm
#
# The optional ML/NLP stacks (scikit-learn, hdbscan, umap, matplotlib) are
# collected ONLY when they are actually installed, so a lean install without the
# [ml,nlp] extras still builds — the app degrades gracefully at runtime.

import os
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# SPECPATH is the directory containing this spec file (the project root).
SPEC_DIR = os.path.abspath(SPECPATH)
SRC_DIR = os.path.join(SPEC_DIR, "src")
IS_MACOS = sys.platform == "darwin"


def _maybe(pkg):
    """Return submodules of an optional package, or [] if it isn't installed."""
    import importlib.util

    if importlib.util.find_spec(pkg) is None:
        return []
    return collect_submodules(pkg)


def _maybe_data(pkg):
    import importlib.util

    if importlib.util.find_spec(pkg) is None:
        return []
    return collect_data_files(pkg)


# --- Hidden imports -------------------------------------------------------
hidden_imports = []
hidden_imports += collect_submodules("PyQt6")
hidden_imports += collect_submodules("cryptography")
hidden_imports += ["sqlite3", "json", "csv", "keyring", "certifi", "psutil"]
# Optional, only if installed:
for _pkg in ("numpy", "sklearn", "pandas", "matplotlib", "hdbscan", "umap"):
    hidden_imports += _maybe(_pkg)

# --- Data files -----------------------------------------------------------
added_data = [
    (os.path.join(SPEC_DIR, "resources"), "resources"),
    (os.path.join(SPEC_DIR, "windows_store", "assets"), os.path.join("windows_store", "assets")),
]
for _pkg in ("sklearn", "hdbscan"):
    added_data += _maybe_data(_pkg)

# --- Analysis -------------------------------------------------------------
a = Analysis(
    [os.path.join(SRC_DIR, "main.py")],
    pathex=[SRC_DIR],
    binaries=[],
    datas=added_data,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "_tkinter", "test", "unittest", "pytest", "sphinx"],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

# Brand the executable. macOS app bundles wrap a plain unix executable; Windows
# uses hearth.exe to match the MSIX manifest (Executable="Hearth\\hearth.exe").
_icon = os.path.join(SPEC_DIR, "windows_store", "assets", "app_icon.ico")

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="hearth",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # UPX can corrupt PyQt6/macOS binaries; not worth the risk
    console=False,
    disable_windowed_traceback=False,
    icon=_icon if os.path.exists(_icon) else None,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="Hearth",
)

# macOS application bundle -------------------------------------------------
if IS_MACOS:
    _icns = os.path.join(SPEC_DIR, "windows_store", "assets", "Hearth.icns")
    app = BUNDLE(
        coll,
        name="Hearth.app",
        icon=_icns if os.path.exists(_icns) else None,
        bundle_identifier="io.hearthproject.hearth",
        version="1.1.0",
        info_plist={
            "CFBundleName": "Hearth",
            "CFBundleDisplayName": "Hearth",
            "CFBundleShortVersionString": "1.1.0",
            "CFBundleVersion": "1.1.0",
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "11.0",
            # Single-user local tool; explicitly opt out of App Sandbox file
            # prompts for the user's own home-dir data directory.
            "LSApplicationCategoryType": "public.app-category.healthcare-fitness",
        },
    )
