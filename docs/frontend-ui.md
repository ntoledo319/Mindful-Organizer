# Frontend Routes and UI Surfaces

**Purpose:** Document the GUI structure, widgets, and data flow.  
**Intended audience:** Frontend engineers, QA.  
**Confidence:** Confirmed from `src/gui/main_window.py` and widget files.  
**Last updated:** 2026-05-02

## Main Window

**Class:** `AdaptiveMainWindow` (`src/gui/main_window.py`)

- Minimum size: 1200×800
- Default size: 1400×900
- Tabbed interface with `QTabWidget`
- Header bar with profile name and theme selector
- Status bar with profile info and "All data stored locally" message

## Tabs / Widgets

Tabs are added conditionally based on the user's profile. The following table lists all known widgets:

| Widget Name | File | Display Name | Always Shown? | Data Dependencies |
|-------------|------|--------------|---------------|-------------------|
| `dashboard` | `widgets/dashboard.py` | Dashboard | Yes | `task_manager`, `energy_predictor`, `wellness_orchestrator`, `subscription_manager` |
| `task_manager` | `widgets/task_manager_widget.py` | Tasks | Yes | `task_manager`, `nlp_parser` |
| `mood_tracker` | `widgets/mood_tracker.py` | Mood | Yes | `mood_manager`, `profile_manager` |
| `diary_card` | `widgets/diary_card_widget.py` | Diary Card | Yes | `diary_card_manager`, `profile_manager` |
| `journaling` | `widgets/journaling_widget.py` | Journal | Yes | `journal_manager`, `profile_manager` |
| `breathing` | `widgets/breathing_widget.py` | Breathing | Yes | `breathing_manager`, `profile_manager` |
| `erp` | `widgets/erp_widget.py` | ERP | Only if OCD | `ERPTracker` (via parent window) |
| `panic_tracker` | `widgets/panic_tracker_widget.py` | Panic Log | If Panic/Anxiety/PTSD | `PanicTracker` (via parent window) |
| `meditation` | `widgets/meditation_widget.py` | Meditation | Yes | `MeditationManager` (via parent window) |
| `crisis` | `widgets/crisis_widget.py` | Crisis Plan | Yes | `CrisisPlanManager` (via parent window) |
| `sleep` | `widgets/sleep_widget.py` | Sleep | Yes | `SleepTracker` (via parent window) |
| `medication` | `widgets/medication_widget.py` | Medication | Yes | `MedicationTracker` (via parent window) |
| `file_organizer` | `widgets/file_organizer_widget.py` | Files | Yes | `file_organizer`, `profile_manager` |
| `settings` | `widgets/settings_widget.py` | Settings | Yes | `SettingsWidget` (via parent window) |

## Widget Constructor Patterns

There are **two incompatible constructor patterns** in the codebase:

1. **Theme-first pattern** — widgets receive a theme dict as the first argument:
   ```python
   DashboardWidget(theme, task_manager=..., profile_manager=...)
   TaskManagerWidget(theme, task_manager=..., nlp_parser=...)
   ```

2. **Parent-first pattern** — widgets receive the main window as parent:
   ```python
   ERPWidget(self)  # self is AdaptiveMainWindow
   MeditationWidget(self)
   CrisisWidget(self)
   ```

This inconsistency means widgets in group 2 access managers via `parent.xxx_manager`, while widgets in group 1 receive managers explicitly. This is a maintenance risk.

## Data Dependencies and Loading States

- All managers are **lazy-loaded** via properties on `AdaptiveMainWindow`.
- If a manager fails to import (e.g. missing optional dependency), `logger.warning` is emitted and the property returns `None`.
- Widgets in group 1 receive `None` managers gracefully; widgets in group 2 access managers through the parent and may crash if the manager is `None` (not all handle this).
- If a widget fails to import, a **placeholder tab** is shown with "This module is loading..."

## Themes and Accessibility

**Class:** `ThemeManager` (`src/gui/themes.py`)

- Supports multiple named themes (light, dark, calm, focus, high-contrast, etc.)
- Accessibility modes: color-blind, reduced motion, dyslexia font, high contrast
- Font scaling via `font_scale` multiplier
- Stylesheets are generated dynamically and applied to `AdaptiveMainWindow`

## Important State and Error Behavior

- **Onboarding:** If no profile exists, `OnboardingWizard` is shown modally. If cancelled, a default profile is created.
- **Close event:** Settings are saved to `settings.json`. Widgets with `save_state()` are called.
- **Theme change:** Emits `theme_changed` signal; widgets refresh styles.
- **No loading spinners:** Data is loaded synchronously on widget creation. Large datasets could block the UI.
