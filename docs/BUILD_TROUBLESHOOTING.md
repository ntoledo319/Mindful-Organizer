# Build Troubleshooting Guide

## PyInstaller COLLECT `FileNotFoundError: libqwebp.dylib`

### Symptom

PyInstaller fails during the **COLLECT** step with:

```
FileNotFoundError: [Errno 2] No such file or directory:
'/Users/.../dist/Hearth/_internal/PyQt6/Qt6/plugins/imageformats/libqwebp.dylib'
```

The `_internal` directory inside `dist/Hearth/` is not created properly, or the
build aborts before all Qt plugins are copied.

### Root Cause

This is a **cache / stale-artifact corruption issue**, not a spec-file bug.
PyInstaller 6.x maintains caches in two places:

1. `build/mindful_organizer/` — the per-build work directory
2. `$HOME/Library/Application Support/pyinstaller` — the global binary/analysis cache

If a previous build was interrupted (Ctrl-C, disk full, IDE kill, etc.), the
`dist/Hearth/` directory can be left in a **partial state**. Subsequent runs may
attempt to re-use or overwrite corrupted symlinks/Mach-O headers in `dist/`,
which causes the COLLECT step to abort when it tries to copy Qt plugins into a
broken `_internal` tree.

**PyInstaller’s `--clean` only wipes `build/`, NOT `dist/`**.

### Fix (Nuclear Clean)

Run the following **before** invoking `pyinstaller`:

```bash
# 1. Remove stale output directories (PyInstaller --clean does NOT do this)
rm -rf dist/Hearth dist/Hearth.app build/mindful_organizer

# 2. Remove PyInstaller's global binary cache (macOS path)
rm -rf "$HOME/Library/Application Support/pyinstaller"

# 3. Rebuild
venv312/bin/pyinstaller mindful_organizer.spec --clean --noconfirm
```

> **Why this works:** Deleting `dist/Hearth/` ensures COLLECT starts from a
> completely empty directory. Clearing the global cache forces PyInstaller to
> re-extract and re-analyze all binaries (including PyQt6 plugins) from scratch.

### Prevention

Add a pre-build clean step to your build script or CI:

```bash
#!/bin/bash
set -euo pipefail
rm -rf dist/Hearth dist/Hearth.app build/mindful_organizer
rm -rf "$HOME/Library/Application Support/pyinstaller"
pyinstaller mindful_organizer.spec --clean --noconfirm
```

### Validation

After a successful build, verify the artifact:

```bash
# Check the onedir executable
dist/Hearth/hearth --version

# Check the .app bundle
dist/Hearth.app/Contents/MacOS/hearth --version

# Verify the missing plugin is present
ls dist/Hearth/_internal/PyQt6/Qt6/plugins/imageformats/libqwebp.dylib
ls dist/Hearth.app/Contents/Frameworks/PyQt6/Qt6/plugins/imageformats/libqwebp.dylib
```

### Related

- PyInstaller issue #7827 — COLLECT race conditions with pre-existing `dist/`
  directories on macOS.
- PyInstaller 6.x changed the `_internal` layout; stale bundles from v5.x can
  conflict.
