"""
Google Cloud Access Tool - Main Application
This is the main entry point for the application.
"""

import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import GCloudAccessApp


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Google Cloud Access Tool")
    
    window = GCloudAccessApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 