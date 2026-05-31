"""
Automation Widget — System automation settings and controls.

Tier-aware display:
- FREE: View default rules, see suggestions, upsell to PRO
- PRO: Toggle execution mode, enable/disable rules, focus mode, display adaptation
- PREMIUM: Custom rules, multiple profiles, scheduled blocks, analytics
"""
from __future__ import annotations

import logging
from datetime import time

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.automation_config import ExecutionMode, ScheduledFocusBlock
from core.automation_rules import ActionType, AutomationAction, AutomationRule, TriggerType
from core.subscription_manager import SubscriptionManager
from core.system_automation import SystemAutomationEngine

logger = logging.getLogger(__name__)


class AutomationWidget(QWidget):
    """Widget for managing system automation settings."""

    def __init__(
        self,
        theme: dict,
        automation_engine: SystemAutomationEngine,
        subscription_manager: SubscriptionManager,
    ) -> None:
        super().__init__()
        self.theme = theme
        self.engine = automation_engine
        self.subscription = subscription_manager
        self.config = automation_engine.config

        self._setup_ui()
        self._refresh_ui()

    # -- tier helpers ---------------------------------------------------------

    @property
    def _is_pro(self) -> bool:
        from core.subscription_manager import SubscriptionTier
        return self.subscription.current_tier in (SubscriptionTier.PRO, SubscriptionTier.PREMIUM)

    @property
    def _is_premium(self) -> bool:
        from core.subscription_manager import SubscriptionTier
        return self.subscription.current_tier == SubscriptionTier.PREMIUM

    @property
    def _can_change_execution_mode(self) -> bool:
        return self.subscription.has_feature("autonomous_mode")

    @property
    def _can_use_custom_rules(self) -> bool:
        return self.subscription.has_feature("custom_rules")

    @property
    def _can_use_analytics(self) -> bool:
        return self.subscription.has_feature("automation_analytics")

    # -- UI setup -------------------------------------------------------------

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("System Automation")
        header.setFont(QFont(self.font().family(), 20, QFont.Weight.Bold))
        layout.addWidget(header)

        subtitle = QLabel("Your computer adapts to your psychological state automatically.")
        subtitle.setStyleSheet("color: #666;")
        layout.addWidget(subtitle)

        # Tier badge
        tier_label = QLabel(f"Current plan: {self.subscription.current_tier.value.upper()}")
        tier_label.setStyleSheet(
            f"background: {'#2ECC71' if self._is_premium else '#3498DB' if self._is_pro else '#95A5A6'}; "
            "color: white; padding: 4px 12px; border-radius: 4px; font-weight: bold;"
        )
        layout.addWidget(tier_label)

        # Tab widget for organization
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Tab 1: Overview & Controls
        self.tab_widget.addTab(self._create_overview_tab(), "Overview")

        # Tab 2: Rules
        self.tab_widget.addTab(self._create_rules_tab(), "Rules")

        # Tab 3: Focus & Schedule (PRO+)
        self.tab_widget.addTab(self._create_focus_tab(), "Focus")

        # Tab 4: Analytics (PREMIUM)
        self.tab_widget.addTab(self._create_analytics_tab(), "Analytics")

    # -- Overview tab ---------------------------------------------------------

    def _create_overview_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        # Execution mode (PRO+)
        mode_group = QGroupBox("Execution Mode")
        mode_layout = QVBoxLayout(mode_group)

        mode_desc = QLabel(
            "Choose how aggressively the automation engine acts on your system."
        )
        mode_desc.setWordWrap(True)
        mode_desc.setStyleSheet("color: #666;")
        mode_layout.addWidget(mode_desc)

        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Suggestions Only — Notify but don't change anything", "suggestions_only")
        self.mode_combo.addItem("Ask First — Prompt before each action", "ask_first")
        self.mode_combo.addItem("Autonomous — Execute immediately", "autonomous")
        self.mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self.mode_combo)

        if not self._can_change_execution_mode:
            self.mode_combo.setEnabled(False)
            mode_note = QLabel("⚡ Upgrade to PRO to enable autonomous mode.")
            mode_note.setStyleSheet("color: #E67E22; font-weight: bold;")
            mode_layout.addWidget(mode_note)

        layout.addWidget(mode_group)

        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)

        self.focus_btn = QPushButton("🎯 Activate Focus Mode")
        self.focus_btn.setStyleSheet(
            "QPushButton { background-color: #2ECC71; color: white; "
            "border-radius: 6px; padding: 10px 20px; font-weight: bold; }"
            "QPushButton:hover { background-color: #27AE60; }"
        )
        self.focus_btn.clicked.connect(self._on_focus_clicked)
        actions_layout.addWidget(self.focus_btn)

        self.grounding_btn = QPushButton("🌿 Grounding Mode")
        self.grounding_btn.setStyleSheet(
            "QPushButton { background-color: #3498DB; color: white; "
            "border-radius: 6px; padding: 10px 20px; font-weight: bold; }"
            "QPushButton:hover { background-color: #2980B9; }"
        )
        self.grounding_btn.clicked.connect(self._on_grounding_clicked)
        actions_layout.addWidget(self.grounding_btn)

        self.crisis_btn = QPushButton("🚨 Crisis Mode")
        self.crisis_btn.setStyleSheet(
            "QPushButton { background-color: #E74C3C; color: white; "
            "border-radius: 6px; padding: 10px 20px; font-weight: bold; }"
            "QPushButton:hover { background-color: #C0392B; }"
        )
        self.crisis_btn.clicked.connect(self._on_crisis_clicked)
        actions_layout.addWidget(self.crisis_btn)

        layout.addWidget(actions_group)

        # Automation engine status
        status_group = QGroupBox("Engine Status")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel()
        status_layout.addWidget(self.status_label)

        self.toggle_engine_btn = QPushButton()
        self.toggle_engine_btn.clicked.connect(self._on_toggle_engine)
        status_layout.addWidget(self.toggle_engine_btn)

        layout.addWidget(status_group)
        layout.addStretch()

        return tab

    # -- Rules tab ------------------------------------------------------------

    def _create_rules_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        rules_label = QLabel("Active Automation Rules")
        rules_label.setFont(QFont(self.font().family(), 14, QFont.Weight.Bold))
        layout.addWidget(rules_label)

        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels(["Rule", "Trigger", "Enabled", "Actions", "Cooldown"])
        self.rules_table.horizontalHeader().setStretchLastSection(True)
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.rules_table)

        # Custom rule builder (PREMIUM)
        if self._can_use_custom_rules:
            custom_group = QGroupBox("Custom Rule Builder")
            custom_layout = QGridLayout(custom_group)

            custom_layout.addWidget(QLabel("Name:"), 0, 0)
            self.custom_name = QLineEdit()
            self.custom_name.setPlaceholderText("e.g., My Focus Rule")
            custom_layout.addWidget(self.custom_name, 0, 1)

            custom_layout.addWidget(QLabel("Trigger:"), 1, 0)
            self.custom_trigger = QComboBox()
            for tt in TriggerType:
                self.custom_trigger.addItem(tt.name, tt)
            custom_layout.addWidget(self.custom_trigger, 1, 1)

            custom_layout.addWidget(QLabel("Action:"), 2, 0)
            self.custom_action = QComboBox()
            for at in ActionType:
                self.custom_action.addItem(at.name, at)
            custom_layout.addWidget(self.custom_action, 2, 1)

            custom_layout.addWidget(QLabel("Target:"), 3, 0)
            self.custom_target = QLineEdit()
            self.custom_target.setPlaceholderText("e.g., Slack or 50")
            custom_layout.addWidget(self.custom_target, 3, 1)

            add_btn = QPushButton("Add Custom Rule")
            add_btn.setStyleSheet(
                "QPushButton { background-color: #9B59B6; color: white; "
                "border-radius: 6px; padding: 8px 16px; font-weight: bold; }"
            )
            add_btn.clicked.connect(self._on_add_custom_rule)
            custom_layout.addWidget(add_btn, 4, 1)

            layout.addWidget(custom_group)
        else:
            upsell = QLabel("🌟 Custom rule builder available with PREMIUM.")
            upsell.setStyleSheet("color: #9B59B6; font-weight: bold; padding: 12px;")
            upsell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(upsell)

        # Profile selector (PREMIUM)
        if self._is_premium:
            profile_group = QGroupBox("Automation Profile")
            profile_layout = QHBoxLayout(profile_group)

            self.profile_combo = QComboBox()
            self.profile_combo.currentIndexChanged.connect(self._on_profile_changed)
            profile_layout.addWidget(self.profile_combo)

            new_profile_btn = QPushButton("New Profile")
            new_profile_btn.clicked.connect(self._on_new_profile)
            profile_layout.addWidget(new_profile_btn)

            layout.addWidget(profile_group)

        refresh_btn = QPushButton("Refresh Rules")
        refresh_btn.clicked.connect(self._refresh_rules_table)
        layout.addWidget(refresh_btn)

        return tab

    # -- Focus tab ------------------------------------------------------------

    def _create_focus_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        # Focus sessions
        focus_group = QGroupBox("Focus Sessions")
        focus_layout = QVBoxLayout(focus_group)

        self.focus_status = QLabel("Focus mode: Inactive")
        focus_layout.addWidget(self.focus_status)

        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration (min):"))
        self.focus_duration = QSpinBox()
        self.focus_duration.setRange(5, 240)
        self.focus_duration.setValue(25)
        duration_layout.addWidget(self.focus_duration)
        focus_layout.addLayout(duration_layout)

        focus_btns = QHBoxLayout()
        start_btn = QPushButton("Start Focus")
        start_btn.clicked.connect(self._on_start_focus)
        focus_btns.addWidget(start_btn)

        stop_btn = QPushButton("Stop Focus")
        stop_btn.clicked.connect(self._on_stop_focus)
        focus_btns.addWidget(stop_btn)

        focus_layout.addLayout(focus_btns)
        layout.addWidget(focus_group)

        # Scheduled blocks (PREMIUM)
        if self._is_premium:
            blocks_group = QGroupBox("Scheduled Focus Blocks")
            blocks_layout = QVBoxLayout(blocks_group)

            self.blocks_table = QTableWidget()
            self.blocks_table.setColumnCount(4)
            self.blocks_table.setHorizontalHeaderLabels(["Name", "Start", "End", "Days"])
            self.blocks_table.horizontalHeader().setStretchLastSection(True)
            blocks_layout.addWidget(self.blocks_table)

            add_block_btn = QPushButton("Add Scheduled Block")
            add_block_btn.clicked.connect(self._on_add_block)
            blocks_layout.addWidget(add_block_btn)

            layout.addWidget(blocks_group)
        else:
            upsell = QLabel("📅 Scheduled focus blocks available with PREMIUM.")
            upsell.setStyleSheet("color: #9B59B6; font-weight: bold; padding: 12px;")
            upsell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(upsell)

        layout.addStretch()
        return tab

    # -- Analytics tab --------------------------------------------------------

    def _create_analytics_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        if not self._can_use_analytics:
            upsell = QLabel("📊 Automation analytics available with PREMIUM.")
            upsell.setStyleSheet("color: #9B59B6; font-weight: bold; padding: 40px;")
            upsell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(upsell)
            layout.addStretch()
            return tab

        header = QLabel("Automation Effectiveness")
        header.setFont(QFont(self.font().family(), 16, QFont.Weight.Bold))
        layout.addWidget(header)

        self.analytics_text = QTextEdit()
        self.analytics_text.setReadOnly(True)
        layout.addWidget(self.analytics_text)

        refresh_btn = QPushButton("Refresh Analytics")
        refresh_btn.clicked.connect(self._refresh_analytics)
        layout.addWidget(refresh_btn)

        return tab

    # -- refresh logic --------------------------------------------------------

    def _refresh_ui(self) -> None:
        """Refresh all UI elements with current state."""
        self._refresh_mode_combo()
        self._refresh_status()
        self._refresh_rules_table()
        self._refresh_focus_status()
        self._refresh_profiles()
        self._refresh_analytics()
        self._refresh_blocks()

    def _refresh_mode_combo(self) -> None:
        profile = self.config.active_profile
        mode_map = {
            ExecutionMode.SUGGESTIONS_ONLY: 0,
            ExecutionMode.ASK_FIRST: 1,
            ExecutionMode.AUTONOMOUS: 2,
        }
        idx = mode_map.get(profile.execution_mode, 0)
        self.mode_combo.setCurrentIndex(idx)

    def _refresh_status(self) -> None:
        enabled = self.engine.is_enabled
        self.status_label.setText(
            f"Engine: {'Running' if enabled else 'Paused'} | "
            f"Profile: {self.config.active_profile.name} | "
            f"Mode: {self.config.active_profile.execution_mode.value}"
        )
        self.toggle_engine_btn.setText("Pause Engine" if enabled else "Resume Engine")

    def _refresh_rules_table(self) -> None:
        rules = self.engine.list_rules()
        self.rules_table.setRowCount(len(rules))
        for i, rule in enumerate(rules):
            self.rules_table.setItem(i, 0, QTableWidgetItem(rule["name"]))
            self.rules_table.setItem(i, 1, QTableWidgetItem(rule["trigger"]))
            enabled_item = QTableWidgetItem("Yes" if rule["enabled"] else "No")
            self.rules_table.setItem(i, 2, enabled_item)
            self.rules_table.setItem(i, 3, QTableWidgetItem(str(rule["actions"])))
            self.rules_table.setItem(i, 4, QTableWidgetItem(f"{rule['cooldown_minutes']} min"))

    def _refresh_focus_status(self) -> None:
        focus = self.engine.focus
        if focus.state.name == "ACTIVE":
            self.focus_status.setText(
                f"Focus mode: ACTIVE | Started: {focus.current_session.started_at.strftime('%H:%M') if focus.current_session else 'N/A'}"
            )
            self.focus_btn.setText("🛑 Deactivate Focus")
        else:
            self.focus_status.setText("Focus mode: Inactive")
            self.focus_btn.setText("🎯 Activate Focus Mode")

    def _refresh_profiles(self) -> None:
        if not self._is_premium or not hasattr(self, 'profile_combo'):
            return
        self.profile_combo.clear()
        for p in self.config.profiles.values():
            label = f"{p.name}{' (active)' if p.profile_id == self.config.active_profile_id else ''}"
            self.profile_combo.addItem(label, p.profile_id)
        idx = self.profile_combo.findData(self.config.active_profile_id)
        if idx >= 0:
            self.profile_combo.setCurrentIndex(idx)

    def _refresh_analytics(self) -> None:
        if not self._can_use_analytics or not hasattr(self, 'analytics_text'):
            return
        data = self.engine.get_analytics()
        if not data:
            self.analytics_text.setPlainText("No analytics data available yet.")
            return

        lines = [
            "=== Overall Stats ===",
            f"Total rules fired: {data['overall']['total_rules_fired']}",
            f"Total display adaptations: {data['overall']['total_display_adaptations']}",
            f"Total apps closed: {data['overall']['total_apps_closed']}",
            f"Unique rules used: {data['overall']['unique_rules_used']}",
            f"Active days: {data['overall']['active_days']}",
            "",
            "=== Focus Trends (30 days) ===",
            f"Total sessions: {data['focus_trends']['total_sessions']}",
            f"Total minutes: {data['focus_trends']['total_minutes']}",
            f"Avg duration: {data['focus_trends']['avg_duration']} min",
            f"Interruption rate: {data['focus_trends']['interruption_rate']}",
            "",
            "=== Rule Effectiveness ===",
        ]
        for rule in data.get("rule_effectiveness", []):
            lines.append(
                f"  {rule['rule_name']}: fired {rule['times_fired']}x, "
                f"success rate {rule.get('success_rate', 0)}"
            )
        self.analytics_text.setPlainText("\n".join(lines))

    def _refresh_blocks(self) -> None:
        if not self._is_premium or not hasattr(self, 'blocks_table'):
            return
        blocks = self.config.scheduled_blocks
        self.blocks_table.setRowCount(len(blocks))
        for i, block in enumerate(blocks):
            self.blocks_table.setItem(i, 0, QTableWidgetItem(block.name))
            self.blocks_table.setItem(i, 1, QTableWidgetItem(block.start_time.strftime("%H:%M")))
            self.blocks_table.setItem(i, 2, QTableWidgetItem(block.end_time.strftime("%H:%M")))
            days = ",".join(["M", "T", "W", "Th", "F", "Sa", "Su"][d] for d in block.days_of_week)
            self.blocks_table.setItem(i, 3, QTableWidgetItem(days))

    # -- event handlers -------------------------------------------------------

    def _on_mode_changed(self, index: int) -> None:
        if not self._can_change_execution_mode:
            return
        mode_values = [ExecutionMode.SUGGESTIONS_ONLY, ExecutionMode.ASK_FIRST, ExecutionMode.AUTONOMOUS]
        mode = mode_values[index]
        self.config.set_execution_mode(self.config.active_profile_id, mode)
        self._refresh_status()

    def _on_toggle_engine(self) -> None:
        if self.engine.is_enabled:
            self.engine.disable()
        else:
            self.engine.enable()
        self._refresh_status()

    def _on_focus_clicked(self) -> None:
        focus = self.engine.focus
        if focus.state.name == "ACTIVE":
            focus.deactivate()
        else:
            self.engine.manual_focus()
        self._refresh_focus_status()

    def _on_grounding_clicked(self) -> None:
        result = self.engine.manual_grounding()
        QMessageBox.information(self, "Grounding Mode", self._summarize(result, "Grounding"))

    def _on_crisis_clicked(self) -> None:
        result = self.engine.manual_crisis()
        QMessageBox.information(self, "Crisis Mode", self._summarize(result, "Crisis"))

    def _summarize(self, result: dict, mode_name: str) -> str:
        """Build an honest message about what the mode actually did.

        Free tier = suggestions only; otherwise report how many system actions
        actually succeeded rather than claiming a blanket success.
        """
        results = result.get("automation_results") or []
        try:
            can_act = bool(self.engine._can_execute_system_actions)
        except Exception:
            can_act = False
        if not can_act:
            return (
                f"{mode_name} mode is on. On your current plan Hearth suggests "
                "supportive changes; upgrade to Pro to let it apply them to your "
                "system automatically."
            )
        applied = [r for r in results if isinstance(r, dict) and r.get("success")]
        if applied:
            return f"{mode_name} mode is on — applied {len(applied)} change(s) to your environment."
        return (
            f"{mode_name} mode is on. No system changes were applied "
            "(your platform may not support them yet)."
        )

    def _on_start_focus(self) -> None:
        duration = self.focus_duration.value()
        self.engine.manual_focus(duration_minutes=duration)
        self._refresh_focus_status()

    def _on_stop_focus(self) -> None:
        self.engine.focus.deactivate()
        self._refresh_focus_status()

    def _on_add_custom_rule(self) -> None:
        name = self.custom_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a rule name.")
            return

        trigger = self.custom_trigger.currentData()
        action_type = self.custom_action.currentData()
        target = self.custom_target.text().strip() or None

        rule = AutomationRule(
            name=name,
            trigger=trigger,
            actions=[AutomationAction(action_type=action_type, target=target, reason=f"Custom: {name}")],
        )
        self.config.add_custom_rule(self.config.active_profile_id, rule)
        self.custom_name.clear()
        self.custom_target.clear()
        self._refresh_rules_table()
        QMessageBox.information(self, "Rule Added", f"Custom rule '{name}' added.")

    def _on_profile_changed(self, index: int) -> None:
        profile_id = self.profile_combo.itemData(index)
        if profile_id:
            self.config.set_active_profile(profile_id)
            self._refresh_ui()

    def _on_new_profile(self) -> None:
        # Simple prompt — could be a dialog
        name, ok = QMessageBox.question(self, "New Profile", "Create a new automation profile?")
        if ok == QMessageBox.StandardButton.Yes:
            profile = self.config.create_profile(name="New Profile", description="Custom profile")
            self._refresh_profiles()
            self.config.set_active_profile(profile.profile_id)
            self._refresh_ui()

    def _on_add_block(self) -> None:
        block = ScheduledFocusBlock(
            block_id="block_1",
            name="Morning Focus",
            start_time=time(9, 0),
            end_time=time(11, 0),
            days_of_week=[0, 1, 2, 3, 4],
        )
        self.config.add_scheduled_block(block)
        self._refresh_blocks()
