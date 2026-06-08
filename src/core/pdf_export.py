"""
PDF wellness report generator.

Generates a personal, printable PDF from wellness data with embedded
charts (mood trends, sleep, energy, medication adherence) using matplotlib
+ reportlab. Falls back to a self-contained HTML file if reportlab is
unavailable.

IMPORTANT: This report is for personal reflection only. It is not a
substitute for professional medical advice, diagnosis, or treatment.
"""

from __future__ import annotations

import base64
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Image,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    _HAS_REPORTLAB = True
except ImportError:
    _HAS_REPORTLAB = False

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False

try:
    import weasyprint

    _HAS_WEASYPRINT = True
except ImportError:
    _HAS_WEASYPRINT = False


# ---------------------------------------------------------------------------
# WellnessPDFExporter
# ---------------------------------------------------------------------------


class WellnessPDFExporter:
    """Export wellness summaries to PDF or print-ready HTML."""

    BRAND_COLOR = "#2C3E50"
    ACCENT_COLOR = "#3498DB"
    WARN_COLOR = "#E74C3C"
    SUCCESS_COLOR = "#27AE60"
    BG_COLOR = "#F8F9FA"

    def __init__(self) -> None:
        pass

    def export(
        self,
        summary: dict[str, Any],
        output_path: Path,
        user_name: str = "You",
    ) -> Path:
        if _HAS_REPORTLAB and output_path.suffix.lower() == ".pdf":
            return self._export_pdf(summary, output_path, user_name)
        if _HAS_WEASYPRINT and output_path.suffix.lower() == ".pdf":
            return self._export_weasyprint(summary, output_path, user_name)
        html_path = output_path.with_suffix(".html")
        return self._export_html(summary, html_path, user_name)

    def export_with_browser_fallback(
        self,
        summary: dict[str, Any],
        output_path: Path,
        user_name: str = "You",
    ) -> Path:
        """Export to PDF if possible, otherwise open HTML in the browser.

        Returns the path to the generated file (PDF or HTML).  When an HTML
        fallback is used, the user's default browser is opened with a note
        that they can use the browser's Print → Save as PDF feature.
        """
        result = self.export(summary, output_path, user_name)
        if result.suffix.lower() == ".pdf":
            return result

        # Open the HTML report in the default browser so the user can
        # print-to-PDF.
        import platform
        import subprocess

        try:
            url = str(result.resolve())
            if platform.system() == "Darwin":
                subprocess.run(["open", url], check=False)
            elif platform.system() == "Windows":
                subprocess.run(["start", url], shell=True, check=False)
            else:
                subprocess.run(["xdg-open", url], check=False)
        except Exception as exc:
            logger.warning("Could not open browser for HTML fallback: %s", exc)
        return result

    def _export_weasyprint(
        self,
        summary: dict[str, Any],
        output_path: Path,
        user_name: str,
    ) -> Path:
        html_path = output_path.with_suffix(".html")
        self._export_html(summary, html_path, user_name)
        weasyprint.HTML(str(html_path)).write_pdf(str(output_path))
        return output_path

    # -- PDF generation ----------------------------------------------------

    def _export_pdf(
        self,
        summary: dict[str, Any],
        output_path: Path,
        user_name: str,
    ) -> Path:
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=60,
            leftMargin=60,
            topMargin=60,
            bottomMargin=40,
        )
        styles = getSampleStyleSheet()
        story: list[Any] = []

        # Brand header
        story.extend(self._build_header(styles, user_name, summary))

        # Mood section with chart
        story.extend(self._build_mood_section(styles, summary))
        story.append(Spacer(1, 0.15 * inch))

        # Energy section with chart
        story.extend(self._build_energy_section(styles, summary))
        story.append(Spacer(1, 0.15 * inch))

        # Sleep section with chart
        story.extend(self._build_sleep_section(styles, summary))
        story.append(Spacer(1, 0.15 * inch))

        # Medication adherence calendar
        story.extend(self._build_medication_section(styles, summary))
        story.append(Spacer(1, 0.15 * inch))

        # Task completion
        story.extend(self._build_task_section(styles, summary))
        story.append(Spacer(1, 0.15 * inch))

        # Values alignment
        story.extend(self._build_values_section(styles, summary))
        story.append(Spacer(1, 0.15 * inch))

        # Crisis signals
        story.extend(self._build_crisis_section(styles, summary))

        # Footer
        story.append(Spacer(1, 0.3 * inch))
        story.append(
            Paragraph(
                (
                    "This report is generated from locally-stored data for personal reflection only. "
                    "It is not a substitute for professional medical advice, diagnosis, or treatment. "
                    "If you are in crisis, contact emergency services or a crisis helpline immediately."
                ),
                styles["Italic"],
            )
        )

        doc.build(story)
        return output_path

    def _build_header(self, styles: Any, user_name: str, summary: dict[str, Any]) -> list[Any]:
        title_style = ParagraphStyle(
            "BrandTitle",
            parent=styles["Heading1"],
            fontSize=22,
            textColor=colors.HexColor(self.BRAND_COLOR),
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "BrandSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.HexColor("#666666"),
            spaceAfter=12,
        )
        period_days = summary.get("period_days", 30)
        generated = summary.get("generated_at", "")[:10]
        return [
            Paragraph("Mindful Organizer", title_style),
            Paragraph("Personal Wellness Report", subtitle_style),
            Paragraph(f"<b>Name:</b> {user_name}", styles["Normal"]),
            Paragraph(
                f"<b>Report Period:</b> Last {period_days} days | <b>Generated:</b> {generated}",
                styles["Normal"],
            ),
            Spacer(1, 0.2 * inch),
        ]

    def _build_mood_section(self, styles: Any, summary: dict[str, Any]) -> list[Any]:
        heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor(self.ACCENT_COLOR),
            spaceAfter=8,
        )
        story = [Paragraph("Mood Trends", heading)]
        mood = summary.get("mood", {})
        entries = mood.get("entries", [])

        if _HAS_MATPLOTLIB and entries:
            chart = self._mood_chart(entries)
            if chart:
                story.append(Image(chart, width=5 * inch, height=2.2 * inch))

        data = [
            ["Metric", "Value"],
            ["Entries logged", str(mood.get("count", 0))],
            ["Average mood", f"{mood.get('average', 'N/A')}"],
            ["Trend", mood.get("trend", "N/A")],
        ]
        story.append(self._make_table(data))
        return story

    def _build_energy_section(self, styles: Any, summary: dict[str, Any]) -> list[Any]:
        heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor(self.ACCENT_COLOR),
            spaceAfter=8,
        )
        story = [Paragraph("Energy Patterns", heading)]
        energy = summary.get("energy", {})
        entries = energy.get("entries", [])

        if _HAS_MATPLOTLIB and entries:
            chart = self._energy_chart(entries)
            if chart:
                story.append(Image(chart, width=5 * inch, height=2.2 * inch))

        data = [
            ["Metric", "Value"],
            ["Average energy", f"{energy.get('average', 'N/A')}"],
            ["Peak time", energy.get("peak_time", "N/A")],
            ["Lowest time", energy.get("low_time", "N/A")],
        ]
        story.append(self._make_table(data))
        return story

    def _build_sleep_section(self, styles: Any, summary: dict[str, Any]) -> list[Any]:
        heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor(self.ACCENT_COLOR),
            spaceAfter=8,
        )
        story = [Paragraph("Sleep", heading)]
        sleep = summary.get("sleep", {})
        entries = sleep.get("entries", [])

        if _HAS_MATPLOTLIB and entries:
            chart = self._sleep_chart(entries)
            if chart:
                story.append(Image(chart, width=5 * inch, height=2.2 * inch))

        data = [
            ["Metric", "Value"],
            ["Entries logged", str(sleep.get("count", 0))],
            ["Average hours", f"{sleep.get('average_hours', 'N/A')}"],
            ["Sleep quality avg", f"{sleep.get('average_quality', 'N/A')}"],
        ]
        story.append(self._make_table(data))
        return story

    def _build_medication_section(self, styles: Any, summary: dict[str, Any]) -> list[Any]:
        heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor(self.ACCENT_COLOR),
            spaceAfter=8,
        )
        story = [Paragraph("Medication Adherence", heading)]
        med = summary.get("medication", {})
        adherence_by_day = med.get("adherence_by_day", [])

        if _HAS_MATPLOTLIB and adherence_by_day:
            chart = self._medication_heatmap(adherence_by_day)
            if chart:
                story.append(Image(chart, width=5 * inch, height=1.8 * inch))

        data = [
            ["Metric", "Value"],
            ["Total scheduled", str(med.get("total_scheduled", 0))],
            ["Taken on time", str(med.get("taken_on_time", 0))],
            ["Adherence rate", f"{med.get('adherence_rate', 0) * 100:.0f}%"],
        ]
        story.append(self._make_table(data))
        return story

    def _build_task_section(self, styles: Any, summary: dict[str, Any]) -> list[Any]:
        heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor(self.ACCENT_COLOR),
            spaceAfter=8,
        )
        story = [Paragraph("Task Completion", heading)]
        tasks = summary.get("tasks", {})
        data = [
            ["Metric", "Value"],
            ["Total tasks", str(tasks.get("total", 0))],
            ["Completed", str(tasks.get("completed", 0))],
            ["Completion rate", f"{tasks.get('completion_rate', 0) * 100:.0f}%"],
            ["Avg energy per task", f"{tasks.get('avg_energy_required', 'N/A')}"],
        ]
        story.append(self._make_table(data))
        return story

    def _build_values_section(self, styles: Any, summary: dict[str, Any]) -> list[Any]:
        heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor(self.ACCENT_COLOR),
            spaceAfter=8,
        )
        story = [Paragraph("Values Alignment", heading)]
        values = summary.get("values", {})
        scores = values.get("scores", [])

        if _HAS_MATPLOTLIB and scores:
            chart = self._values_radar(scores)
            if chart:
                story.append(Image(chart, width=4 * inch, height=3 * inch))

        if values.get("top_value"):
            story.append(
                Paragraph(
                    f"<b>Top value this week:</b> {values['top_value']}",
                    styles["Normal"],
                )
            )
        if values.get("neglected_value"):
            story.append(
                Paragraph(
                    f"<b>Needs attention:</b> {values['neglected_value']}",
                    styles["Normal"],
                )
            )
        return story

    def _build_crisis_section(self, styles: Any, summary: dict[str, Any]) -> list[Any]:
        signals = summary.get("crisis_signals", [])
        if not signals:
            return []
        heading = ParagraphStyle(
            "CrisisHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor(self.WARN_COLOR),
            spaceAfter=8,
        )
        story = [Paragraph("Wellness Check-Ins", heading)]
        for sig in signals:
            severity = sig.get("severity", "info")
            color = self.WARN_COLOR if severity in ("moderate", "urgent") else self.ACCENT_COLOR
            story.append(
                Paragraph(
                    f"<font color='{color}'><b>{severity.title()}:</b></font> "
                    f"{sig.get('description', '')}",
                    styles["Normal"],
                )
            )
            story.append(
                Paragraph(
                    f"<i>Suggestion:</i> {sig.get('recommendation', '')}",
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 0.08 * inch))
        return story

    # -- charts ------------------------------------------------------------

    def _mood_chart(self, entries: list[dict[str, Any]]) -> Any:
        if not entries:
            return None
        try:
            dates = [datetime.fromisoformat(e["timestamp"]) for e in entries if e.get("timestamp")]
            scores = [e["mood_score"] for e in entries if e.get("mood_score") is not None]
            if len(dates) != len(scores) or not dates:
                return None
            fig, ax = plt.subplots(figsize=(6, 2.5))
            ax.plot(dates, scores, color=self.ACCENT_COLOR, linewidth=1.5, marker="o", markersize=3)
            ax.axhline(5, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
            ax.fill_between(
                dates,
                scores,
                5,
                where=[s >= 5 for s in scores],
                alpha=0.2,
                color=self.SUCCESS_COLOR,
            )
            ax.fill_between(
                dates, scores, 5, where=[s < 5 for s in scores], alpha=0.2, color=self.WARN_COLOR
            )
            ax.set_ylim(0, 10)
            ax.set_ylabel("Mood (0-10)")
            ax.set_title("Mood Over Time", fontsize=10, color=self.BRAND_COLOR)
            ax.tick_params(axis="x", rotation=30, labelsize=7)
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=120)
            plt.close(fig)
            buf.seek(0)
            return buf
        except Exception:
            logger.exception("Mood chart generation failed")
            return None

    def _energy_chart(self, entries: list[dict[str, Any]]) -> Any:
        if not entries:
            return None
        try:
            dates = [datetime.fromisoformat(e["timestamp"]) for e in entries if e.get("timestamp")]
            scores = [e.get("energy_level", e.get("energy_score", 0)) for e in entries]
            if len(dates) != len(scores) or not dates:
                return None
            fig, ax = plt.subplots(figsize=(6, 2.5))
            ax.plot(dates, scores, color="#9B59B6", linewidth=1.5, marker="s", markersize=3)
            ax.set_ylim(0, 100)
            ax.set_ylabel("Energy (0-100)")
            ax.set_title("Energy Over Time", fontsize=10, color=self.BRAND_COLOR)
            ax.tick_params(axis="x", rotation=30, labelsize=7)
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=120)
            plt.close(fig)
            buf.seek(0)
            return buf
        except Exception:
            logger.exception("Energy chart generation failed")
            return None

    def _sleep_chart(self, entries: list[dict[str, Any]]) -> Any:
        if not entries:
            return None
        try:
            dates = []
            hours = []
            for e in entries:
                d = e.get("date") or e.get("timestamp")
                if d:
                    dates.append(datetime.fromisoformat(str(d)))
                    hours.append(e.get("duration_hours", e.get("hours", 0)))
            if not dates:
                return None
            fig, ax = plt.subplots(figsize=(6, 2.5))
            ax.bar(dates, hours, color="#1ABC9C", width=0.7, alpha=0.8)
            ax.axhline(7, color="gray", linestyle="--", linewidth=0.8, alpha=0.5)
            ax.set_ylabel("Hours")
            ax.set_title("Sleep Duration", fontsize=10, color=self.BRAND_COLOR)
            ax.tick_params(axis="x", rotation=30, labelsize=7)
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=120)
            plt.close(fig)
            buf.seek(0)
            return buf
        except Exception:
            logger.exception("Sleep chart generation failed")
            return None

    def _medication_heatmap(self, adherence_by_day: list[dict[str, Any]]) -> Any:
        if not adherence_by_day:
            return None
        try:
            days = [d["day"] for d in adherence_by_day]
            rates = [d["rate"] for d in adherence_by_day]
            fig, ax = plt.subplots(figsize=(6, 2))
            colors_map = [
                self.SUCCESS_COLOR if r >= 1.0 else (self.WARN_COLOR if r < 0.5 else "#F39C12")
                for r in rates
            ]
            ax.barh(
                ["Adherence"] * len(days),
                [1] * len(days),
                left=range(len(days)),
                color=colors_map,
                height=0.6,
            )
            ax.set_xlim(0, len(days))
            ax.set_xticks(range(0, len(days), max(1, len(days) // 7)))
            ax.set_xticklabels(
                [days[i] for i in range(0, len(days), max(1, len(days) // 7))],
                rotation=45,
                ha="right",
                fontsize=7,
            )
            ax.set_yticks([])
            ax.set_title("Daily Medication Adherence", fontsize=10, color=self.BRAND_COLOR)
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=120)
            plt.close(fig)
            buf.seek(0)
            return buf
        except Exception:
            logger.exception("Medication chart generation failed")
            return None

    def _values_radar(self, scores: list[dict[str, Any]]) -> Any:
        if not scores:
            return None
        try:
            labels = [s["value_name"] for s in scores[:8]]
            values = [s.get("tasks_aligned", 0) for s in scores[:8]]
            if not labels:
                return None
            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
            values += values[:1]
            angles += angles[:1]
            fig, ax = plt.subplots(figsize=(4, 4), subplot_kw={"polar": True})
            ax.fill(angles, values, color=self.ACCENT_COLOR, alpha=0.25)
            ax.plot(angles, values, color=self.ACCENT_COLOR, linewidth=1.5)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, fontsize=7)
            ax.set_title("Values Alignment", fontsize=10, color=self.BRAND_COLOR, pad=15)
            fig.tight_layout()
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=120)
            plt.close(fig)
            buf.seek(0)
            return buf
        except Exception:
            logger.exception("Values radar generation failed")
            return None

    # -- helpers -----------------------------------------------------------

    def _make_table(self, data: list[list[str]]) -> Table:
        table = Table(data, colWidths=[2.5 * inch, 2.5 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(self.ACCENT_COLOR)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor(self.BG_COLOR)),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        return table

    # -- HTML fallback -----------------------------------------------------

    def _export_html(
        self,
        summary: dict[str, Any],
        output_path: Path,
        user_name: str,
    ) -> Path:
        period_days = summary.get("period_days", 30)
        generated = summary.get("generated_at", "")[:10]
        mood = summary.get("mood", {})
        sleep = summary.get("sleep", {})
        med = summary.get("medication", {})
        tasks = summary.get("tasks", {})
        values = summary.get("values", {})
        signals = summary.get("crisis_signals", [])

        # Embed charts as base64 if matplotlib is available
        charts_html = ""
        if _HAS_MATPLOTLIB:
            for chart_name, entries_key, chart_method in [
                ("mood_chart", "entries", self._mood_chart),
                ("energy_chart", "entries", self._energy_chart),
                ("sleep_chart", "entries", self._sleep_chart),
            ]:
                entries = summary.get(chart_name.replace("_chart", ""), {}).get(entries_key, [])
                buf = chart_method(entries)
                if buf:
                    b64 = base64.b64encode(buf.getvalue()).decode()
                    charts_html += f'<img src="data:image/png;base64,{b64}" style="max-width:100%;margin:12px 0;">\n'

        signals_html = ""
        for sig in signals:
            severity = sig.get("severity", "")
            css = "severe" if severity in ("moderate", "urgent") else ""
            signals_html += f"""
<div class="signal {css}">
  <strong>{severity.title()}:</strong> {sig.get("description", "")}<br>
  <em>Suggestion:</em> {sig.get("recommendation", "")}
</div>
"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Wellness Report — {user_name}</title>
<style>
  body {{ font-family: Georgia, serif; max-width: 720px; margin: 40px auto; color: #222; line-height: 1.6; padding: 0 20px; }}
  h1 {{ color: {self.BRAND_COLOR}; border-bottom: 2px solid {self.ACCENT_COLOR}; padding-bottom: 8px; font-size: 1.6em; }}
  h2 {{ color: {self.ACCENT_COLOR}; font-size: 1.2em; margin-top: 28px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
  th {{ background: {self.ACCENT_COLOR}; color: white; text-align: left; padding: 8px; }}
  td {{ background: {self.BG_COLOR}; padding: 8px; border: 1px solid #ddd; }}
  .footer {{ margin-top: 40px; font-style: italic; color: #666; font-size: 0.9em; }}
  .signal {{ margin: 8px 0; padding: 8px; background: #FFF3CD; border-left: 4px solid #F39C12; }}
  .signal.severe {{ background: #F8D7DA; border-left-color: {self.WARN_COLOR}; }}
  img {{ border-radius: 6px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
</style>
</head>
<body>
<h1>Mindful Organizer — Personal Wellness Report</h1>
<p><strong>Name:</strong> {user_name}</p>
<p><strong>Period:</strong> Last {period_days} days | <strong>Generated:</strong> {generated}</p>

{charts_html}

<h2>Mood Trends</h2>
<table>
  <tr><th>Metric</th><th>Value</th></tr>
  <tr><td>Entries logged</td><td>{mood.get("count", 0)}</td></tr>
  <tr><td>Average mood</td><td>{mood.get("average", "N/A")}</td></tr>
  <tr><td>Trend</td><td>{mood.get("trend", "N/A")}</td></tr>
</table>

<h2>Sleep</h2>
<table>
  <tr><th>Metric</th><th>Value</th></tr>
  <tr><td>Entries logged</td><td>{sleep.get("count", 0)}</td></tr>
  <tr><td>Average hours</td><td>{sleep.get("average_hours", "N/A")}</td></tr>
  <tr><td>Average quality</td><td>{sleep.get("average_quality", "N/A")}</td></tr>
</table>

<h2>Medication Adherence</h2>
<table>
  <tr><th>Metric</th><th>Value</th></tr>
  <tr><td>Total scheduled</td><td>{med.get("total_scheduled", 0)}</td></tr>
  <tr><td>Taken on time</td><td>{med.get("taken_on_time", 0)}</td></tr>
  <tr><td>Adherence rate</td><td>{med.get("adherence_rate", 0) * 100:.0f}%</td></tr>
</table>

<h2>Task Completion</h2>
<table>
  <tr><th>Metric</th><th>Value</th></tr>
  <tr><td>Total tasks</td><td>{tasks.get("total", 0)}</td></tr>
  <tr><td>Completed</td><td>{tasks.get("completed", 0)}</td></tr>
  <tr><td>Completion rate</td><td>{tasks.get("completion_rate", 0) * 100:.0f}%</td></tr>
</table>

<h2>Values Alignment</h2>
<p><strong>Top value:</strong> {values.get("top_value", "N/A")}</p>
<p><strong>Needs attention:</strong> {values.get("neglected_value", "N/A")}</p>

{signals_html and f"<h2>Wellness Check-Ins</h2>{signals_html}" or ""}

<div class="footer">
  This report is generated from locally-stored data for personal reflection only.
  It is not a substitute for professional medical advice, diagnosis, or treatment.
  If you are in crisis, contact emergency services or a crisis helpline immediately.
</div>
</body>
</html>
"""
        output_path.write_text(html, encoding="utf-8")
        return output_path


# Backwards-compatible alias used by validation and legacy imports.
PDFExporter = WellnessPDFExporter
