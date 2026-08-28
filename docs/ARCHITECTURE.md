# Paulatim Architecture

_Last updated: 2026-07-14_

_Visible-name correction — 2026-08-28: the architecture review date remains
historical. Product wording is now Paulatim; stable `ample.*` storage/API
namespaces and the `HEARTHDB` envelope marker are intentionally unchanged for
upgrade compatibility._

Paulatim is a local-first, offline-only desktop application built on Electron,
React, and SQLite. Its architecture prioritizes a narrow network boundary,
authenticated local persistence, recoverability, and immediate responsiveness.
It does not claim absolute privacy: decrypted data exists in process memory
while the app is open, and user-requested exports are plaintext.

## The Electron Boundary
Paulatim follows strict Electron security guidelines:
- **Main Process (Node.js)**: Handles all local file system interactions,
  encrypted SQLite snapshot persistence (`better-sqlite3`), native OS
  integration (tray and screen dimming via transparent windows), and heuristic
  calculations.
- **Preload Script**: Bridges the gap between Main and Renderer. It exposes a strictly typed, context-isolated IPC (Inter-Process Communication) API. No Node integration exists in the renderer.
- **Renderer Process (React)**: The UI layer. It only knows how to ask the Preload bridge for data or send updates.

## State Management

Paulatim recently migrated away from scattered local component state to a robust two-tier state architecture to prevent data desynchronization ("gutted features"):

### 1. Global Synchronous State (`Zustand`)
Handled in `src/renderer/state/store.tsx`. 
- **Purpose**: Manages app-wide, highly volatile, or deeply integrated UI state.
- **What it holds**: 
  - Current Route
  - Theming and Presence Settings (Quiet Mode, Focus Guard)
  - The user-selected 4–24 daily energy budget and derived remaining capacity

### 2. Asynchronous Server State (`TanStack Query`)
Handled via `useQuery` and `useMutation` across all screens.
- **Purpose**: Manages data fetching, caching, and optimistic updates for SQLite reads/writes.
- **Why**: SQLite operations over IPC are asynchronous. Relying on local `useState` for lists (Tasks, Medications, Practices) led to stale data and race conditions. TanStack Query guarantees that when a mutation occurs (e.g. marking a task complete), the relevant queries are invalidated and the UI immediately refetches the source of truth.
- **What it holds**: 
  - `Tasks`, `DiaryCards`, `Meds`, `Trends`, `Practices`, `Erp` lists.
  - `CrisisPlan` saving and syncing.

## The Heuristics Engine
The "acting" layer of Paulatim lives in `electron/wellness.ts`. This engine runs queries against the SQLite store to calculate patterns:
- Rapid mood drops.
- Consecutive nights of low sleep combined with high anxiety.
- Spoons (energy) remaining vs. scheduled tasks.
This data is exposed to the frontend purely as flags and "Today" briefings. It
never diagnoses or infers the user's energy budget from a diagnosis or check-in.

## Persistence and recovery

- **Runtime database:** SQLite runs in memory with foreign-key enforcement.
- **At-rest format:** Every successful mutation is serialized to a versioned,
  authenticated AES-256-GCM snapshot with a fresh random IV. Atomic replacement
  and one rolling encrypted backup protect the last verified generation.
- **Key protection:** A random 256-bit key is wrapped with Electron
  `safeStorage` (Windows DPAPI, macOS Keychain, or a secure Linux Secret
  Service/KWallet backend). Paulatim fails closed when secure OS-backed key
  storage is unavailable.
- **Legacy migration:** A pre-encryption SQLite database is opened read-only,
  integrity checked, encrypted, and verified. The temporary encrypted migration
  backup and plaintext database/WAL/SHM/journal files are retired only after the
  new primary and rolling backup authenticate.
- **Deletion:** Erase uses a crash-recoverable marker and destroys the protected
  key before best-effort removal of encrypted and legacy remnants.
- **Location:** Files live under Electron's per-user `userData/data` directory.

See `docs/PRIVACY.md` for the user-facing boundary, including memory,
OS-session, export, deletion, snapshot, and backup limits.

## Capability vault

`src/renderer/capabilities.ts` is the navigation contract. The default daily
loop contains Today, Tasks, Check in, Practices, and Rhythm. Crisis plan and
Settings remain utilities. Diary cards, ERP notes, and medication reference are
still typed, renderable, persisted, and tested, but omitted from default
navigation until each receives deliberate opt-in and specialist safety review.
Legacy condition-label metadata also remains in the settings type and export
path for backward compatibility, but the launch UI no longer collects it.
