"""
Reusable UI components for Mindful Organizer.

All widgets in this package are theme-aware and accessibility-friendly.
They eliminate the copy-pasted card / label / button helpers that were
previously duplicated across 10+ widget modules.
"""

from gui.components.buttons import AccentButton, DangerButton, GhostButton
from gui.components.card import CardFrame
from gui.components.containers import ScrollContainer
from gui.components.progress import ThemedProgressBar
from gui.components.typography import BodyLabel, Caption, SectionTitle
from gui.components.upsell_dialog import UpsellDialog

__all__ = [
    "CardFrame",
    "SectionTitle",
    "BodyLabel",
    "Caption",
    "AccentButton",
    "DangerButton",
    "GhostButton",
    "ScrollContainer",
    "ThemedProgressBar",
    "UpsellDialog",
]
