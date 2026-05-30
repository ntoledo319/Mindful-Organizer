"""
Theme management system for Hearth.
Provides highly polished, distinctive, condition-aware themes with accessibility support.
"""
from dataclasses import dataclass, field


@dataclass
class Theme:
    """Complete theme definition with behavioral tokens for premium UI."""
    name: str
    display_name: str
    description: str
    background: str
    surface: str       # Elevated surface (e.g. cards, modals)
    surface_alt: str   # Alternate surface (e.g. input fields)
    text: str
    text_muted: str
    accent: str
    accent_hover: str
    success: str
    warning: str
    danger: str
    border: str
    divider: str
    hover_bg: str
    disabled_bg: str
    disabled_text: str
    shadow: str
    condition_suitability: list = field(default_factory=list)
    layout_density: float = 1.0   # 0.8 = spacious, 1.2 = compact
    animation_speed_ms: int = 250
    border_radius: int = 12
    chrome_visibility: str = "full"  # "full" | "reduced" | "minimal"

    def to_dict(self) -> dict[str, str]:
        return {
            "background": self.background,
            "surface": self.surface,
            "surface_alt": self.surface_alt,
            "text": self.text,
            "text_muted": self.text_muted,
            "accent": self.accent,
            "accent_hover": self.accent_hover,
            "success": self.success,
            "warning": self.warning,
            "danger": self.danger,
            "border": self.border,
            "divider": self.divider,
            "hover_bg": self.hover_bg,
            "disabled_bg": self.disabled_bg,
            "disabled_text": self.disabled_text,
            "shadow": self.shadow,
            # Compatibility aliases used by older widgets while they migrate
            # to the newer premium token names.
            "secondary": self.text_muted,
            "card_bg": self.surface,
            "hover": self.hover_bg,
            "disabled": self.disabled_bg,
            "input_bg": self.surface_alt,
            "tab_active": self.accent,
            "tab_inactive": self.surface,
            "scrollbar": self.divider,
        }


# === Premium Theme Definitions ===

THEMES: dict[str, Theme] = {
    "onyx": Theme(
        name="onyx",
        display_name="Onyx",
        description="Deep, premium dark mode. Low visual noise.",
        background="#0F0F11",
        surface="#18181A",
        surface_alt="#222225",
        text="#F3F3F4",
        text_muted="#8E8E93",
        accent="#D9A05B",
        accent_hover="#E6B57A",
        success="#5E9A68",
        warning="#D09241",
        danger="#C85250",
        border="#2C2C2E",
        divider="#1E1E20",
        hover_bg="#262629",
        disabled_bg="#2C2C2E",
        disabled_text="#636366",
        shadow="rgba(0, 0, 0, 0.4)",
        condition_suitability=["general", "anxiety", "ptsd", "adhd", "ocd"],
        layout_density=1.0,
        border_radius=12,
    ),
    "alabaster": Theme(
        name="alabaster",
        display_name="Alabaster",
        description="Soft, organic light mode resembling premium paper.",
        background="#FAFAFA",
        surface="#FFFFFF",
        surface_alt="#F2F2F4",
        text="#1A1A1C",
        text_muted="#6E6E73",
        accent="#426B52",
        accent_hover="#507F63",
        success="#488152",
        warning="#C28230",
        danger="#BA4B48",
        border="#E5E5EA",
        divider="#EFEFF4",
        hover_bg="#F4F4F5",
        disabled_bg="#E5E5EA",
        disabled_text="#AEAEB2",
        shadow="rgba(20, 20, 24, 0.06)",
        condition_suitability=["general", "depression"],
        layout_density=1.0,
        border_radius=12,
    ),
    "slate": Theme(
        name="slate",
        display_name="Slate",
        description="Cool, focused dark mode to reduce cognitive load.",
        background="#1C1F24",
        surface="#23272C",
        surface_alt="#2B3036",
        text="#E8EAED",
        text_muted="#8E959E",
        accent="#62A0EA",
        accent_hover="#7AB4F8",
        success="#57A773",
        warning="#F5C065",
        danger="#E05C5C",
        border="#3C424A",
        divider="#2E3339",
        hover_bg="#353A42",
        disabled_bg="#3C424A",
        disabled_text="#737A83",
        shadow="rgba(0, 0, 0, 0.25)",
        condition_suitability=["general", "adhd", "anxiety"],
        layout_density=1.0,
        border_radius=10,
    ),
    "quiet": Theme(
        name="quiet",
        display_name="Quiet",
        description="High contrast, reduced chrome for maximum clarity.",
        background="#000000",
        surface="#0A0A0A",
        surface_alt="#111111",
        text="#FFFFFF",
        text_muted="#AAAAAA",
        accent="#FFD400",
        accent_hover="#FFE24D",
        success="#00FF00",
        warning="#FFA500",
        danger="#FF4040",
        border="#333333",
        divider="#222222",
        hover_bg="#1A1A1A",
        disabled_bg="#333333",
        disabled_text="#777777",
        shadow="rgba(0,0,0,0)",
        condition_suitability=["general", "adhd", "ptsd", "anxiety"],
        layout_density=1.05,
        animation_speed_ms=0,
        border_radius=4,
        chrome_visibility="reduced",
    ),
}

COLOR_BLIND_OVERRIDES = {
    "protanopia": {
        "success": "#0072B2",
        "warning": "#E69F00",
        "danger": "#D55E00",
        "accent": "#56B4E9",
    },
    "deuteranopia": {
        "success": "#0072B2",
        "warning": "#E69F00",
        "danger": "#D55E00",
        "accent": "#56B4E9",
    },
    "tritanopia": {
        "success": "#009E73",
        "warning": "#CC79A7",
        "danger": "#D55E00",
        "accent": "#0072B2",
    },
}


class ThemeManager:
    """Manages themes and generates high-end PyQt stylesheets."""

    def __init__(self):
        self.current_theme_name: str = "onyx"
        self.color_blind_mode: str | None = None
        self.font_scale: float = 1.0
        self.reduced_motion: bool = False
        self.dyslexia_font: bool = False

    @property
    def current_theme(self) -> Theme:
        return THEMES.get(self.current_theme_name, THEMES["onyx"])

    def set_theme(self, name: str) -> None:
        # Migrate legacy names if present
        legacy_map = {
            "ember": "onyx",
            "linen": "alabaster",
            "quiet": "quiet"
        }
        mapped_name = legacy_map.get(name, name)
        if mapped_name in THEMES:
            self.current_theme_name = mapped_name

    def get_theme_names(self) -> list:
        return [(t.name, t.display_name, t.description) for t in THEMES.values()]

    def get_recommended_themes(self, conditions: set) -> list:
        condition_names = {c.value.lower() if hasattr(c, 'value') else str(c).lower() for c in conditions}
        recommended = []
        for theme in THEMES.values():
            score = sum(1 for s in theme.condition_suitability if s in condition_names)
            if score > 0 or "general" in theme.condition_suitability:
                recommended.append((theme.name, theme.display_name, score))
        recommended.sort(key=lambda x: x[2], reverse=True)
        return recommended

    def generate_stylesheet(self) -> str:
        """Generate complete QSS stylesheet for the current theme."""
        theme = self.current_theme
        t = theme.to_dict()

        if self.color_blind_mode and self.color_blind_mode in COLOR_BLIND_OVERRIDES:
            t.update(COLOR_BLIND_OVERRIDES[self.color_blind_mode])

        base_font_size = int(14 * self.font_scale)
        small_font = int(12 * self.font_scale)
        large_font = int(16 * self.font_scale)
        xlarge_font = int(20 * self.font_scale)
        header_font = int(26 * self.font_scale)

        font_family = (
            "OpenDyslexic, Arial, sans-serif"
            if self.dyslexia_font
            else '"SF Pro Text", "Inter", "Segoe UI", "Helvetica Neue", sans-serif'
        )
        density = theme.layout_density
        radius = theme.border_radius
        accent_text = "#FFFFFF" if theme.name != "alabaster" else "#FFFFFF"

        return f"""
            * {{
                font-family: {font_family};
            }}
            QMainWindow {{
                background-color: {t['background']};
                color: {t['text']};
            }}
            QFrame#appHeader {{
                background-color: {t['background']};
                border-bottom: 1px solid {t['divider']};
            }}
            QFrame#sideNav {{
                background-color: {t['surface']};
                border-right: 1px solid {t['divider']};
            }}
            QLabel#sideNavHeader {{
                color: {t['text_muted']};
                font-size: {small_font}px;
                font-weight: 600;
                letter-spacing: 0.5px;
                padding: 4px 6px 12px 6px;
                text-transform: uppercase;
            }}
            QFrame#sideNavDivider {{
                background-color: {t['divider']};
                border: none;
                margin: 16px 8px;
            }}
            QFrame#sideNav QPushButton[class="navItem"] {{
                background-color: transparent;
                color: {t['text_muted']};
                border: none;
                border-radius: {radius - 2}px;
                padding: {int(10 * density)}px {int(14 * density)}px;
                margin: 2px 0;
                min-height: 38px;
                text-align: left;
                font-size: {base_font_size}px;
                font-weight: 500;
            }}
            QFrame#sideNav QPushButton[class="navItem"]:hover {{
                background-color: {t['hover_bg']};
                color: {t['text']};
            }}
            QFrame#sideNav QPushButton[class="navItem"]:checked {{
                background-color: {t['accent']};
                color: {accent_text};
                font-weight: 600;
            }}
            QFrame#sideNav QPushButton[tone="danger"] {{
                color: {t['danger']};
            }}
            QFrame#sideNav QPushButton[tone="danger"]:checked {{
                background-color: {t['danger']};
                color: #FFFFFF;
            }}
            QWidget {{
                background-color: {t['background']};
                color: {t['text']};
                font-size: {base_font_size}px;
            }}
            QLabel {{
                color: {t['text']};
                background-color: transparent;
            }}
            QLabel[class="header"] {{
                font-size: {header_font}px;
                font-weight: 700;
                letter-spacing: -0.5px;
            }}
            QLabel[class="subheader"] {{
                font-size: {xlarge_font}px;
                font-weight: 600;
                letter-spacing: -0.3px;
                color: {t['text_muted']};
            }}
            QPushButton {{
                background-color: {t['surface_alt']};
                color: {t['text']};
                border: 1px solid {t['border']};
                padding: {int(8 * density)}px {int(18 * density)}px;
                border-radius: {radius}px;
                font-size: {base_font_size}px;
                font-weight: 500;
                min-height: 38px;
            }}
            QPushButton:hover {{
                background-color: {t['hover_bg']};
                border-color: {t['text_muted']};
            }}
            QPushButton:pressed {{
                background-color: {t['divider']};
            }}
            QPushButton:disabled {{
                background-color: {t['disabled_bg']};
                color: {t['disabled_text']};
                border-color: transparent;
            }}
            QPushButton[class="accent"] {{
                background-color: {t['accent']};
                color: {accent_text};
                border: none;
            }}
            QPushButton[class="accent"]:hover {{
                background-color: {t['accent_hover']};
            }}
            QPushButton[class="danger"] {{
                background-color: {t['danger']};
                color: white;
                border: none;
            }}
            QPushButton#crisisButton {{
                background-color: transparent;
                color: {t['danger']};
                border: 2px solid {t['danger']};
                font-weight: 600;
                border-radius: {radius}px;
            }}
            QPushButton#crisisButton:hover {{
                background-color: {t['danger']};
                color: white;
            }}
            QComboBox {{
                background-color: {t['surface']};
                color: {t['text']};
                border: 1px solid {t['border']};
                padding: {int(8 * density)}px {int(16 * density)}px;
                border-radius: {radius}px;
                min-height: 36px;
                font-weight: 500;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 32px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {t['surface']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: {radius}px;
                selection-background-color: {t['hover_bg']};
                selection-color: {t['text']};
                padding: 4px;
            }}
            QTabWidget::pane {{
                border: none;
                background-color: {t['background']};
            }}
            QTabBar::tab {{
                background-color: transparent;
                color: {t['text_muted']};
                padding: {int(12 * density)}px {int(20 * density)}px;
                border: none;
                border-bottom: 2px solid transparent;
                font-size: {large_font}px;
                font-weight: 500;
            }}
            QTabBar::tab:selected {{
                color: {t['text']};
                border-bottom: 2px solid {t['accent']};
            }}
            QTabBar::tab:hover:!selected {{
                color: {t['text']};
            }}
            QListWidget {{
                background-color: {t['surface']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: {radius}px;
                padding: 8px;
                outline: none;
            }}
            QListWidget::item {{
                padding: {int(12 * density)}px;
                border-radius: {radius - 2}px;
                margin-bottom: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {t['hover_bg']};
                color: {t['text']};
                font-weight: 500;
            }}
            QListWidget::item:hover:!selected {{
                background-color: {t['surface_alt']};
            }}
            QTextEdit, QPlainTextEdit, QLineEdit {{
                background-color: {t['surface']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: {radius}px;
                padding: {int(10 * density)}px {int(14 * density)}px;
                font-size: {base_font_size}px;
            }}
            QLineEdit {{
                min-height: 38px;
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {t['accent']};
                background-color: {t['surface_alt']};
            }}
            QProgressBar {{
                border: none;
                border-radius: 4px;
                text-align: right;
                min-height: 8px;
                max-height: 8px;
                background-color: {t['divider']};
            }}
            QProgressBar::chunk {{
                background-color: {t['accent']};
                border-radius: 4px;
            }}
            QSlider::groove:horizontal {{
                border: none;
                height: 6px;
                background: {t['divider']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: {t['accent']};
                border: 2px solid {t['surface']};
                width: 24px;
                height: 24px;
                margin: -9px 0;
                border-radius: 12px;
            }}
            QSlider::sub-page:horizontal {{
                background: {t['accent']};
                border-radius: 3px;
            }}
            QCheckBox {{
                spacing: 12px;
                font-size: {base_font_size}px;
                font-weight: 500;
            }}
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border: 2px solid {t['border']};
                border-radius: 6px;
                background-color: {t['surface']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {t['accent']};
                border-color: {t['accent']};
            }}
            QSpinBox {{
                background-color: {t['surface']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: {radius}px;
                padding: 6px 12px;
                min-height: 36px;
            }}
            QFrame[class="card"] {{
                background-color: {t['surface']};
                border: 1px solid {t['border']};
                border-radius: {radius * 1.5}px;
                padding: 24px;
            }}
            QGroupBox {{
                font-size: {large_font}px;
                font-weight: 600;
                border: 1px solid {t['border']};
                border-radius: {radius}px;
                margin-top: 28px;
                padding: 24px 16px 16px 16px;
                background-color: {t['surface']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                top: -12px;
                padding: 0 8px;
                background-color: {t['surface']};
                color: {t['text_muted']};
                font-size: {small_font}px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 14px;
                border-radius: 7px;
                margin: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {t['border']};
                border-radius: 7px;
                min-height: 40px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {t['text_muted']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QCalendarWidget {{
                background-color: {t['surface']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: {radius}px;
            }}
            QCalendarWidget QWidget {{
                background-color: {t['surface']};
            }}
            QCalendarWidget QToolButton {{
                color: {t['text']};
                border: none;
                border-radius: {radius - 2}px;
                padding: 6px;
                min-height: 28px;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: {t['hover_bg']};
            }}
            QCalendarWidget QAbstractItemView {{
                background-color: {t['surface']};
                color: {t['text']};
                selection-background-color: {t['accent']};
                selection-color: {accent_text};
                border-radius: {radius}px;
                outline: none;
            }}
            QDialog {{
                background-color: {t['background']};
            }}
            QToolTip {{
                background-color: {t['surface_alt']};
                color: {t['text']};
                border: 1px solid {t['border']};
                padding: 8px 12px;
                border-radius: 6px;
                font-size: {small_font}px;
            }}
            QStatusBar {{
                background-color: {t['background']};
                color: {t['text_muted']};
                font-size: {small_font}px;
                border-top: 1px solid {t['divider']};
            }}
        """

    def get_card_style(self, variant: str = "default") -> str:
        """Get inline style for card widgets."""
        t = self.current_theme.to_dict()
        base = f"background-color: {t['surface']}; border: 1px solid {t['border']}; border-radius: {self.current_theme.border_radius * 1.5}px; padding: 24px;"
        if variant == "accent":
            base += f" border-left: 4px solid {t['accent']};"
        elif variant == "success":
            base += f" border-left: 4px solid {t['success']};"
        elif variant == "warning":
            base += f" border-left: 4px solid {t['warning']};"
        elif variant == "danger":
            base += f" border-left: 4px solid {t['danger']};"
        return base

    def get_colors(self) -> dict[str, str]:
        """Get current theme colors as a dict."""
        t = self.current_theme.to_dict()
        if self.color_blind_mode and self.color_blind_mode in COLOR_BLIND_OVERRIDES:
            t.update(COLOR_BLIND_OVERRIDES[self.color_blind_mode])
        return t
