"""
Data portability and wellness report generation for Mindful Organizer.

Supports JSON/CSV/PDF export, selective date-range export, settings
import/export, data anonymization, and wellness report building.
"""

import csv
import hashlib
import io
import json
import logging
import statistics
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DATA_DIR = Path.home() / ".mindful_organizer"


# ---------------------------------------------------------------------------
# Enums & data classes
# ---------------------------------------------------------------------------

class ExportFormat(Enum):
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"


class DataCategory(Enum):
    MOOD = "mood_entries"
    TASKS = "tasks"
    SLEEP = "sleep_logs"
    MEDICATION = "medication_logs"
    JOURNAL = "journal_entries"
    ENERGY = "energy_readings"
    ACHIEVEMENTS = "achievements"
    BREATHING = "breathing_sessions"
    NOTIFICATIONS = "notifications"
    CRISIS_PLANS = "crisis_plans"
    SETTINGS = "settings"


@dataclass
class ExportOptions:
    """Controls what gets exported and how."""
    format: ExportFormat = ExportFormat.JSON
    categories: list[DataCategory] = field(default_factory=lambda: list(DataCategory))
    start_date: date | None = None
    end_date: date | None = None
    anonymize: bool = False
    include_settings: bool = True
    output_path: Path | None = None

    @property
    def effective_output_path(self) -> Path:
        if self.output_path:
            return self.output_path
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "json" if self.format == ExportFormat.JSON else self.format.value
        return DATA_DIR / "exports" / f"export_{ts}.{ext}"


@dataclass
class ImportValidation:
    """Result of validating an import file before applying."""
    is_valid: bool = False
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    record_counts: dict[str, int] = field(default_factory=dict)
    schema_version: int | None = None


@dataclass
class WellnessReportSection:
    title: str
    content: str
    data: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Anonymizer
# ---------------------------------------------------------------------------

class _Anonymizer:
    """Strips or hashes personally identifiable information."""

    _SENSITIVE_KEYS = {
        "prescriber", "support_contacts", "professional_contacts",
        "emergency_numbers", "personal_notes", "dreams",
    }
    _NAME_LIKE_KEYS = {"medication_name", "name", "title"}

    def __init__(self, salt: str = "") -> None:
        self._salt = salt

    def _hash(self, value: str) -> str:
        return hashlib.sha256((self._salt + value).encode()).hexdigest()[:12]

    def anonymize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        cleaned: dict[str, Any] = {}
        for key, value in row.items():
            if key in self._SENSITIVE_KEYS:
                cleaned[key] = "[REDACTED]"
            elif key in self._NAME_LIKE_KEYS and isinstance(value, str):
                cleaned[key] = f"ANON_{self._hash(value)}"
            elif key == "content" and isinstance(value, str):
                # Journal content: redact but keep length indicator
                cleaned[key] = f"[REDACTED - {len(value)} chars]"
            elif key == "notes" and isinstance(value, str):
                cleaned[key] = f"[REDACTED - {len(value)} chars]"
            else:
                cleaned[key] = value
        return cleaned


# ---------------------------------------------------------------------------
# ExportManager
# ---------------------------------------------------------------------------

class ExportManager:
    """Handles data export, import, and wellness report generation.

    Usage::

        from core.database import DatabaseManager
        db = DatabaseManager()
        db.initialize()
        em = ExportManager(db)

        # Full JSON export
        path = em.export(ExportOptions(format=ExportFormat.JSON))

        # Selective export (mood + sleep, last 30 days)
        from datetime import date, timedelta
        opts = ExportOptions(
            categories=[DataCategory.MOOD, DataCategory.SLEEP],
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
        )
        path = em.export(opts)

        # Wellness report
        report = em.generate_wellness_report(days=90)
    """

    def __init__(self, db: Any) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Date-column mapping per table
    # ------------------------------------------------------------------

    _DATE_COLUMN: dict[str, str] = {
        "mood_entries": "timestamp",
        "tasks": "created_at",
        "sleep_logs": "date",
        "medication_logs": "created_at",
        "journal_entries": "timestamp",
        "energy_readings": "timestamp",
        "achievements": "created_at",
        "breathing_sessions": "timestamp",
        "notifications": "created_at",
        "crisis_plans": "created_at",
        "settings": "updated_at",
    }

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def _fetch_table(
        self,
        table_name: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch rows from a table, optionally filtered by date range."""
        from core.database import TableName

        table_enum = TableName(table_name)
        date_col = self._DATE_COLUMN.get(table_name)

        where_parts: list[str] = []
        params: list[Any] = []

        if start_date and date_col:
            where_parts.append(f"{date_col} >= ?")
            params.append(start_date.isoformat())
        if end_date and date_col:
            where_parts.append(f"{date_col} <= ?")
            params.append((end_date + timedelta(days=1)).isoformat())

        where = " AND ".join(where_parts)
        result = self._db.query(table_enum, where=where, params=params)
        rows: list[dict[str, Any]] = result.rows
        return rows

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export(self, options: ExportOptions | None = None) -> Path:
        """Export data according to the supplied options.

        Returns the path to the exported file or directory.
        """
        if options is None:
            options = ExportOptions()

        output = options.effective_output_path
        output.parent.mkdir(parents=True, exist_ok=True)

        data = self._collect_data(options)

        if options.format == ExportFormat.JSON:
            return self._export_json(data, output, options)
        elif options.format == ExportFormat.CSV:
            return self._export_csv(data, output)
        elif options.format == ExportFormat.PDF:
            return self._export_pdf_text(data, output)
        else:
            raise ValueError(f"Unsupported format: {options.format}")

    def _collect_data(self, options: ExportOptions) -> dict[str, Any]:
        anonymizer = _Anonymizer() if options.anonymize else None
        payload: dict[str, Any] = {
            "exported_at": datetime.now().isoformat(),
            "anonymized": options.anonymize,
        }

        for category in options.categories:
            rows = self._fetch_table(
                category.value,
                start_date=options.start_date,
                end_date=options.end_date,
            )
            if anonymizer:
                rows = [anonymizer.anonymize_row(r) for r in rows]
            payload[category.value] = rows

        return payload

    def _export_json(
        self, data: dict[str, Any], output: Path, options: ExportOptions,
    ) -> Path:
        from core.database import CURRENT_SCHEMA_VERSION
        data["schema_version"] = CURRENT_SCHEMA_VERSION
        output.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        logger.info("Exported JSON to %s", output)
        return output

    def _export_csv(self, data: dict[str, Any], output: Path) -> Path:
        """Write one CSV file per table into a directory."""
        output.mkdir(parents=True, exist_ok=True)
        for key, rows in data.items():
            if not isinstance(rows, list) or not rows:
                continue
            csv_path = output / f"{key}.csv"
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            csv_path.write_text(buf.getvalue(), encoding="utf-8")
        logger.info("Exported CSV files to %s", output)
        return output

    def _export_pdf_text(self, data: dict[str, Any], output: Path) -> Path:
        """Generate a plain-text report formatted for printing / PDF conversion.

        If ``reportlab`` is available, a real PDF is created; otherwise
        a ``.txt`` file is written that can be converted externally.
        """
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("MINDFUL ORGANIZER DATA EXPORT")
        lines.append(f"Generated: {data.get('exported_at', '')}")
        if data.get("anonymized"):
            lines.append("** DATA HAS BEEN ANONYMIZED **")
        lines.append("=" * 60)
        lines.append("")

        for key, rows in data.items():
            if not isinstance(rows, list) or not rows:
                continue
            lines.append(f"--- {key.replace('_', ' ').title()} ({len(rows)} records) ---")
            lines.append("")
            for row in rows[:200]:  # cap for readability
                for k, v in row.items():
                    lines.append(f"  {k}: {v}")
                lines.append("")
            lines.append("")

        text = "\n".join(lines)

        # Attempt real PDF via reportlab
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas as rl_canvas

            pdf_output = output.with_suffix(".pdf")
            c = rl_canvas.Canvas(str(pdf_output), pagesize=letter)
            width, height = letter
            y = height - 40
            for line in lines:
                if y < 40:
                    c.showPage()
                    y = height - 40
                c.drawString(40, y, line[:100])
                y -= 14
            c.save()
            logger.info("Exported PDF to %s", pdf_output)
            return pdf_output
        except ImportError:
            txt_output = output.with_suffix(".txt")
            txt_output.write_text(text, encoding="utf-8")
            logger.info(
                "reportlab not installed; exported text report to %s", txt_output
            )
            return txt_output

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    def validate_import(self, file_path: Path) -> ImportValidation:
        """Validate a JSON import file without applying it.

        Checks structure, schema version compatibility, and record integrity.
        """
        validation = ImportValidation()

        if not file_path.exists():
            validation.errors.append(f"File not found: {file_path}")
            return validation

        try:
            raw = file_path.read_text(encoding="utf-8")
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            validation.errors.append(f"Invalid JSON: {exc}")
            return validation
        except OSError as exc:
            validation.errors.append(f"Cannot read file: {exc}")
            return validation

        if not isinstance(data, dict):
            validation.errors.append("Top-level JSON must be an object")
            return validation

        # Schema version
        validation.schema_version = data.get("schema_version")
        from core.database import CURRENT_SCHEMA_VERSION
        if validation.schema_version is not None and validation.schema_version > CURRENT_SCHEMA_VERSION:
                validation.errors.append(
                    f"Import schema version {validation.schema_version} is newer "
                    f"than current {CURRENT_SCHEMA_VERSION}"
                )

        valid_tables = {cat.value for cat in DataCategory}

        for key, rows in data.items():
            if key in ("exported_at", "schema_version", "anonymized"):
                continue
            if key not in valid_tables:
                validation.warnings.append(f"Unknown table '{key}' will be skipped")
                continue
            if not isinstance(rows, list):
                validation.errors.append(f"'{key}' must be a list")
                continue
            validation.record_counts[key] = len(rows)
            # Spot-check each row is a dict
            for i, row in enumerate(rows):
                if not isinstance(row, dict):
                    validation.errors.append(
                        f"'{key}' row {i} is not a dict"
                    )
                    break

        if data.get("anonymized"):
            validation.warnings.append(
                "This export was anonymized; some data has been redacted"
            )

        validation.is_valid = len(validation.errors) == 0
        return validation

    def import_from_json(
        self,
        file_path: Path,
        *,
        merge: bool = True,
        validate_first: bool = True,
    ) -> dict[str, int]:
        """Import data from a JSON backup file.

        Args:
            file_path: Path to the JSON file.
            merge: If True, inserts new rows alongside existing data.
                   If False, clears existing data in each imported table first.
            validate_first: Run validation before importing.

        Returns:
            Dict mapping table names to number of rows imported.
        """
        if validate_first:
            validation = self.validate_import(file_path)
            if not validation.is_valid:
                raise ValueError(
                    "Import validation failed:\n" + "\n".join(validation.errors)
                )

        data = json.loads(file_path.read_text(encoding="utf-8"))
        from core.database import TableName

        valid_tables = {cat.value for cat in DataCategory}
        counts: dict[str, int] = {}

        for key, rows in data.items():
            if key not in valid_tables or not isinstance(rows, list):
                continue

            try:
                table_enum = TableName(key)
            except ValueError:
                continue

            if not merge:
                self._db.execute(f"DELETE FROM {key}")

            imported = 0
            for row in rows:
                if not isinstance(row, dict):
                    continue
                # Strip the 'id' field so the database assigns new IDs
                clean = {k: v for k, v in row.items() if k != "id"}
                if not clean:
                    continue
                try:
                    self._db.insert(table_enum, **clean)
                    imported += 1
                except Exception as exc:
                    logger.warning("Skipping row in '%s': %s", key, exc)
            counts[key] = imported

        logger.info("Import complete: %s", counts)
        return counts

    # ------------------------------------------------------------------
    # Settings export / import
    # ------------------------------------------------------------------

    def export_settings(self, output_path: Path | None = None) -> Path:
        """Export all settings to a JSON file."""
        from core.database import TableName
        result = self._db.query(TableName.SETTINGS)
        settings = {row["key"]: row["value"] for row in result.rows}
        categories = {row["key"]: row.get("category", "general") for row in result.rows}
        payload = {
            "exported_at": datetime.now().isoformat(),
            "settings": settings,
            "categories": categories,
        }
        if output_path is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = DATA_DIR / "exports" / f"settings_{ts}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("Settings exported to %s", output_path)
        return output_path

    def import_settings(self, file_path: Path) -> int:
        """Import settings from a JSON file. Returns number of settings applied."""
        raw = json.loads(file_path.read_text(encoding="utf-8"))
        settings = raw.get("settings", {})
        categories = raw.get("categories", {})
        count = 0
        for key, value in settings.items():
            cat = categories.get(key, "general")
            self._db.set_setting(key, value, category=cat)
            count += 1
        logger.info("Imported %d settings from %s", count, file_path)
        return count

    # ------------------------------------------------------------------
    # wellness report
    # ------------------------------------------------------------------

    def generate_wellness_report(
        self,
        days: int = 90,
        anonymize: bool = False,
    ) -> list[WellnessReportSection]:
        """Generate a structured wellness report for personal reflection.

        The report summarizes mood trends, sleep patterns, medication
        adherence, and symptom correlations over the requested period.
        """
        end = date.today()
        start = end - timedelta(days=days)
        sections: list[WellnessReportSection] = []

        # -- Header --
        sections.append(WellnessReportSection(
            title="Report Overview",
            content=(
                f"Wellness summary for the period {start.isoformat()} to "
                f"{end.isoformat()} ({days} days)."
            ),
            data={"start_date": start.isoformat(), "end_date": end.isoformat()},
        ))

        # -- Mood trends --
        mood_rows = self._fetch_table("mood_entries", start, end)
        if mood_rows:
            scores = [r["mood_score"] for r in mood_rows if r.get("mood_score") is not None]
            anxiety = [r["anxiety_level"] for r in mood_rows if r.get("anxiety_level") is not None]
            mood_data: dict[str, Any] = {
                "total_entries": len(mood_rows),
            }
            if scores:
                mood_data["mean_mood"] = round(statistics.mean(scores), 2)
                mood_data["median_mood"] = round(statistics.median(scores), 2)
                mood_data["mood_range"] = [min(scores), max(scores)]
                if len(scores) >= 2:
                    mood_data["mood_stdev"] = round(statistics.stdev(scores), 2)
            if anxiety:
                mood_data["mean_anxiety"] = round(statistics.mean(anxiety), 2)

            summary_parts = [f"Total mood entries: {len(mood_rows)}."]
            if scores:
                summary_parts.append(
                    f"Average mood: {mood_data.get('mean_mood')}/10 "
                    f"(range {mood_data['mood_range'][0]}-{mood_data['mood_range'][1]})."
                )
            if anxiety:
                summary_parts.append(
                    f"Average anxiety: {mood_data['mean_anxiety']}/10."
                )

            sections.append(WellnessReportSection(
                title="Mood Trends",
                content=" ".join(summary_parts),
                data=mood_data,
            ))

        # -- Sleep patterns --
        sleep_rows = self._fetch_table("sleep_logs", start, end)
        if sleep_rows:
            durations = [
                r["duration_hours"] for r in sleep_rows
                if r.get("duration_hours") is not None
            ]
            qualities = [
                r["quality"] for r in sleep_rows
                if r.get("quality") is not None
            ]
            sleep_data: dict[str, Any] = {"total_entries": len(sleep_rows)}
            if durations:
                sleep_data["mean_duration_hours"] = round(statistics.mean(durations), 2)
                sleep_data["total_sleep_hours"] = round(sum(durations), 1)
            if qualities:
                sleep_data["mean_quality"] = round(statistics.mean(qualities), 2)

            parts = [f"Total sleep logs: {len(sleep_rows)}."]
            if durations:
                parts.append(f"Average duration: {sleep_data['mean_duration_hours']}h.")
            if qualities:
                parts.append(f"Average quality: {sleep_data['mean_quality']}/10.")

            sections.append(WellnessReportSection(
                title="Sleep Patterns",
                content=" ".join(parts),
                data=sleep_data,
            ))

        # -- Medication adherence --
        med_rows = self._fetch_table("medication_logs", start, end)
        if med_rows:
            statuses = [r.get("status", "pending") for r in med_rows]
            taken = statuses.count("taken")
            missed = statuses.count("missed")
            late = statuses.count("late")
            total = len(statuses)
            adherence_pct = round((taken / total) * 100, 1) if total else 0.0
            med_data: dict[str, Any] = {
                "total_logs": total,
                "taken": taken,
                "missed": missed,
                "late": late,
                "adherence_percent": adherence_pct,
            }

            # Group by medication
            by_med: dict[str, dict[str, int]] = {}
            for r in med_rows:
                name = r.get("medication_name", "Unknown")
                if anonymize:
                    name = _Anonymizer()._hash(name)
                by_med.setdefault(name, {"taken": 0, "missed": 0, "late": 0, "total": 0})
                by_med[name]["total"] += 1
                status = r.get("status", "pending")
                if status in by_med[name]:
                    by_med[name][status] += 1
            med_data["by_medication"] = by_med

            sections.append(WellnessReportSection(
                title="Medication Adherence",
                content=(
                    f"Overall adherence: {adherence_pct}% "
                    f"({taken} taken, {missed} missed, {late} late out of {total})."
                ),
                data=med_data,
            ))

        # -- Breathing / coping --
        breath_rows = self._fetch_table("breathing_sessions", start, end)
        if breath_rows:
            pre = [r["pre_anxiety"] for r in breath_rows if r.get("pre_anxiety") is not None]
            post = [r["post_anxiety"] for r in breath_rows if r.get("post_anxiety") is not None]
            breath_data: dict[str, Any] = {"total_sessions": len(breath_rows)}
            if pre and post and len(pre) == len(post):
                reductions = [p - q for p, q in zip(pre, post, strict=False)]
                breath_data["mean_anxiety_reduction"] = round(statistics.mean(reductions), 2)

            parts = [f"Total breathing sessions: {len(breath_rows)}."]
            if breath_data.get("mean_anxiety_reduction") is not None:
                parts.append(
                    f"Average anxiety reduction: "
                    f"{breath_data['mean_anxiety_reduction']} points."
                )
            sections.append(WellnessReportSection(
                title="Coping Activities (Breathing)",
                content=" ".join(parts),
                data=breath_data,
            ))

        # -- Energy --
        energy_rows = self._fetch_table("energy_readings", start, end)
        if energy_rows:
            levels = [
                r["energy_level"] for r in energy_rows
                if r.get("energy_level") is not None
            ]
            energy_data: dict[str, Any] = {"total_entries": len(energy_rows)}
            if levels:
                energy_data["mean_energy"] = round(statistics.mean(levels), 2)
                energy_data["energy_range"] = [min(levels), max(levels)]
            sections.append(WellnessReportSection(
                title="Energy Trends",
                content=(
                    f"Total energy readings: {len(energy_rows)}. "
                    f"Average energy: {energy_data.get('mean_energy', 'N/A')}/10."
                ),
                data=energy_data,
            ))

        # -- Disclaimer --
        sections.append(WellnessReportSection(
            title="Disclaimer",
            content=(
                "This report is auto-generated from self-reported data and is "
                "intended for personal reflection only. It "
                "does not constitute a diagnosis or medical advice."
            ),
        ))

        return sections

    def wellness_report_to_text(
        self, sections: list[WellnessReportSection],
    ) -> str:
        """Render wellness report sections to a plain-text string."""
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("MINDFUL ORGANIZER - WELLNESS REPORT")
        lines.append("=" * 60)
        lines.append("")
        for section in sections:
            lines.append(f"## {section.title}")
            lines.append(section.content)
            lines.append("")
        return "\n".join(lines)

    def export_wellness_report(
        self,
        days: int = 90,
        output_path: Path | None = None,
        anonymize: bool = False,
    ) -> Path:
        """Generate and save a wellness report to a file."""
        sections = self.generate_wellness_report(days=days, anonymize=anonymize)
        text = self.wellness_report_to_text(sections)
        if output_path is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = DATA_DIR / "exports" / f"wellness_report_{ts}.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
        logger.info("Wellness report saved to %s", output_path)
        return output_path
