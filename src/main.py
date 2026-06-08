#!/usr/bin/env python3
"""
Hearth — A desktop that adapts to your psychology.

The Hearth Project — psychological operating-system layer.

A desktop application that adapts to your mental health needs,
helping you stay organized while prioritizing your well-being.

All data is stored locally on your device. No cloud sync. No telemetry.
"""

import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Ensure src/ is on the path
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


def setup_logging(data_dir: Path) -> None:
    """Configure logging with rotation to file and console."""
    log_dir = data_dir / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)

    file_handler = RotatingFileHandler(
        log_dir / "mindful_organizer.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB per file
        backupCount=5,  # keep 5 archived files → 30 MB cap
        encoding="utf-8",
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            file_handler,
            logging.StreamHandler(sys.stdout),
        ],
    )
    # Suppress noisy third-party loggers
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)


def get_data_dir() -> Path:
    """Get the canonical platform-appropriate data directory.

    Delegates to :mod:`core.paths`, which also performs the legacy
    ``.mindful_optimizer`` -> ``.mindful_organizer`` rename, so the entry point,
    the database layer, and the GUI all resolve to the same location.
    """
    from core.paths import get_data_dir as _canonical

    return _canonical()


def configure_high_dpi() -> None:
    """Configure high-DPI scaling before QApplication creation."""
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    if sys.platform == "win32":
        os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")


def show_error_dialog(title: str, message: str, detail: str = "") -> None:
    """Show a platform-native error dialog."""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        if detail:
            msg.setDetailedText(detail)
        msg.exec()
    except Exception:
        print(f"ERROR: {title}\n{message}\n{detail}", file=sys.stderr)


def check_single_instance(data_dir: Path) -> bool:
    """Ensure only one instance of the app runs at a time."""
    lock_file = data_dir / ".lock"
    if sys.platform == "win32":
        try:
            if lock_file.exists():
                lock_file.unlink()
            # Create lock file
            fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return True
        except FileExistsError:
            return False
        except OSError:
            return True
    else:
        try:
            import fcntl

            lock_fd = open(lock_file, "w")  # noqa: SIM115
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_fd.write(str(os.getpid()))
            lock_fd.flush()
            # Keep fd open for lock duration
            globals()["_lock_fd"] = lock_fd
            return True
        except OSError:
            return False
        except ImportError:
            return True


def cleanup_lock(data_dir: Path) -> None:
    """Remove the lock file on exit."""
    lock_file = data_dir / ".lock"
    try:
        if lock_file.exists():
            lock_file.unlink()
    except OSError:
        pass


def run_first_launch_migration(data_dir: Path) -> None:
    """Migrate legacy JSON wellness data to SQLite on first launch.

    Runs at most once per install — a `.migration_complete` marker is written
    when finished. Safe to run on fresh installs (no JSON files = no-op).
    """
    marker = data_dir / ".migration_complete"
    if marker.exists():
        return

    logger = logging.getLogger("mindful_organizer.migration")
    legacy_files = list(data_dir.glob("*.json"))
    if not any(
        f.name
        in {
            "tasks.json",
            "mood_data.json",
            "energy_data.json",
            "sleep_data.json",
            "medication_data.json",
            "journal_entries.json",
            "breathing_sessions.json",
        }
        for f in legacy_files
    ):
        marker.touch()
        return

    try:
        from core.migration_manager import MigrationManager

        report = MigrationManager(data_dir=data_dir).migrate_all()
        if report.all_success:
            logger.info(
                "First-launch migration complete: %d records moved to SQLite",
                report.total_records,
            )
            marker.touch()
        else:
            failed = [r.module for r in report.results if not r.success]
            logger.error("Migration failed for: %s", failed)
    except Exception:
        logger.exception("First-launch migration crashed; will retry next launch")


def main() -> int:
    """Application entry point."""
    if any(arg in {"-h", "--help"} for arg in sys.argv[1:]):
        print(
            "usage: mindful-organizer [--help]\n\n"
            "Hearth desktop application.\n\n"
            "options:\n"
            "  -h, --help  show this help message and exit"
        )
        return 0

    data_dir = get_data_dir()
    setup_logging(data_dir)
    logger = logging.getLogger("mindful_organizer")
    logger.info("Starting Hearth")
    run_first_launch_migration(data_dir)

    # Single instance check
    if not check_single_instance(data_dir):
        show_error_dialog(
            "Already Running", "Hearth is already running.\n\nCheck your taskbar or system tray."
        )
        return 1

    try:
        configure_high_dpi()

        from PyQt6.QtGui import QFont, QFontDatabase
        from PyQt6.QtWidgets import QApplication

        from app_metadata import APP_NAME, APP_VERSION, ORGANIZATION_NAME

        app = QApplication(sys.argv)
        app.setApplicationName(APP_NAME)
        app.setApplicationVersion(APP_VERSION)
        app.setOrganizationName(ORGANIZATION_NAME)

        # Set default font — probe availability to avoid Qt font-alias penalty.
        def _first_available(stack: list[str], size: int) -> QFont:
            available = set(QFontDatabase.families())
            for fam in stack:
                if fam in available:
                    return QFont(fam, size)
            return QFont(stack[-1], size)

        if sys.platform == "win32":
            app.setFont(_first_available(["Segoe UI", "Helvetica Neue", "Arial"], 10))
        elif sys.platform == "darwin":
            app.setFont(
                _first_available(
                    ["SF Pro Text", "SF Pro", ".AppleSystemUIFont", "Helvetica Neue", "Arial"],
                    12,
                )
            )
        else:
            app.setFont(_first_available(["Sans", "DejaVu Sans", "Liberation Sans", "Arial"], 10))

        # Set app icon if available
        icon_path = src_dir.parent / "windows_store" / "assets" / "app_icon.png"
        if icon_path.exists():
            from PyQt6.QtGui import QIcon

            app.setWindowIcon(QIcon(str(icon_path)))

        # Create and show the main window
        from gui.main_window import AdaptiveMainWindow

        window = AdaptiveMainWindow()
        window.show()

        logger.info("Application window displayed")
        result = app.exec()

        # Cleanup
        cleanup_lock(data_dir)
        logger.info("Application closed normally")
        return result

    except ImportError as e:
        error_msg = f"Missing dependency: {e}\n\nPlease install requirements:\n  pip install -r requirements.txt"
        logger.error(error_msg)
        show_error_dialog("Missing Dependency", error_msg)
        cleanup_lock(data_dir)
        return 1

    except Exception as e:
        error_detail = traceback.format_exc()
        logger.critical(f"Unhandled exception: {e}\n{error_detail}")
        show_error_dialog(
            "Unexpected Error",
            f"Hearth encountered an error:\n\n{e}",
            error_detail,
        )
        cleanup_lock(data_dir)
        return 1


if __name__ == "__main__":
    sys.exit(main())
