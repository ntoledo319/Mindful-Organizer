# Mindful Organizer - Windows Store V1 Scope

## Core Goal
A polished, safe, and "calm" desktop application that helps users organize their files and their day, personalized to their mental health needs.

## A. Core Smart File Organizer (MUST HAVE)
- **Scan & Index**: Fast scanning of a user-selected directory.
- **Organization Plan**: Generate a readable plan *before* moving anything.
    - Group by: Date (Year/Month), File Type (Images, Docs), or Project.
- **Safe Execution**:
    - **Dry Run** by default.
    - **Transaction Log**: Record every move.
    - **Undo**: One-click restore of the last organizing session.
- **Backup**: Optional copy to a backup folder before reorganization.

## B. Mental Health & Productivity (MUST HAVE)
- **Profile System**:
    - Intake questionnaire (Conditions: ADHD, Anxiety, etc.).
    - Adapts UI (Density, Gamification level).
- **Task Manager**:
    - Simple list with Priority and "Energy Required" tags.
    - Daily Top 3 focus.
- **Mood Tracker**:
    - 1-5 Scale.
    - Tags for Symptoms and Skills used (DBT/CBT).
    - Basic history view (Calendar/List).
- **Resources**:
    - Simple library of DBT/CBT skill cards (text-based).

## C. Smart / Advanced Features (SHOULD HAVE - Toggleable)
- **Semantic Search**: Find files by meaning (using `sentence-transformers` if feasible, otherwise standard keyword search).
- **Clustering**: Group files by topic (using `hdbscan` / `sklearn`). *Note: Make this an optional download or disable if it bloats the installer too much.*

## D. Non-Goals (DEPRIORITIZE / REMOVE for V1)
- **System Optimizer**: CPU/RAM/Battery monitoring and "cleaning". This is off-topic and competes with system utilities.
- **Complex AI Agents**: "AI Optimization" that doesn't do anything concrete.
- **External Accounts**: No cloud sync or login required. Local data only.
- **Heavy ML by default**: If `pytorch`/`sklearn` make the download >500MB, we default to heuristic-based organization (extension, date).

## Technical Requirements for Store
- **Single Executable/Installer**: using PyInstaller.
- **Signed Code**: (Simulated for this task).
- **Crash Reporting**: Local log file.
- **Privacy Policy**: "Data stays on your device."
