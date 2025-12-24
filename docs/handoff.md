# Handoff Notes

## Current State
Mindful Organizer is now a **stable, V1-ready Windows desktop application**.
- **Core Feature**: Smart File Organization with **Safety First** (Plan -> Preview -> Execute -> Undo).
- **Mental Health**: Evidence-based profile system (ADHD, Anxiety, etc.) that adapts the UI.
- **Data**: All data is stored locally in `~/.mindful_optimizer/`.

## Key Changes
- **Refactored File Organizer**: Now uses a Transaction/Undo model.
- **Config-Driven Profiles**: `src/config/profile_presets.yaml` controls the personalization logic.
- **Cleaned UI**: Removed "fake" AI system optimization features to focus on the core value proposition.
- **Fixed Dependencies**: `requirements.txt` is now valid.

## Build Instructions
See `docs/build_windows.md`.
Essentially:
```bash
pip install -r requirements.txt
python src/main.py
```

## Next Steps (Post-V1)
1. **Semantic Search**: Re-enable the `sentence-transformers` logic in `FileOrganizer` if the installer size allows.
2. **Visual Mood Charts**: Implement a `matplotlib` or `PyQtChart` view for the mood history in `Dashboard`.
3. **Localization**: Move hardcoded strings to a translation file.

## Known Issues
- Search is currently a simple filename wildcard match.
- The "Theme" selector in the UI is a placeholder stub.

## Store Assets
See `docs/windows_store_listing.md` for the copy text.
