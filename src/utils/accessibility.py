"""
Accessibility utilities for Mindful Organizer.

Provides screen reader text, high contrast support, keyboard navigation,
font scaling, colour-blindness modes, reduced motion, focus indicators,
ARIA-like descriptions for PyQt6 widgets, and dyslexia-friendly font support.
"""

import logging
import os
import platform
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

DATA_DIR = Path.home() / ".mindful_optimizer"


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class FontScale(Enum):
    """Predefined font size levels."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"

    @property
    def multiplier(self) -> float:
        return {
            "small": 0.85,
            "medium": 1.0,
            "large": 1.25,
            "extra_large": 1.5,
        }[self.value]

    @property
    def base_point_size(self) -> int:
        """Return the base point size for this scale."""
        return {
            "small": 9,
            "medium": 11,
            "large": 14,
            "extra_large": 17,
        }[self.value]


class ColorBlindnessMode(Enum):
    """Supported colour-vision deficiency simulations / corrections."""
    NONE = "none"
    PROTANOPIA = "protanopia"       # Red-blind
    DEUTERANOPIA = "deuteranopia"   # Green-blind
    TRITANOPIA = "tritanopia"       # Blue-blind

    @property
    def description(self) -> str:
        return {
            "none": "Normal colour vision",
            "protanopia": "Red-blind (protanopia)",
            "deuteranopia": "Green-blind (deuteranopia)",
            "tritanopia": "Blue-blind (tritanopia)",
        }[self.value]


class ContrastLevel(Enum):
    """Contrast levels for the UI."""
    NORMAL = "normal"
    HIGH = "high"
    EXTRA_HIGH = "extra_high"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class AccessibilitySettings:
    """Current accessibility configuration for the application."""
    font_scale: FontScale = FontScale.MEDIUM
    color_blindness_mode: ColorBlindnessMode = ColorBlindnessMode.NONE
    contrast_level: ContrastLevel = ContrastLevel.NORMAL
    reduced_motion: bool = False
    screen_reader_enabled: bool = False
    dyslexia_font: bool = False
    focus_indicators: bool = True
    keyboard_navigation: bool = True
    animation_duration_ms: int = 200

    def to_dict(self) -> Dict[str, Any]:
        return {
            "font_scale": self.font_scale.value,
            "color_blindness_mode": self.color_blindness_mode.value,
            "contrast_level": self.contrast_level.value,
            "reduced_motion": self.reduced_motion,
            "screen_reader_enabled": self.screen_reader_enabled,
            "dyslexia_font": self.dyslexia_font,
            "focus_indicators": self.focus_indicators,
            "keyboard_navigation": self.keyboard_navigation,
            "animation_duration_ms": self.animation_duration_ms,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AccessibilitySettings":
        return cls(
            font_scale=FontScale(data.get("font_scale", "medium")),
            color_blindness_mode=ColorBlindnessMode(
                data.get("color_blindness_mode", "none")
            ),
            contrast_level=ContrastLevel(data.get("contrast_level", "normal")),
            reduced_motion=data.get("reduced_motion", False),
            screen_reader_enabled=data.get("screen_reader_enabled", False),
            dyslexia_font=data.get("dyslexia_font", False),
            focus_indicators=data.get("focus_indicators", True),
            keyboard_navigation=data.get("keyboard_navigation", True),
            animation_duration_ms=data.get("animation_duration_ms", 200),
        )


@dataclass
class ColorPalette:
    """Colour palette adjusted for the current accessibility settings."""
    background: str = "#FFFFFF"
    surface: str = "#F5F5F5"
    primary: str = "#4A90D9"
    primary_variant: str = "#357ABD"
    secondary: str = "#7B68EE"
    text_primary: str = "#212121"
    text_secondary: str = "#757575"
    success: str = "#4CAF50"
    warning: str = "#FF9800"
    error: str = "#F44336"
    border: str = "#E0E0E0"
    focus_ring: str = "#4A90D9"


# ---------------------------------------------------------------------------
# Colour-blindness safe palettes
# ---------------------------------------------------------------------------

_NORMAL_PALETTE = ColorPalette()

_PROTANOPIA_PALETTE = ColorPalette(
    primary="#4A7FD9",
    primary_variant="#3567BD",
    secondary="#6B58DE",
    success="#4682B4",    # Blue instead of green
    warning="#D4A017",    # Gold instead of orange
    error="#D94A4A",
    focus_ring="#4A7FD9",
)

_DEUTERANOPIA_PALETTE = ColorPalette(
    primary="#4A7FD9",
    primary_variant="#3567BD",
    secondary="#6B58DE",
    success="#4682B4",    # Blue instead of green
    warning="#D4A017",
    error="#CC3333",
    focus_ring="#4A7FD9",
)

_TRITANOPIA_PALETTE = ColorPalette(
    primary="#D94A7F",
    primary_variant="#BD3567",
    secondary="#DE6B58",
    success="#4CAF50",
    warning="#D94A4A",   # Red instead of orange-yellow
    error="#D94A4A",
    focus_ring="#D94A7F",
)

_HIGH_CONTRAST_OVERRIDES = {
    "background": "#000000",
    "surface": "#1A1A1A",
    "text_primary": "#FFFFFF",
    "text_secondary": "#E0E0E0",
    "border": "#FFFFFF",
    "focus_ring": "#FFFF00",
}

_EXTRA_HIGH_CONTRAST_OVERRIDES = {
    "background": "#000000",
    "surface": "#000000",
    "text_primary": "#FFFFFF",
    "text_secondary": "#FFFFFF",
    "border": "#FFFFFF",
    "focus_ring": "#FFFF00",
    "primary": "#00BFFF",
    "error": "#FF4444",
    "success": "#44FF44",
    "warning": "#FFFF00",
}


def get_palette(settings: AccessibilitySettings) -> ColorPalette:
    """Return a colour palette appropriate for the given accessibility settings."""
    base = {
        ColorBlindnessMode.NONE: _NORMAL_PALETTE,
        ColorBlindnessMode.PROTANOPIA: _PROTANOPIA_PALETTE,
        ColorBlindnessMode.DEUTERANOPIA: _DEUTERANOPIA_PALETTE,
        ColorBlindnessMode.TRITANOPIA: _TRITANOPIA_PALETTE,
    }.get(settings.color_blindness_mode, _NORMAL_PALETTE)

    # Apply contrast overrides
    palette_dict = {
        "background": base.background,
        "surface": base.surface,
        "primary": base.primary,
        "primary_variant": base.primary_variant,
        "secondary": base.secondary,
        "text_primary": base.text_primary,
        "text_secondary": base.text_secondary,
        "success": base.success,
        "warning": base.warning,
        "error": base.error,
        "border": base.border,
        "focus_ring": base.focus_ring,
    }
    if settings.contrast_level == ContrastLevel.HIGH:
        palette_dict.update(_HIGH_CONTRAST_OVERRIDES)
    elif settings.contrast_level == ContrastLevel.EXTRA_HIGH:
        palette_dict.update(_EXTRA_HIGH_CONTRAST_OVERRIDES)

    return ColorPalette(**palette_dict)


# ---------------------------------------------------------------------------
# Screen reader helpers
# ---------------------------------------------------------------------------

def screen_reader_text(
    widget_type: str,
    label: str,
    value: Optional[str] = None,
    state: Optional[str] = None,
    hint: Optional[str] = None,
) -> str:
    """Generate descriptive text suitable for screen readers.

    Args:
        widget_type: Kind of widget (e.g. "button", "slider", "text field").
        label: The visible label of the widget.
        value: Current value (for sliders, spinboxes, etc.).
        state: Extra state info (e.g. "checked", "disabled").
        hint: Additional usage hint.
    """
    parts = [label]
    if value is not None:
        parts.append(f", value {value}")
    parts.append(f", {widget_type}")
    if state:
        parts.append(f", {state}")
    if hint:
        parts.append(f". {hint}")
    return "".join(parts)


def set_accessible_properties(widget: Any, **props: Any) -> None:
    """Set accessibility properties on a PyQt6 widget.

    Accepted keyword arguments:
        name: Accessible name
        description: Accessible description
        role: QAccessible.Role value
        help_text: What's This help text
        tooltip: Tooltip text
    """
    if props.get("name"):
        widget.setAccessibleName(props["name"])
    if props.get("description"):
        widget.setAccessibleDescription(props["description"])
    if props.get("help_text"):
        widget.setWhatsThis(props["help_text"])
    if props.get("tooltip"):
        widget.setToolTip(props["tooltip"])


def announce_to_screen_reader(widget: Any, message: str) -> None:
    """Post an announcement event so screen readers speak *message*.

    Requires PyQt6.QtWidgets.QAccessible.
    """
    try:
        from PyQt6.QtWidgets import QAccessible  # type: ignore[attr-defined]
        event = QAccessible.Event.NameChanged
        QAccessible.updateAccessibility(
            QAccessible.queryAccessibleInterface(widget), 0, event
        )
    except Exception:
        # Graceful fallback: just log
        logger.debug("Screen reader announcement: %s", message)


# ---------------------------------------------------------------------------
# High contrast detection
# ---------------------------------------------------------------------------

def detect_high_contrast() -> bool:
    """Detect if the OS has a high-contrast theme enabled."""
    sys_name = platform.system().lower()
    if sys_name == "windows":
        try:
            import ctypes
            SPI_GETHIGHCONTRAST = 0x0042
            # HIGHCONTRAST structure
            class HIGHCONTRAST(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_uint),
                    ("dwFlags", ctypes.c_uint),
                    ("lpszDefaultScheme", ctypes.c_wchar_p),
                ]
            hc = HIGHCONTRAST()
            hc.cbSize = ctypes.sizeof(HIGHCONTRAST)
            ctypes.windll.user32.SystemParametersInfoW(  # type: ignore[attr-defined]
                SPI_GETHIGHCONTRAST, hc.cbSize, ctypes.byref(hc), 0,
            )
            return bool(hc.dwFlags & 0x00000001)  # HCF_HIGHCONTRASTON
        except Exception:
            return False
    elif sys_name == "linux":
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.a11y.interface", "high-contrast"],
                capture_output=True, text=True, timeout=5,
            )
            return "true" in result.stdout.lower()
        except Exception:
            return False
    return False


# ---------------------------------------------------------------------------
# Keyboard navigation
# ---------------------------------------------------------------------------

class KeyboardNavigationHelper:
    """Manages tab-order and keyboard navigation for a set of widgets.

    Usage::

        helper = KeyboardNavigationHelper()
        helper.register(widget_a, order=0, group="main")
        helper.register(widget_b, order=1, group="main")
        helper.apply_tab_order()
    """

    def __init__(self) -> None:
        self._widgets: List[Tuple[int, str, Any]] = []  # (order, group, widget)

    def register(self, widget: Any, order: int = 0, group: str = "default") -> None:
        """Register a widget for keyboard navigation."""
        self._widgets.append((order, group, widget))

    def unregister(self, widget: Any) -> None:
        self._widgets = [(o, g, w) for o, g, w in self._widgets if w is not widget]

    def apply_tab_order(self, group: Optional[str] = None) -> None:
        """Set the tab order of registered widgets using QWidget.setTabOrder.

        If *group* is given, only widgets in that group are ordered.
        """
        try:
            from PyQt6.QtWidgets import QWidget
        except ImportError:
            logger.warning("PyQt6 not available; cannot apply tab order")
            return

        filtered = [
            (o, g, w) for o, g, w in self._widgets
            if group is None or g == group
        ]
        filtered.sort(key=lambda x: x[0])

        for i in range(len(filtered) - 1):
            QWidget.setTabOrder(filtered[i][2], filtered[i + 1][2])

    def get_ordered_widgets(self, group: Optional[str] = None) -> List[Any]:
        filtered = [
            (o, g, w) for o, g, w in self._widgets
            if group is None or g == group
        ]
        filtered.sort(key=lambda x: x[0])
        return [w for _, _, w in filtered]

    def groups(self) -> List[str]:
        return sorted({g for _, g, _ in self._widgets})


# ---------------------------------------------------------------------------
# Font scaling
# ---------------------------------------------------------------------------

def build_font_css(
    scale: FontScale,
    dyslexia_friendly: bool = False,
) -> str:
    """Return a CSS/QSS stylesheet fragment for the given font settings."""
    base_size = scale.base_point_size
    family = _get_font_family(dyslexia_friendly)

    return (
        f"* {{ font-family: {family}; font-size: {base_size}pt; }}\n"
        f"QLabel {{ font-size: {base_size}pt; }}\n"
        f"QPushButton {{ font-size: {base_size}pt; padding: {max(4, base_size // 3)}px; }}\n"
        f"QLineEdit, QTextEdit, QPlainTextEdit {{ font-size: {base_size}pt; }}\n"
        f"QMenuBar {{ font-size: {base_size}pt; }}\n"
        f"QMenu {{ font-size: {base_size}pt; }}\n"
        f"QTabBar::tab {{ font-size: {base_size}pt; padding: {max(6, base_size // 2)}px; }}\n"
    )


def apply_font_scale(app: Any, scale: FontScale) -> None:
    """Apply font scaling to a QApplication instance."""
    try:
        from PyQt6.QtGui import QFont
        font = app.font()
        font.setPointSize(scale.base_point_size)
        app.setFont(font)
    except ImportError:
        logger.warning("PyQt6 not available; cannot apply font scale")


def _get_font_family(dyslexia_friendly: bool) -> str:
    if dyslexia_friendly and is_opendyslexic_available():
        return "'OpenDyslexic', sans-serif"
    return "'Segoe UI', 'Helvetica Neue', 'Ubuntu', sans-serif"


def is_opendyslexic_available() -> bool:
    """Check whether the OpenDyslexic font is installed on the system."""
    try:
        from PyQt6.QtGui import QFontDatabase
        families = QFontDatabase.families()
        return any("opendyslexic" in f.lower() for f in families)
    except ImportError:
        pass

    # Fallback: look for font files
    search_dirs = [
        Path.home() / ".fonts",
        Path.home() / ".local" / "share" / "fonts",
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
    ]
    sys_name = platform.system().lower()
    if sys_name == "windows":
        windir = os.environ.get("WINDIR", r"C:\Windows")
        search_dirs.append(Path(windir) / "Fonts")
    elif sys_name == "darwin":
        search_dirs.extend([
            Path.home() / "Library" / "Fonts",
            Path("/Library/Fonts"),
        ])

    for d in search_dirs:
        if d.exists():
            for f in d.iterdir():
                if "opendyslexic" in f.name.lower():
                    return True
    return False


# ---------------------------------------------------------------------------
# Reduced motion
# ---------------------------------------------------------------------------

def detect_reduced_motion() -> bool:
    """Detect if the OS has a 'reduce motion' preference enabled."""
    sys_name = platform.system().lower()
    if sys_name == "darwin":
        try:
            result = subprocess.run(
                ["defaults", "read", "com.apple.universalaccess", "reduceMotion"],
                capture_output=True, text=True, timeout=5,
            )
            return result.stdout.strip() == "1"
        except Exception:
            return False
    elif sys_name == "linux":
        try:
            result = subprocess.run(
                ["gsettings", "get", "org.gnome.desktop.interface", "enable-animations"],
                capture_output=True, text=True, timeout=5,
            )
            return "false" in result.stdout.lower()
        except Exception:
            return False
    elif sys_name == "windows":
        try:
            import ctypes
            SPI_GETCLIENTAREAANIMATION = 0x1042
            animation = ctypes.c_bool()
            ctypes.windll.user32.SystemParametersInfoW(  # type: ignore[attr-defined]
                SPI_GETCLIENTAREAANIMATION, 0, ctypes.byref(animation), 0,
            )
            return not animation.value
        except Exception:
            return False
    return False


def effective_animation_duration(
    settings: AccessibilitySettings, base_ms: int = 200,
) -> int:
    """Return the animation duration to use, respecting reduced-motion settings."""
    if settings.reduced_motion:
        return 0
    return settings.animation_duration_ms or base_ms


# ---------------------------------------------------------------------------
# Focus indicator
# ---------------------------------------------------------------------------

_FOCUS_STYLESHEET = """
*:focus {{
    outline: 2px solid {color};
    outline-offset: 2px;
}}
QPushButton:focus, QToolButton:focus {{
    border: 2px solid {color};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border: 2px solid {color};
}}
QComboBox:focus {{
    border: 2px solid {color};
}}
"""


def focus_indicator_stylesheet(
    settings: AccessibilitySettings,
    palette: Optional[ColorPalette] = None,
) -> str:
    """Generate a QSS stylesheet that adds visible focus indicators."""
    if not settings.focus_indicators:
        return ""
    if palette is None:
        palette = get_palette(settings)
    return _FOCUS_STYLESHEET.format(color=palette.focus_ring)


# ---------------------------------------------------------------------------
# Full stylesheet builder
# ---------------------------------------------------------------------------

def build_accessibility_stylesheet(settings: AccessibilitySettings) -> str:
    """Combine all accessibility-related styles into one QSS string."""
    palette = get_palette(settings)
    parts: List[str] = []

    # Font
    parts.append(build_font_css(settings.font_scale, settings.dyslexia_font))

    # Focus indicators
    parts.append(focus_indicator_stylesheet(settings, palette))

    # Contrast colours
    parts.append(f"""
QWidget {{
    background-color: {palette.background};
    color: {palette.text_primary};
}}
QLabel {{
    color: {palette.text_primary};
}}
QPushButton {{
    background-color: {palette.primary};
    color: #FFFFFF;
    border: 1px solid {palette.border};
    border-radius: 4px;
}}
QPushButton:hover {{
    background-color: {palette.primary_variant};
}}
QLineEdit, QTextEdit, QPlainTextEdit {{
    background-color: {palette.surface};
    color: {palette.text_primary};
    border: 1px solid {palette.border};
}}
""")

    # Reduced motion: disable transitions
    if settings.reduced_motion:
        parts.append("* { transition: none; animation: none; }\n")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# AccessibilityManager (high-level coordinator)
# ---------------------------------------------------------------------------

class AccessibilityManager:
    """Central coordinator for all accessibility features.

    Usage::

        mgr = AccessibilityManager()
        mgr.settings.font_scale = FontScale.LARGE
        mgr.settings.color_blindness_mode = ColorBlindnessMode.DEUTERANOPIA
        mgr.apply(app)        # apply to QApplication
        mgr.save(db)          # persist to database
    """

    def __init__(self, settings: Optional[AccessibilitySettings] = None) -> None:
        self.settings = settings or AccessibilitySettings()
        self._nav_helper = KeyboardNavigationHelper()

    @property
    def nav(self) -> KeyboardNavigationHelper:
        return self._nav_helper

    def auto_detect(self) -> None:
        """Auto-detect OS accessibility preferences and update settings."""
        if detect_high_contrast():
            self.settings.contrast_level = ContrastLevel.HIGH
        if detect_reduced_motion():
            self.settings.reduced_motion = True
            self.settings.animation_duration_ms = 0
        if is_opendyslexic_available():
            logger.info("OpenDyslexic font detected on system")

    def apply(self, app: Any) -> None:
        """Apply current accessibility settings to a QApplication."""
        stylesheet = build_accessibility_stylesheet(self.settings)
        app.setStyleSheet(stylesheet)
        apply_font_scale(app, self.settings.font_scale)
        logger.info(
            "Applied accessibility settings: scale=%s, contrast=%s, cb=%s",
            self.settings.font_scale.value,
            self.settings.contrast_level.value,
            self.settings.color_blindness_mode.value,
        )

    def save(self, db: Any) -> None:
        """Persist current settings to the database."""
        import json
        db.set_setting(
            "accessibility",
            json.dumps(self.settings.to_dict()),
            category="accessibility",
        )

    def load(self, db: Any) -> None:
        """Load settings from the database."""
        import json
        raw = db.get_setting("accessibility")
        if raw:
            try:
                data = json.loads(raw)
                self.settings = AccessibilitySettings.from_dict(data)
            except (json.JSONDecodeError, KeyError) as exc:
                logger.warning("Failed to load accessibility settings: %s", exc)

    def get_palette(self) -> ColorPalette:
        return get_palette(self.settings)

    def get_stylesheet(self) -> str:
        return build_accessibility_stylesheet(self.settings)
