"""
Theme management system for Hearth.
Provides condition-aware themes with accessibility support.
"""
from dataclasses import dataclass, field


@dataclass
class Theme:
    """Complete theme definition with behavioral tokens."""
    name: str
    display_name: str
    description: str
    background: str
    text: str
    accent: str
    secondary: str
    success: str
    warning: str
    danger: str
    card_bg: str
    border: str
    hover: str
    disabled: str
    input_bg: str
    tab_active: str
    tab_inactive: str
    scrollbar: str
    shadow: str
    condition_suitability: list = field(default_factory=list)
    # Behavioral tokens -- make themes structurally different, not just color swaps
    layout_density: float = 1.0   # 0.8 = airy/spacious, 1.2 = compact/information-dense
    animation_speed_ms: int = 200
    border_radius_scale: float = 1.0
    chrome_visibility: str = "full"  # "full" | "reduced" | "minimal"

    def to_dict(self) -> dict[str, str]:
        return {
            "background": self.background,
            "text": self.text,
            "accent": self.accent,
            "secondary": self.secondary,
            "success": self.success,
            "warning": self.warning,
            "danger": self.danger,
            "card_bg": self.card_bg,
            "border": self.border,
            "hover": self.hover,
            "disabled": self.disabled,
            "input_bg": self.input_bg,
            "tab_active": self.tab_active,
            "tab_inactive": self.tab_inactive,
            "scrollbar": self.scrollbar,
            "shadow": self.shadow,
            "accent_hover": self.hover,
        }


# === Theme Definitions ===

THEMES: dict[str, Theme] = {
    "ember": Theme(
        name="ember",
        display_name="Ember",
        description="Warm dark default for focused daily use",
        background="#18130F",
        text="#F2E8D9",
        accent="#A8845F",
        secondary="#BCAE9C",
        success="#95B776",
        warning="#E5B16C",
        danger="#C66860",
        card_bg="#221C16",
        border="#3D3128",
        hover="#2F2620",
        disabled="#5F5347",
        input_bg="#2B231C",
        tab_active="#382C24",
        tab_inactive="#221C16",
        scrollbar="#6B5848",
        shadow="rgba(0,0,0,0.32)",
        condition_suitability=["general", "anxiety", "ptsd", "ocd", "adhd"],
        layout_density=1.0,
        animation_speed_ms=180,
        border_radius_scale=0.8,
    ),
    "linen": Theme(
        name="linen",
        display_name="Linen",
        description="Warm light theme with parchment surfaces",
        background="#F7F2EA",
        text="#2D2520",
        accent="#7D5E3F",
        secondary="#6B5E50",
        success="#5F8A47",
        warning="#B8842E",
        danger="#A04A42",
        card_bg="#FFFFFF",
        border="#D4C7B2",
        hover="#EFE8DC",
        disabled="#B5A695",
        input_bg="#FAF6EE",
        tab_active="#E8DFD0",
        tab_inactive="#F7F2EA",
        scrollbar="#A8957B",
        shadow="rgba(45,37,32,0.10)",
        condition_suitability=["general"],
        layout_density=1.0,
        animation_speed_ms=180,
        border_radius_scale=0.8,
    ),
    "quiet": Theme(
        name="quiet",
        display_name="Quiet",
        description="High contrast, reduced chrome accessibility theme",
        background="#000000",
        text="#FFFFFF",
        accent="#FFD400",
        secondary="#D4D4D4",
        success="#00FF00",
        warning="#FFA500",
        danger="#FF4040",
        card_bg="#0A0A0A",
        border="#FFFFFF",
        hover="#222222",
        disabled="#777777",
        input_bg="#0A0A0A",
        tab_active="#111111",
        tab_inactive="#000000",
        scrollbar="#FFFFFF",
        shadow="rgba(255,255,255,0.10)",
        condition_suitability=["general", "adhd", "ptsd", "anxiety"],
        layout_density=1.05,
        animation_speed_ms=0,
        border_radius_scale=0.5,
        chrome_visibility="reduced",
    ),
}

# Color blindness adaptations
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
    """Manages themes and generates stylesheets."""

    def __init__(self):
        self.current_theme_name: str = "ember"
        self.color_blind_mode: str | None = None
        self.font_scale: float = 1.0
        self.reduced_motion: bool = False
        self.dyslexia_font: bool = False

    @property
    def current_theme(self) -> Theme:
        return THEMES.get(self.current_theme_name, THEMES["ember"])

    def set_theme(self, name: str) -> None:
        if name in THEMES:
            self.current_theme_name = name

    def get_theme_names(self) -> list:
        return [(t.name, t.display_name, t.description) for t in THEMES.values()]

    def get_recommended_themes(self, conditions: set) -> list:
        """Get themes recommended for the user's conditions."""
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

        # Apply color blindness overrides
        if self.color_blind_mode and self.color_blind_mode in COLOR_BLIND_OVERRIDES:
            t.update(COLOR_BLIND_OVERRIDES[self.color_blind_mode])

        base_font_size = int(12 * self.font_scale)
        small_font = int(10 * self.font_scale)
        large_font = int(14 * self.font_scale)
        xlarge_font = int(16 * self.font_scale)
        header_font = int(20 * self.font_scale)

        font_family = (
            "OpenDyslexic, Arial, sans-serif"
            if self.dyslexia_font
            else '"Söhne", "SF Pro Text", "Segoe UI", Arial, sans-serif'
        )
        density = theme.layout_density
        radius = int(6 * theme.border_radius_scale)
        selected_text = "#000000" if theme.name == "quiet" else t["text"]
        accent_text = "#18130F" if theme.name != "linen" else "#F7F2EA"

        return f"""
            * {{
                font-family: {font_family};
            }}
            QMainWindow {{
                background-color: {t['background']};
                color: {t['text']};
            }}
            QFrame#appHeader {{
                background-color: {t['card_bg']};
                border-bottom: 1px solid {t['border']};
            }}
            QFrame#sideNav {{
                background-color: {t['card_bg']};
                border-right: 1px solid {t['border']};
            }}
            QLabel#sideNavHeader {{
                color: {t['secondary']};
                font-size: {small_font}px;
                font-weight: 500;
                padding: 2px 4px 10px 4px;
            }}
            QFrame#sideNavDivider {{
                background-color: {t['border']};
                border: none;
                margin: 10px 4px;
            }}
            QFrame#sideNav QPushButton[class="navItem"] {{
                background-color: transparent;
                color: {t['secondary']};
                border: none;
                border-radius: {radius}px;
                padding: {int(8 * density)}px {int(10 * density)}px;
                min-height: 32px;
                text-align: left;
                font-size: {base_font_size}px;
                font-weight: 500;
            }}
            QFrame#sideNav QPushButton[class="navItem"]:hover {{
                background-color: {t['hover']};
                color: {t['text']};
            }}
            QFrame#sideNav QPushButton[class="navItem"]:checked {{
                background-color: {t['tab_active']};
                color: {t['text']};
                border-left: 2px solid {t['accent']};
                padding-left: {int(8 * density)}px;
            }}
            QFrame#sideNav QPushButton[tone="danger"] {{
                color: {t['danger']};
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
                font-weight: 600;
            }}
            QLabel[class="subheader"] {{
                font-size: {xlarge_font}px;
                font-weight: 600;
            }}
            QPushButton {{
                background-color: {t['accent']};
                color: {accent_text};
                border: none;
                padding: {int(7 * density)}px {int(14 * density)}px;
                border-radius: {radius}px;
                font-size: {base_font_size}px;
                font-weight: 500;
                min-height: 34px;
            }}
            QPushButton:hover {{
                background-color: {t['hover']};
                color: {t['text']};
            }}
            QPushButton:pressed {{
                background-color: {t['accent']};
                opacity: 0.8;
            }}
            QPushButton:disabled {{
                background-color: {t['disabled']};
                color: {t['background']};
            }}
            QPushButton[class="danger"] {{
                background-color: {t['danger']};
                color: white;
            }}
            QPushButton#crisisButton {{
                background-color: transparent;
                color: {t['danger']};
                border: 1px solid {t['danger']};
                padding: 6px 12px;
                min-height: 30px;
            }}
            QPushButton#crisisButton:hover {{
                background-color: {t['danger']};
                color: white;
            }}
            QPushButton[class="success"] {{
                background-color: {t['success']};
            }}
            QPushButton[class="secondary"] {{
                background-color: {t['secondary']};
            }}
            QPushButton[class="outline"] {{
                background-color: transparent;
                border: 1px solid {t['border']};
                color: {t['accent']};
            }}
            QComboBox {{
                background-color: {t['input_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                padding: {int(6 * density)}px {int(12 * density)}px;
                border-radius: {radius}px;
                min-height: 28px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {t['input_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                selection-background-color: {t['accent']};
                selection-color: white;
            }}
            QTabWidget::pane {{
                border: none;
                background-color: {t['background']};
            }}
            QTabBar::tab {{
                background-color: {t['tab_inactive']};
                color: {t['secondary']};
                padding: {int(9 * density)}px {int(16 * density)}px;
                border: none;
                border-bottom: 2px solid transparent;
                margin-right: 1px;
                font-size: {base_font_size}px;
                min-height: 30px;
            }}
            QTabBar::tab:selected {{
                background-color: {t['tab_active']};
                color: {selected_text};
                border-bottom: 2px solid {t['accent']};
                font-weight: 500;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {t['hover']};
                color: {t['text']};
            }}
            QListWidget {{
                background-color: {t['card_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: {radius}px;
                padding: 4px;
                outline: none;
            }}
            QListWidget::item {{
                padding: {int(8 * density)}px;
                border-bottom: 1px solid {t['border']};
                border-radius: {max(1, radius - 2)}px;
                margin: 2px;
            }}
            QListWidget::item:selected {{
                background-color: {t['tab_active']};
                color: {t['text']};
            }}
            QListWidget::item:hover:!selected {{
                background-color: {t['hover']};
            }}
            QTextEdit, QPlainTextEdit {{
                background-color: {t['input_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: {radius}px;
                padding: {int(8 * density)}px;
                font-size: {base_font_size}px;
            }}
            QLineEdit {{
                background-color: {t['input_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                padding: {int(8 * density)}px {int(12 * density)}px;
                border-radius: {radius}px;
                min-height: 28px;
                font-size: {base_font_size}px;
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {t['accent']};
            }}
            QProgressBar {{
                border: 1px solid {t['border']};
                border-radius: {radius}px;
                text-align: center;
                min-height: 20px;
                background-color: {t['card_bg']};
                font-size: {small_font}px;
            }}
            QProgressBar::chunk {{
                background-color: {t['accent']};
                border-radius: {max(1, radius - 1)}px;
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {t['border']};
                height: 8px;
                background: {t['card_bg']};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {t['accent']};
                border: none;
                width: 20px;
                height: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }}
            QSlider::sub-page:horizontal {{
                background: {t['accent']};
                border-radius: 4px;
            }}
            QCheckBox {{
                spacing: 8px;
                font-size: {base_font_size}px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {t['border']};
                border-radius: 4px;
                background-color: {t['input_bg']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {t['accent']};
                border-color: {t['accent']};
            }}
            QSpinBox {{
                background-color: {t['input_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 4px 8px;
                min-height: 28px;
            }}
            QFrame[class="card"] {{
                background-color: {t['card_bg']};
                border: 1px solid {t['border']};
                border-radius: {radius}px;
                padding: 16px;
            }}
            QGroupBox {{
                font-size: {large_font}px;
                font-weight: 600;
                border: 1px solid {t['border']};
                border-radius: {radius}px;
                margin-top: 20px;
                padding: 20px 10px 10px 10px;
                background-color: {t['card_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                top: 8px;
                padding: 0;
                background-color: transparent;
                color: {t['text']};
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background: {t['card_bg']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {t['scrollbar']};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background: {t['card_bg']};
                height: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background: {t['scrollbar']};
                border-radius: 5px;
                min-width: 30px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QCalendarWidget {{
                background-color: {t['card_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: {radius}px;
            }}
            QCalendarWidget QWidget {{
                background-color: {t['card_bg']};
                color: {t['text']};
            }}
            QCalendarWidget QToolButton {{
                background-color: transparent;
                color: {t['text']};
                border: none;
                border-radius: {radius}px;
                padding: 4px 8px;
                min-height: 24px;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: {t['hover']};
            }}
            QCalendarWidget QMenu {{
                background-color: {t['card_bg']};
                color: {t['text']};
            }}
            QCalendarWidget QSpinBox {{
                background-color: {t['input_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
            }}
            QCalendarWidget QAbstractItemView {{
                background-color: {t['card_bg']};
                color: {t['text']};
                selection-background-color: {t['accent']};
                selection-color: {accent_text};
                outline: none;
            }}
            QTimeEdit, QDateEdit, QDateTimeEdit {{
                background-color: {t['input_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                border-radius: 6px;
                padding: 4px 8px;
                min-height: 28px;
            }}
            QDialog {{
                background-color: {t['background']};
                color: {t['text']};
            }}
            QDialogButtonBox QPushButton {{
                min-width: 80px;
            }}
            QToolTip {{
                background-color: {t['card_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
                padding: 6px;
                border-radius: 4px;
                font-size: {small_font}px;
            }}
            QStatusBar {{
                background-color: {t['card_bg']};
                color: {t['secondary']};
                font-size: {small_font}px;
                border-top: 1px solid {t['border']};
            }}
            QMenuBar {{
                background-color: {t['card_bg']};
                color: {t['text']};
            }}
            QMenuBar::item:selected {{
                background-color: {t['hover']};
                color: {t['text']};
            }}
            QMenu {{
                background-color: {t['card_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
            }}
            QMenu::item:selected {{
                background-color: {t['hover']};
                color: {t['text']};
            }}
        """

    def get_card_style(self, variant: str = "default") -> str:
        """Get inline style for card widgets."""
        t = self.current_theme.to_dict()
        base = f"background-color: {t['card_bg']}; border: 1px solid {t['border']}; border-radius: 10px; padding: 16px;"
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
