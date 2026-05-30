# System Overview

**Purpose:** High-level description of what Hearth is, who uses it, and what it does.
**Intended audience:** New engineers, operators, auditors, buyers.
**Confidence:** Mixed — product behavior is confirmed from source; user personas are inferred from feature design.
**Source references:** `src/main.py`, `src/gui/main_window.py`, `src/core/`, `src/profiles/`, `src/wellness/`
**Last updated:** 2026-05-29

## What the Product Is

Hearth is a **single-user, offline-first desktop application** for mental-health-aware productivity. It runs on macOS, Linux, and Windows. User records are stored locally in SQLite, with small JSON files for settings/templates. There is no cloud sync, no telemetry, and no network dependency for core features.

The application adapts its UI and recommendations based on a user-configurable mental health profile (conditions such as ADHD, Anxiety, Depression, OCD, PTSD, Bipolar, etc.).

## Main Actors

| Actor | Role | Evidence |
|-------|------|----------|
| **End user** | The primary actor. Creates tasks, logs mood/sleep/meds, uses therapeutic tools, views reports. | `src/gui/widgets/`, `src/core/task_manager.py` |
| **Application** | Orchestrates modules, manages persistence, enforces single-instance, applies themes. | `src/main.py`, `src/gui/main_window.py` |
| **Wellness orchestrator** | Background intelligence that reads aggregated data and produces insights/crisis signals. | `src/core/wellness_orchestrator.py` |
| **Subscription manager** | Enforces feature gating based on Free/Pro/Premium tier or trial state. | `src/core/subscription_manager.py` |

There is **no multi-user support**, **no server-side API**, and **no administrator role**.

## Core Workflows

### 1. Daily Check-In
1. User opens app → `AdaptiveMainWindow` loads profile and theme.
2. User navigates to **Mood** tab → `MoodTrackerWidget`.
3. User submits mood score → `MoodManager` → `DatabaseManager.insert(TableName.MOOD_ENTRIES, ...)`.
4. `StateBus` emits signal → `DashboardWidget` refreshes.
5. `WellnessOrchestrator.snapshot()` reads latest mood + sleep + meds.
6. If heuristics fire (e.g. low mood + low sleep), a `CrisisSignal` is generated.

### 2. Task Creation & Prioritization
1. User navigates to **Tasks** tab → `TaskManagerWidget`.
2. User adds task (or uses NLP parser for natural language input).
3. `TaskManager.add_task()` persists to SQLite (`tasks` table).
4. `StateBus.emit_task_changed()` notifies dashboard.
5. User sorts by energy or priority; `TaskManager` filters in-memory.

### 3. Crisis Plan Access
1. User navigates to **Crisis Plan** tab → `CrisisWidget`.
2. Widget displays warning signs, coping strategies, and emergency contacts stored in SQLite (`crisis_plans` table).
3. Data is readable without authentication (single-user app).

## System Boundaries

```
┌─────────────────────────────────────────────┐
│          Hearth (desktop)        │
│  ┌─────────┐  ┌─────────┐  ┌─────────────┐ │
│  │   GUI   │  │  Core   │  │   Wellness  │ │
│  │ (PyQt6) │  │Managers │  │   Modules   │ │
│  └────┬────┘  └────┬────┘  └──────┬──────┘ │
│       └─────────────┴──────────────┘        │
│                   │                         │
│            ┌──────┴──────┐                  │
│            │  SQLite DB  │                  │
│            │ + config    │                  │
│            └─────────────┘                  │
└─────────────────────────────────────────────┘
         │ Optional: GitHub API (update check)
         │ Optional: Chart.js CDN (reports)
         │ Optional: MP3 download URLs (meditations)
```

**In-bounds:**
- All code in `src/`
- Local SQLite database (`~/.mindful_organizer/mindful_organizer.db`)
- Local JSON files for templates, custom categories, settings, and license state
- In-app HTML reports (self-contained, CDN-loaded Chart.js)

**Out-of-bounds:**
- Cloud sync servers
- Telemetry pipelines
- Medical devices or diagnostic systems
- Third-party authentication providers

## Glossary

| Term | Meaning |
|------|---------|
| **DBT** | Dialectical Behavior Therapy |
| **Diary Card** | Structured daily tracking form used in DBT |
| **ERP** | Exposure and Response Prevention (OCD therapy) |
| **Spoon theory** | Metaphor for limited energy in chronic illness |
| **SUDS** | Subjective Units of Distress Scale (0–100) |
| **Condition-aware** | UI or logic that changes based on user's declared conditions |

## Confirmed vs Inferred

| Claim | Status | Evidence |
|-------|--------|----------|
| Single-user desktop app | **Confirmed** | `src/main.py` single-instance lock, no auth system |
| Offline-first | **Confirmed** | No network calls in core paths; SQLite plus local config only |
| No telemetry | **Confirmed** | No network logging or analytics SDKs found |
| Target users have ADHD/Anxiety/Depression | **High-confidence inference** | Condition enum, profile builder, feature design |
| Intended for clinical use | **Unclear / false** | Disclaimer says "not a medical device"; crisis plan is self-help |
| Commercial product | **High-confidence inference** | Subscription tiers, license keys, store listing, pricing |
