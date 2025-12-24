# Technical Debt & Issues

## Critical (Blocking / Safety Risks)
- **Invalid Requirements**: `requirements.txt` includes `sqlite3`, which is a standard library module. This breaks installation.
- **Heavy Dependencies**: `scikit-learn`, `hdbscan`, `umap-learn`, `sentence-transformers` are listed but may not be essential for V1. They bloat the app size significantly.
- **Missing Undo**: The File Organizer needs a robust, transactional Undo system. Currently, it seems to just move files.
- **Data Safety**: No atomic writes or backups for JSON data files. A crash during save could corrupt user data.
- **Hardcoded Paths**: Some logic might assume file paths or structures that aren't cross-platform safe.

## High Impact (UX / Performance / Stability)
- **Monolithic UI Class**: `AdaptiveMainWindow` (700+ lines) mixes UI construction, business logic, and data handling. This makes it hard to test and maintain.
- **Blocking UI**: Long-running operations (like file scanning or "AI Optimization") might block the main thread, freezing the UI. Need to ensure threading/workers are used.
- **"Fake" AI**: The `AISystemOptimizer` and system resource monitoring (CPU/RAM) might be unnecessary feature creep. It confuses the product identity.
- **Hardcoded Strings**: Many UI strings are hardcoded, making localization or text updates difficult.
- **Error Handling**: Many `try...except` blocks might swallow errors or just log them without informing the user properly.

## Nice-to-Have (Refactoring)
- **Dependency Injection**: Managers (`TaskManager`, `ProfileManager`) are instantiated inside `MainWindow`. Injecting them would make testing easier.
- **Model-View-Controller (MVC)**: Separating the data models (Task, Profile) from the View (PyQt widgets) would clean up the code.
- **Test Coverage**: Need to establish a baseline of unit tests for the core logic, especially file operations.
