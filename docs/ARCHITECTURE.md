# Hearth Architecture

_Last updated: 2026-07-02_

Hearth is a local-first, offline-only desktop application built on Electron, React, and SQLite. The architectural philosophy prioritizes absolute data privacy, robustness, and immediate responsiveness. 

## The Electron Boundary
Hearth follows strict Electron security guidelines:
- **Main Process (Node.js)**: Handles all local file system interactions, SQLite persistence (`better-sqlite3`), native OS integration (tray, screen dimming via transparent windows), and heuristics calculations.
- **Preload Script**: Bridges the gap between Main and Renderer. It exposes a strictly typed, context-isolated IPC (Inter-Process Communication) API. No Node integration exists in the renderer.
- **Renderer Process (React)**: The UI layer. It only knows how to ask the Preload bridge for data or send updates.

## State Management

Hearth recently migrated away from scattered local component state to a robust two-tier state architecture to prevent data desynchronization ("gutted features"):

### 1. Global Synchronous State (`Zustand`)
Handled in `src/renderer/state/store.tsx`. 
- **Purpose**: Manages app-wide, highly volatile, or deeply integrated UI state.
- **What it holds**: 
  - Current Route
  - Theming and Presence Settings (Quiet Mode, Focus Guard)
  - Spoons/Energy budget calculations

### 2. Asynchronous Server State (`TanStack Query`)
Handled via `useQuery` and `useMutation` across all screens.
- **Purpose**: Manages data fetching, caching, and optimistic updates for SQLite reads/writes.
- **Why**: SQLite operations over IPC are asynchronous. Relying on local `useState` for lists (Tasks, Medications, Practices) led to stale data and race conditions. TanStack Query guarantees that when a mutation occurs (e.g. marking a task complete), the relevant queries are invalidated and the UI immediately refetches the source of truth.
- **What it holds**: 
  - `Tasks`, `DiaryCards`, `Meds`, `Trends`, `Practices`, `Erp` lists.
  - `CrisisPlan` saving and syncing.

## The Heuristics Engine
The "acting" layer of Hearth lives in `electron/wellness.ts`. This engine runs queries against the SQLite store to calculate patterns:
- Rapid mood drops.
- Consecutive nights of low sleep combined with high anxiety.
- Spoons (energy) remaining vs. scheduled tasks.
This data is exposed to the frontend purely as flags and "Today" briefings. It never diagnoses.

## File System
- **Database**: SQLite WAL (Write-Ahead Logging) mode is used for high concurrency between reads (heuristics) and writes (check-ins).
- **Location**: `userData` directory provided by Electron (e.g., `~/Library/Application Support/Hearth` on macOS).
