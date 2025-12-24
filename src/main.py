#!/usr/bin/env python3

import sys
import os
from PyQt6.QtWidgets import QApplication
from gui.main_window import AdaptiveMainWindow

def main():
    # Initialize the application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = AdaptiveMainWindow()
    window.show()
    
    # Start the event loop
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
