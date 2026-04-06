# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for Mindful Organizer
# Builds a one-dir Windows executable (windowed mode, no console)
#
# Usage:
#   pyinstaller mindful_organizer.spec
#

import os
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# ---------------------------------------------------------------------------
# Path configuration
# ---------------------------------------------------------------------------
SPEC_DIR = os.path.abspath(os.path.dirname(SPECPATH))
SRC_DIR = os.path.join(SPEC_DIR, 'src')

# ---------------------------------------------------------------------------
# Hidden imports
# PyQt6 and ML libraries need explicit enumeration because PyInstaller
# cannot always detect runtime imports in these packages.
# ---------------------------------------------------------------------------
hidden_imports = []
hidden_imports += collect_submodules('PyQt6')
hidden_imports += collect_submodules('PyQt6.QtCore')
hidden_imports += collect_submodules('PyQt6.QtGui')
hidden_imports += collect_submodules('PyQt6.QtWidgets')
hidden_imports += collect_submodules('numpy')
hidden_imports += collect_submodules('sklearn')
hidden_imports += collect_submodules('cryptography')
hidden_imports += [
    'hdbscan',
    'umap',
    'matplotlib',
    'matplotlib.backends.backend_qt5agg',
    'seaborn',
    'sqlite3',
    'json',
    'csv',
    'dateutil',
    'dateutil.parser',
    'dateutil.tz',
]

# ---------------------------------------------------------------------------
# Data files
# Resources directory (meditations, guided sessions, etc.)
# Windows Store assets (icons, logos)
# ---------------------------------------------------------------------------
added_data = [
    (os.path.join(SPEC_DIR, 'resources'), 'resources'),
    (os.path.join(SPEC_DIR, 'windows_store', 'assets'), os.path.join('windows_store', 'assets')),
]

# Collect additional data files from ML libraries that ship models/config
added_data += collect_data_files('sklearn')
added_data += collect_data_files('hdbscan')

# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
a = Analysis(
    [os.path.join(SRC_DIR, 'main.py')],
    pathex=[SRC_DIR],
    binaries=[],
    datas=added_data,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        '_tkinter',
        'test',
        'unittest',
        'pytest',
        'sphinx',
        'setuptools',
        'pip',
        'distutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# ---------------------------------------------------------------------------
# PYZ archive (compressed Python bytecode)
# ---------------------------------------------------------------------------
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

# ---------------------------------------------------------------------------
# EXE
# one-file mode disabled (one-dir) for faster startup
# console disabled (windowed GUI application)
# ---------------------------------------------------------------------------
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='mindful-organizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    icon=os.path.join(SPEC_DIR, 'windows_store', 'assets', 'app_icon.ico'),
    version_info={
        'FileVersion': (1, 0, 0, 0),
        'ProductVersion': (1, 0, 0, 0),
        'FileDescription': 'Mindful Organizer - Mental health-aware productivity',
        'InternalName': 'mindful-organizer',
        'OriginalFilename': 'mindful-organizer.exe',
        'ProductName': 'Mindful Organizer',
        'CompanyName': 'Nicholas Toledo',
        'LegalCopyright': 'Copyright 2026 Nicholas Toledo. MIT License.',
    },
    uac_admin=False,          # asInvoker -- no elevation required
    uac_uiaccess=False,
    manifest=None,            # use default manifest (asInvoker)
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ---------------------------------------------------------------------------
# COLLECT (one-dir bundle)
# ---------------------------------------------------------------------------
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MindfulOrganizer',
)
