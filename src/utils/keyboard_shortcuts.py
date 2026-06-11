"""
Keyboard shortcut management for Mindful Organizer.

Provides customizable, platform-aware shortcuts with conflict detection,
context-aware bindings, an overlay display, and persistent configuration.
"""

import contextlib
import json
import logging
import platform
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from core.paths import get_data_dir

logger = logging.getLogger(__name__)

DATA_DIR = get_data_dir(create=False)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_IS_MACOS = platform.system().lower() == "darwin"

# Qt modifier key names differ on macOS (Cmd) vs others (Ctrl)
_PRIMARY_MOD = "Cmd" if _IS_MACOS else "Ctrl"


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ShortcutContext(Enum):
    """Contexts in which shortcuts are active."""

    GLOBAL = "global"
    TASKS = "tasks"
    MOOD = "mood"
    JOURNAL = "journal"
    BREATHING = "breathing"
    SLEEP = "sleep"
    MEDICATION = "medication"
    SETTINGS = "settings"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class ShortcutAction:
    """Definition of a single keyboard shortcut."""

    action_id: str
    label: str
    description: str
    default_key: str  # e.g. "Ctrl+N"
    current_key: str | None = None  # user-customised key
    context: ShortcutContext = ShortcutContext.GLOBAL
    enabled: bool = True
    callback: Callable[[], None] | None = None

    @property
    def effective_key(self) -> str:
        """Return the active key sequence (user-set or default)."""
        return self.current_key if self.current_key else self.default_key

    @property
    def display_key(self) -> str:
        """Platform-aware display string (Cmd on macOS, Ctrl elsewhere)."""
        key = self.effective_key
        if _IS_MACOS:
            return key.replace("Ctrl+", "Cmd+")
        return key

    def reset(self) -> None:
        """Reset to default key binding."""
        self.current_key = None


@dataclass
class ShortcutConflict:
    """Describes a conflict between two shortcut actions."""

    key: str
    action_a: str
    action_b: str
    context: ShortcutContext

    def __str__(self) -> str:
        return (
            f"Key '{self.key}' is bound to both '{self.action_a}' and "
            f"'{self.action_b}' in context '{self.context.value}'."
        )


# ---------------------------------------------------------------------------
# Default shortcuts
# ---------------------------------------------------------------------------

_DEFAULT_SHORTCUTS: list[ShortcutAction] = [
    ShortcutAction(
        action_id="new_task",
        label="New Task",
        description="Create a new task",
        default_key="Ctrl+N",
        context=ShortcutContext.GLOBAL,
    ),
    ShortcutAction(
        action_id="mood_entry",
        label="Mood Entry",
        description="Log a new mood entry",
        default_key="Ctrl+M",
        context=ShortcutContext.GLOBAL,
    ),
    ShortcutAction(
        action_id="breathing_exercise",
        label="Breathing Exercise",
        description="Start a guided breathing exercise",
        default_key="Ctrl+B",
        context=ShortcutContext.GLOBAL,
    ),
    ShortcutAction(
        action_id="global_search",
        label="Search",
        description="Open global search",
        default_key="Ctrl+F",
        context=ShortcutContext.GLOBAL,
    ),
    ShortcutAction(
        action_id="journal_entry",
        label="Journal Entry",
        description="Open journal for a new entry",
        default_key="Ctrl+J",
        context=ShortcutContext.GLOBAL,
    ),
    ShortcutAction(
        action_id="show_shortcuts",
        label="Show Shortcuts",
        description="Display all keyboard shortcuts",
        default_key="Ctrl+/",
        context=ShortcutContext.GLOBAL,
    ),
    ShortcutAction(
        action_id="focus_session",
        label="Focus Session",
        description="Open the Focus Sessions tab",
        default_key="Ctrl+Shift+F",
        context=ShortcutContext.GLOBAL,
    ),
    ShortcutAction(
        action_id="help",
        label="Help",
        description="Open help documentation",
        default_key="F1",
        context=ShortcutContext.GLOBAL,
    ),
    ShortcutAction(
        action_id="save_export",
        label="Save / Export",
        description="Save current view or export data",
        default_key="Ctrl+S",
        context=ShortcutContext.GLOBAL,
    ),
    ShortcutAction(
        action_id="undo",
        label="Undo",
        description="Undo the last action",
        default_key="Ctrl+Z",
        context=ShortcutContext.GLOBAL,
    ),
    ShortcutAction(
        action_id="redo",
        label="Redo",
        description="Redo the last undone action",
        default_key="Ctrl+Shift+Z",
        context=ShortcutContext.GLOBAL,
    ),
    # ----- Context-specific shortcuts -----
    ShortcutAction(
        action_id="task_complete",
        label="Complete Task",
        description="Mark selected task as complete",
        default_key="Ctrl+D",
        context=ShortcutContext.TASKS,
    ),
    ShortcutAction(
        action_id="task_delete",
        label="Delete Task",
        description="Delete selected task",
        default_key="Delete",
        context=ShortcutContext.TASKS,
    ),
    ShortcutAction(
        action_id="mood_quick_rate",
        label="Quick Rate",
        description="Open quick mood rating popup",
        default_key="Ctrl+R",
        context=ShortcutContext.MOOD,
    ),
    ShortcutAction(
        action_id="journal_save",
        label="Save Journal",
        description="Save the current journal entry",
        default_key="Ctrl+S",
        context=ShortcutContext.JOURNAL,
    ),
    ShortcutAction(
        action_id="breathing_pause",
        label="Pause / Resume",
        description="Pause or resume the breathing exercise",
        default_key="Space",
        context=ShortcutContext.BREATHING,
    ),
    ShortcutAction(
        action_id="breathing_stop",
        label="Stop Exercise",
        description="Stop the breathing exercise",
        default_key="Escape",
        context=ShortcutContext.BREATHING,
    ),
]


# ---------------------------------------------------------------------------
# ShortcutManager
# ---------------------------------------------------------------------------


class ShortcutManager:
    """Manages keyboard shortcuts with customisation, conflict detection,
    and context awareness.

    Usage::

        sm = ShortcutManager()
        sm.set_callback("new_task", my_new_task_handler)
        sm.remap("mood_entry", "Ctrl+Shift+M")

        # Bind to PyQt6 QShortcut objects
        sm.bind_to_widget(main_window)

        # Save / load
        sm.save(db)
        sm.load(db)
    """

    def __init__(self) -> None:
        self._actions: dict[str, ShortcutAction] = {}
        self._qt_shortcuts: list[Any] = []  # QShortcut references
        self._active_context: ShortcutContext = ShortcutContext.GLOBAL

        # Populate defaults
        for shortcut in _DEFAULT_SHORTCUTS:
            self._actions[shortcut.action_id] = ShortcutAction(
                action_id=shortcut.action_id,
                label=shortcut.label,
                description=shortcut.description,
                default_key=shortcut.default_key,
                current_key=shortcut.current_key,
                context=shortcut.context,
                enabled=shortcut.enabled,
            )

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------

    def get_action(self, action_id: str) -> ShortcutAction | None:
        return self._actions.get(action_id)

    def get_all_actions(self) -> list[ShortcutAction]:
        return list(self._actions.values())

    def get_actions_for_context(
        self,
        context: ShortcutContext,
    ) -> list[ShortcutAction]:
        """Return shortcuts active in the given context.

        Always includes ``GLOBAL`` shortcuts.
        """
        return [
            a
            for a in self._actions.values()
            if a.context in (ShortcutContext.GLOBAL, context) and a.enabled
        ]

    @property
    def active_context(self) -> ShortcutContext:
        return self._active_context

    @active_context.setter
    def active_context(self, ctx: ShortcutContext) -> None:
        self._active_context = ctx
        logger.debug("Active shortcut context: %s", ctx.value)

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def set_callback(
        self,
        action_id: str,
        callback: Callable[[], None],
    ) -> None:
        """Bind a callback function to an action."""
        if action_id in self._actions:
            self._actions[action_id].callback = callback
        else:
            logger.warning("Unknown action_id '%s'; callback not set", action_id)

    def trigger(self, action_id: str) -> bool:
        """Manually trigger an action's callback. Returns True if fired."""
        action = self._actions.get(action_id)
        if action and action.enabled and action.callback:
            try:
                action.callback()
                return True
            except Exception:  # noqa: BLE001
                logger.exception("Error executing shortcut '%s'", action_id)
        return False

    # ------------------------------------------------------------------
    # Remapping
    # ------------------------------------------------------------------

    def remap(self, action_id: str, new_key: str) -> list[ShortcutConflict]:
        """Change the key binding for an action.

        Returns a list of conflicts (empty if none).
        """
        action = self._actions.get(action_id)
        if action is None:
            raise KeyError(f"Unknown action: {action_id}")

        # Check for conflicts before applying
        conflicts = self._find_conflicts_for(new_key, action.context, exclude=action_id)
        action.current_key = new_key
        logger.info("Remapped '%s' to '%s'", action_id, new_key)
        return conflicts

    def reset_action(self, action_id: str) -> None:
        """Reset a single action to its default key."""
        action = self._actions.get(action_id)
        if action:
            action.reset()

    def reset_all(self) -> None:
        """Reset all actions to default keys."""
        for action in self._actions.values():
            action.reset()

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def detect_conflicts(self) -> list[ShortcutConflict]:
        """Scan all shortcuts and return any conflicts."""
        conflicts: list[ShortcutConflict] = []
        # Group by (effective_key, context)
        seen: dict[tuple[str, ShortcutContext], str] = {}
        for action in self._actions.values():
            if not action.enabled:
                continue
            key = action.effective_key.lower()
            for ctx in (action.context, ShortcutContext.GLOBAL):
                pair = (key, ctx)
                if pair in seen and seen[pair] != action.action_id:
                    # GLOBAL overlaps if contexts differ
                    if ctx == ShortcutContext.GLOBAL or action.context == ShortcutContext.GLOBAL:
                        conflicts.append(
                            ShortcutConflict(
                                key=action.effective_key,
                                action_a=seen[pair],
                                action_b=action.action_id,
                                context=ctx,
                            )
                        )
                else:
                    seen[pair] = action.action_id
        return conflicts

    def _find_conflicts_for(
        self,
        key: str,
        context: ShortcutContext,
        exclude: str = "",
    ) -> list[ShortcutConflict]:
        conflicts: list[ShortcutConflict] = []
        key_lower = key.lower()
        for action in self._actions.values():
            if action.action_id == exclude or not action.enabled:
                continue
            if action.effective_key.lower() != key_lower:
                continue
            # Same context or one is global
            if (
                action.context == context
                or action.context == ShortcutContext.GLOBAL
                or context == ShortcutContext.GLOBAL
            ):
                conflicts.append(
                    ShortcutConflict(
                        key=key,
                        action_a=action.action_id,
                        action_b=exclude,
                        context=context,
                    )
                )
        return conflicts

    # ------------------------------------------------------------------
    # Register custom action
    # ------------------------------------------------------------------

    def register(
        self,
        action_id: str,
        label: str,
        key: str,
        description: str = "",
        context: ShortcutContext = ShortcutContext.GLOBAL,
        callback: Callable[[], None] | None = None,
    ) -> list[ShortcutConflict]:
        """Register a new shortcut action. Returns any conflicts."""
        conflicts = self._find_conflicts_for(key, context, exclude=action_id)
        self._actions[action_id] = ShortcutAction(
            action_id=action_id,
            label=label,
            description=description,
            default_key=key,
            context=context,
            callback=callback,
        )
        return conflicts

    def unregister(self, action_id: str) -> None:
        self._actions.pop(action_id, None)

    # ------------------------------------------------------------------
    # PyQt6 integration
    # ------------------------------------------------------------------

    def bind_to_widget(self, widget: Any, context: ShortcutContext | None = None) -> None:
        """Create QShortcut objects on *widget* for matching actions.

        If *context* is None, binds all enabled actions.
        """
        try:
            from PyQt6.QtGui import QKeySequence, QShortcut
        except ImportError:
            logger.warning("PyQt6 not available; shortcuts not bound")
            return

        actions = (
            self.get_actions_for_context(context)
            if context
            else [a for a in self._actions.values() if a.enabled]
        )

        for action in actions:
            key_seq = self._to_qt_key(action.effective_key)
            shortcut = QShortcut(QKeySequence(key_seq), widget)
            if action.callback:
                shortcut.activated.connect(action.callback)
            self._qt_shortcuts.append(shortcut)

    def unbind_all(self) -> None:
        """Remove all QShortcut bindings."""
        for qs in self._qt_shortcuts:
            with contextlib.suppress(Exception):
                qs.setEnabled(False)
                qs.deleteLater()
        self._qt_shortcuts.clear()

    @staticmethod
    def _to_qt_key(key: str) -> str:
        """Convert our shortcut notation to Qt key sequence string.

        On macOS, replace Ctrl with Meta (Qt maps Meta to Cmd).
        """
        if _IS_MACOS:
            return key.replace("Ctrl+", "Meta+")
        return key

    # ------------------------------------------------------------------
    # Overlay (text representation)
    # ------------------------------------------------------------------

    def overlay_text(self, context: ShortcutContext | None = None) -> str:
        """Generate a human-readable summary of all shortcuts.

        Suitable for display in an overlay or help dialog.
        """
        lines: list[str] = []
        lines.append("Keyboard Shortcuts")
        lines.append("=" * 40)

        contexts_to_show: list[ShortcutContext]
        contexts_to_show = [ShortcutContext.GLOBAL, context] if context else list(ShortcutContext)

        for ctx in contexts_to_show:
            actions = [a for a in self._actions.values() if a.context == ctx and a.enabled]
            if not actions:
                continue
            lines.append("")
            lines.append(f"--- {ctx.value.title()} ---")
            for action in sorted(actions, key=lambda a: a.label):
                lines.append(f"  {action.display_key:<20s} {action.label}")
                if action.description:
                    lines.append(f"  {'':20s} {action.description}")
            lines.append("")

        return "\n".join(lines)

    def overlay_data(
        self,
        context: ShortcutContext | None = None,
    ) -> list[dict[str, str]]:
        """Return structured data for building a shortcuts overlay UI."""
        contexts_to_show: list[ShortcutContext]
        contexts_to_show = [ShortcutContext.GLOBAL, context] if context else list(ShortcutContext)

        data: list[dict[str, str]] = []
        for ctx in contexts_to_show:
            for action in self._actions.values():
                if action.context == ctx and action.enabled:
                    data.append(
                        {
                            "action_id": action.action_id,
                            "label": action.label,
                            "key": action.display_key,
                            "description": action.description,
                            "context": ctx.value,
                        }
                    )
        return data

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, db: Any) -> None:
        """Save current shortcut configuration to the database."""
        config: dict[str, dict[str, Any]] = {}
        for action in self._actions.values():
            if action.current_key is not None or not action.enabled:
                config[action.action_id] = {
                    "current_key": action.current_key,
                    "enabled": action.enabled,
                }
        db.set_setting(
            "keyboard_shortcuts",
            json.dumps(config),
            category="shortcuts",
        )
        logger.info("Saved %d custom shortcut bindings", len(config))

    def load(self, db: Any) -> None:
        """Load shortcut configuration from the database."""
        raw = db.get_setting("keyboard_shortcuts")
        if not raw:
            return
        try:
            config = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Invalid shortcut config in database; using defaults")
            return

        for action_id, data in config.items():
            action = self._actions.get(action_id)
            if action is None:
                continue
            if "current_key" in data:
                action.current_key = data["current_key"]
            if "enabled" in data:
                action.enabled = data["enabled"]

        logger.info("Loaded shortcut config; %d overrides applied", len(config))

    def save_to_file(self, path: Path | None = None) -> Path:
        """Export shortcut configuration to a JSON file."""
        if path is None:
            path = DATA_DIR / "shortcuts.json"
        path.parent.mkdir(parents=True, exist_ok=True)

        config: dict[str, dict[str, Any]] = {}
        for action in self._actions.values():
            config[action.action_id] = {
                "label": action.label,
                "default_key": action.default_key,
                "current_key": action.current_key,
                "context": action.context.value,
                "enabled": action.enabled,
            }
        path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        logger.info("Shortcuts exported to %s", path)
        return path

    def load_from_file(self, path: Path) -> None:
        """Import shortcut configuration from a JSON file."""
        if not path.exists():
            raise FileNotFoundError(f"Shortcut config not found: {path}")
        config = json.loads(path.read_text(encoding="utf-8"))
        for action_id, data in config.items():
            action = self._actions.get(action_id)
            if action is None:
                if data.get("label"):
                    # Register new action from file
                    self._actions[action_id] = ShortcutAction(
                        action_id=action_id,
                        label=data.get("label", action_id),
                        description="",
                        default_key=data.get("default_key", ""),
                        current_key=data.get("current_key"),
                        context=ShortcutContext(data.get("context", "global")),
                        enabled=data.get("enabled", True),
                    )
                continue
            if "current_key" in data:
                action.current_key = data["current_key"]
            if "enabled" in data:
                action.enabled = data["enabled"]

        logger.info("Loaded shortcuts from %s", path)
