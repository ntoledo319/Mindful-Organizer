#!/usr/bin/env python3
"""
Mindful Organizer - Mental Health-Aware Productivity Application

A desktop application that adapts to your mental health needs,
helping you stay organized while prioritizing your well-being.

All data is stored locally on your device. No cloud sync. No telemetry.
"""
import sys
import os
import logging
import traceback
from pathlib import Path

# Ensure src/ is on the path
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


def setup_logging(data_dir: Path) -> None:
    """Configure logging to file and console."""
    log_dir = data_dir / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "mindful_organizer.log", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    # Suppress noisy third-party loggers
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)


def get_data_dir() -> Path:
    """Get platform-appropriate data directory."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path.home()
    data_dir = base / ".mindful_optimizer"
    data_dir.mkdir(exist_ok=True, parents=True)
    return data_dir


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
            lock_fd = open(lock_file, "w")
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_fd.write(str(os.getpid()))
            lock_fd.flush()
            # Keep fd open for lock duration
            globals()["_lock_fd"] = lock_fd
            return True
        except (IOError, OSError):
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


def main() -> int:
    """Application entry point."""
    data_dir = get_data_dir()
    setup_logging(data_dir)
    logger = logging.getLogger("mindful_organizer")
    logger.info("Starting Mindful Organizer")

    # Single instance check
    if not check_single_instance(data_dir):
        show_error_dialog(
            "Already Running",
            "Mindful Organizer is already running.\n\n"
            "Check your taskbar or system tray."
        )
        return 1

    try:
        configure_high_dpi()

        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QFont

        app = QApplication(sys.argv)
        app.setApplicationName("Mindful Organizer")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Mindful Organizer")

        # Set default font
        if sys.platform == "win32":
            app.setFont(QFont("Segoe UI", 10))
        elif sys.platform == "darwin":
            app.setFont(QFont("SF Pro Text", 12))
        else:
            app.setFont(QFont("Sans", 10))

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
            f"Mindful Organizer encountered an error:\n\n{e}",
            error_detail,
        )
        cleanup_lock(data_dir)
        return 1


if __name__ == "__main__":
    sys.exit(main())
