"""
Theme management system for Mindful Organizer.
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
        }


# === Theme Definitions ===

THEMES: dict[str, Theme] = {
    "light": Theme(
        name="light",
        display_name="Light",
        description="Clean and energizing light theme",
        background="#FFFFFF",
        text="#2C3E50",
        accent="#3498DB",
        secondary="#6C7A89",
        success="#27AE60",
        warning="#F39C12",
        danger="#E74C3C",
        card_bg="#F8F9FA",
        border="#DEE2E6",
        hover="#E8F4FD",
        disabled="#BDC3C7",
        input_bg="#FFFFFF",
        tab_active="#3498DB",
        tab_inactive="#ECF0F1",
        scrollbar="#BDC3C7",
        shadow="rgba(0,0,0,0.1)",
        condition_suitability=["general"],
    ),
    "dark": Theme(
        name="dark",
        display_name="Dark",
        description="Easy on the eyes, reduces eye strain",
        background="#1A1A2E",
        text="#E0E0E0",
        accent="#4A9BD9",
        secondary="#8899AA",
        success="#2ECC71",
        warning="#F1C40F",
        danger="#E74C3C",
        card_bg="#16213E",
        border="#2C3E6B",
        hover="#1F3A5F",
        disabled="#555555",
        input_bg="#0F3460",
        tab_active="#4A9BD9",
        tab_inactive="#16213E",
        scrollbar="#2C3E6B",
        shadow="rgba(0,0,0,0.3)",
        condition_suitability=["general", "anxiety", "ptsd"],
    ),
    "calm": Theme(
        name="calm",
        display_name="Calm",
        description="Soothing colors to reduce anxiety",
        background="#F0F7F4",
        text="#2D4A3E",
        accent="#5B9A8B",
        secondary="#7FB5A0",
        success="#5B9A8B",
        warning="#D4A574",
        danger="#C17C74",
        card_bg="#E8F3EE",
        border="#C5DDD4",
        hover="#D5EAE1",
        disabled="#A8C5B8",
        input_bg="#F5FAF7",
        tab_active="#5B9A8B",
        tab_inactive="#E0EDE7",
        scrollbar="#B5D4C8",
        shadow="rgba(91,154,139,0.1)",
        condition_suitability=["anxiety", "ptsd", "ocd"],
    ),
    "high_contrast": Theme(
        name="high_contrast",
        display_name="High Contrast",
        description="Maximum readability for accessibility",
        background="#000000",
        text="#FFFFFF",
        accent="#FFD700",
        secondary="#00BFFF",
        success="#00FF00",
        warning="#FFA500",
        danger="#FF0000",
        card_bg="#1A1A1A",
        border="#FFFFFF",
        hover="#333333",
        disabled="#666666",
        input_bg="#1A1A1A",
        tab_active="#FFD700",
        tab_inactive="#333333",
        scrollbar="#FFD700",
        shadow="rgba(255,215,0,0.2)",
        condition_suitability=["general", "adhd"],
    ),
    "warm": Theme(
        name="warm",
        display_name="Warm & Uplifting",
        description="Warm tones to combat low mood",
        background="#FFF8F0",
        text="#3D2C2E",
        accent="#E07A5F",
        secondary="#81B29A",
        success="#81B29A",
        warning="#F2CC8F",
        danger="#E07A5F",
        card_bg="#FFF1E6",
        border="#F2CC8F",
        hover="#FFE8D6",
        disabled="#C4A882",
        input_bg="#FFFAF5",
        tab_active="#E07A5F",
        tab_inactive="#FFF1E6",
        scrollbar="#E07A5F",
        shadow="rgba(224,122,95,0.1)",
        condition_suitability=["depression"],
    ),
    "focus": Theme(
        name="focus",
        display_name="Focus Mode",
        description="Minimal distractions for ADHD",
        background="#FAFAFA",
        text="#212121",
        accent="#FF6B35",
        secondary="#4ECDC4",
        success="#4ECDC4",
        warning="#FFE66D",
        danger="#FF6B6B",
        card_bg="#FFFFFF",
        border="#E0E0E0",
        hover="#FFF0E8",
        disabled="#BDBDBD",
        input_bg="#FFFFFF",
        tab_active="#FF6B35",
        tab_inactive="#F5F5F5",
        scrollbar="#FF6B35",
        shadow="rgba(255,107,53,0.1)",
        condition_suitability=["adhd"],
        layout_density=1.2,
        animation_speed_ms=150,
        chrome_visibility="reduced",
    ),
    "gentle": Theme(
        name="gentle",
        display_name="Gentle",
        description="Soft, non-threatening colors for PTSD",
        background="#FAF8F5",
        text="#4A4543",
        accent="#A8A0D6",
        secondary="#B8D4C8",
        success="#B8D4C8",
        warning="#E8D5A3",
        danger="#D4A0A0",
        card_bg="#F5F2EF",
        layout_density=0.9,
        animation_speed_ms=400,
        border_radius_scale=1.2,
        border="#E0DBD5",
        hover="#EEEAE5",
        disabled="#C8C3BD",
        input_bg="#FDFCFA",
        tab_active="#A8A0D6",
        tab_inactive="#F0EDE9",
        scrollbar="#C8C0E0",
        shadow="rgba(168,160,214,0.1)",
        condition_suitability=["ptsd", "anxiety"],
    ),
    "structured": Theme(
        name="structured",
        display_name="Structured",
        description="Clear, organized appearance for OCD",
        background="#F5F5F5",
        text="#333333",
        accent="#5C6BC0",
        secondary="#78909C",
        success="#66BB6A",
        warning="#FFA726",
        danger="#EF5350",
        card_bg="#FFFFFF",
        border="#BDBDBD",
        hover="#E8EAF6",
        disabled="#9E9E9E",
        input_bg="#FFFFFF",
        tab_active="#5C6BC0",
        tab_inactive="#EEEEEE",
        scrollbar="#5C6BC0",
        shadow="rgba(92,107,192,0.1)",
        condition_suitability=["ocd"],
        layout_density=1.0,
        animation_speed_ms=100,
        border_radius_scale=0.5,
        chrome_visibility="full",
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
        self.current_theme_name: str = "light"
        self.color_blind_mode: str | None = None
        self.font_scale: float = 1.0
        self.reduced_motion: bool = False
        self.dyslexia_font: bool = False

    @property
    def current_theme(self) -> Theme:
        return THEMES.get(self.current_theme_name, THEMES["light"])

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

        font_family = "OpenDyslexic, Arial, sans-serif" if self.dyslexia_font else "Segoe UI, Arial, sans-serif"
        density = theme.layout_density
        radius = int(6 * theme.border_radius_scale)
        int(12 * theme.border_radius_scale)

        return f"""
            * {{
                font-family: {font_family};
                font-size: {base_font_size}px;
            }}
            QMainWindow {{
                background-color: {t['background']};
                color: {t['text']};
            }}
            QWidget {{
                background-color: {t['background']};
                color: {t['text']};
            }}
            QLabel {{
                color: {t['text']};
                background-color: transparent;
            }}
            QLabel[class="header"] {{
                font-size: {header_font}px;
                font-weight: bold;
            }}
            QLabel[class="subheader"] {{
                font-size: {xlarge_font}px;
                font-weight: bold;
            }}
            QPushButton {{
                background-color: {t['accent']};
                color: white;
                border: none;
                padding: {int(8 * density)}px {int(16 * density)}px;
                border-radius: {radius}px;
                font-size: {base_font_size}px;
                font-weight: 500;
                min-height: 32px;
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
            }}
            QPushButton[class="success"] {{
                background-color: {t['success']};
            }}
            QPushButton[class="secondary"] {{
                background-color: {t['secondary']};
            }}
            QPushButton[class="outline"] {{
                background-color: transparent;
                border: 2px solid {t['accent']};
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
                border: 1px solid {t['border']};
                background-color: {t['background']};
                border-radius: {radius}px;
            }}
            QTabBar::tab {{
                background-color: {t['tab_inactive']};
                color: {t['text']};
                padding: {int(10 * density)}px {int(20 * density)}px;
                border: 1px solid {t['border']};
                border-bottom: none;
                border-top-left-radius: {radius}px;
                border-top-right-radius: {radius}px;
                margin-right: 2px;
                font-size: {base_font_size}px;
            }}
            QTabBar::tab:selected {{
                background-color: {t['tab_active']};
                color: white;
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {t['hover']};
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
                background-color: {t['accent']};
                color: white;
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
                border: 2px solid {t['accent']};
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
                border-radius: 10px;
                padding: 16px;
            }}
            QGroupBox {{
                font-size: {large_font}px;
                font-weight: bold;
                border: 1px solid {t['border']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 20px;
                background-color: {t['card_bg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                background-color: {t['card_bg']};
                color: {t['accent']};
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
            }}
            QCalendarWidget QAbstractItemView {{
                background-color: {t['card_bg']};
                color: {t['text']};
                selection-background-color: {t['accent']};
                selection-color: white;
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
            }}
            QMenuBar {{
                background-color: {t['card_bg']};
                color: {t['text']};
            }}
            QMenuBar::item:selected {{
                background-color: {t['accent']};
                color: white;
            }}
            QMenu {{
                background-color: {t['card_bg']};
                color: {t['text']};
                border: 1px solid {t['border']};
            }}
            QMenu::item:selected {{
                background-color: {t['accent']};
                color: white;
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
