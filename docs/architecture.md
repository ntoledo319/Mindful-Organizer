# Mindful Organizer Architecture

## Overview
Mindful Organizer is a desktop application built with Python and PyQt6. It combines intelligent file organization with evidence-based mental health tools to help users manage both their digital clutter and their mental well-being.

## Directory Structure
- `src/`: Source code root.
    - `core/`: Core business logic.
        - `file_organizer.py`: Orchestrates file scanning, planning, and execution.
        - `task_manager.py`: Manages user tasks, priorities, and energy levels.
        - `smart_file_system/`: Modules for file indexing, clustering, and analysis.
    - `gui/`: User Interface code (PyQt6).
        - `main_window.py`: The main application window and view logic.
    - `profile/`: User profile management.
        - `mental_health_profile_builder.py`: Handles user conditions (ADHD, Anxiety, etc.) and personalizes the app experience.
        - `clinical_combinations.py`: Logic for combining multiple conditions.
    - `security/`: Encryption and security utilities.
- `tests/`: Unit and integration tests.
- `docs/`: Documentation.

## Key Components

### 1. Adaptive User Interface (`src/gui/`)
The `AdaptiveMainWindow` acts as the central hub. It uses a tabbed interface to switch between:
- **Dashboard**: High-level overview of tasks, mood, and system status.
- **Mood Tracker**: Tools for logging mood, symptoms, and DBT skills.
- **Task Manager**: Task list with priority and energy-level filtering.
- **File Organizer**: Interface for scanning and organizing files.
- **Settings**: Configuration for notifications, themes, etc.

The UI is "adaptive" because it changes its appearance and available features based on the user's `Profile`.

### 2. File Organization Engine (`src/core/`)
The file organization logic follows a "Scan -> Plan -> Apply" pattern:
- **Scan**: `SmartFileSystem` indexes files, extracting metadata and optionally computing semantic embeddings.
- **Plan**: `FileOrganizer` uses strategies (e.g., file type, date, or semantic clusters) to propose a new directory structure.
- **Apply**: The user reviews the plan and confirms. Changes are logged for safety and undo capability.

### 3. Profile & Personalization (`src/profile/`)
The `ProfileManager` maintains a user's profile, which includes:
- **Conditions**: ADHD, Anxiety, Depression, etc.
- **Therapy Types**: CBT, DBT, ACT, ERP.
- **Preferences**: Theme, notification style, organization strictness.

The profile determines:
- Which UI tabs are shown (e.g., "DBT Skills" is only shown if DBT is selected).
- The tone of notifications and tips.
- Default organization strategies (e.g., simpler structures for ADHD).

### 4. Data Persistence
- **User Data**: Stored in `~/.mindful_optimizer/` (or platform equivalent).
- **Format**:
    - `profile.json`: User profile and settings.
    - `tasks.json`: Task list.
    - `mood_log.json`: Mood entries.
    - `transaction_log.json` (Planned): Log of file operations for Undo.

## Mental Health Integration
Features are grounded in evidence-based practices:
- **DBT (Dialectical Behavior Therapy)**: Skills reference, mood tracking with specific skill usage.
- **CBT (Cognitive Behavioral Therapy)**: Thought records (planned), behavioral activation via task completion.
- **ADHD Support**: Gamification, energy-based task planning, clear visual structures.

## Design Patterns
- **Monolithic View**: Currently, `AdaptiveMainWindow` contains much of the view logic. *Refactoring target.*
- **Strategy Pattern**: used in `file_organization` to allow different organization rules.
- **Observer Pattern**: (Implicit via Qt Signals/Slots) for updating UI when data changes.
