"""
Main Window UI Component
This module contains the main application window with tabbed interface.
"""

import sys
from typing import List, Dict, Any, Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton, QLabel,
    QTextEdit, QLineEdit, QComboBox, QGroupBox, QFormLayout, QMessageBox,
    QProgressBar, QSplitter, QListWidget, QListWidgetItem, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QPixmap

from core.gcloudapi import GCloudAPI
from ui.workers import GCloudWorker
from ui.tabs import (
    ServicesTab,
    BuildTab,
    ImagesTab,
    LogsTab,
    IAMTab
)


class GCloudAccessApp(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.gcloud_api = GCloudAPI()
        self.workers = []
        
        self.init_ui()
        self.setup_connections()
        
        # Check authentication
        self.check_auth()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Google Cloud Access Tool")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_tabs()
        
        # Status bar
        self.statusBar().showMessage("Ready")

    def create_tabs(self):
        """Create all the application tabs"""
        # Services tab
        self.services_tab = ServicesTab(self.gcloud_api)
        self.tab_widget.addTab(self.services_tab, "Cloud Run Services")
        
        # Build tab
        self.build_tab = BuildTab(self.gcloud_api)
        self.tab_widget.addTab(self.build_tab, "Cloud Build")
        
        # Images tab
        self.images_tab = ImagesTab(self.gcloud_api)
        self.tab_widget.addTab(self.images_tab, "Container Images")
        
        # Logs tab
        self.logs_tab = LogsTab(self.gcloud_api)
        self.tab_widget.addTab(self.logs_tab, "Logs")
        
        # IAM tab
        self.iam_tab = IAMTab(self.gcloud_api)
        self.tab_widget.addTab(self.iam_tab, "IAM Management")

    def setup_connections(self):
        """Setup signal connections between components"""
        # Connect tab signals to main window handlers
        self.services_tab.error_occurred.connect(self.on_error)
        self.build_tab.error_occurred.connect(self.on_error)
        self.images_tab.error_occurred.connect(self.on_error)
        self.logs_tab.error_occurred.connect(self.on_error)
        self.iam_tab.error_occurred.connect(self.on_error)

    def check_auth(self):
        """Check Google Cloud authentication"""
        auth_result = self.gcloud_api.check_authentication()
        
        if auth_result['success'] and auth_result['authenticated']:
            self.statusBar().showMessage(f"Authenticated with project: {auth_result['project']}")
        else:
            QMessageBox.warning(
                self,
                "Authentication Error",
                f"Please run 'gcloud auth application-default login' to authenticate.\nError: {auth_result.get('error', 'Unknown error')}"
            )

    def on_error(self, error_message: str):
        """Handle errors from workers and tabs"""
        QMessageBox.critical(self, "Error", f"Operation failed: {error_message}")
        self.statusBar().showMessage("Operation failed")

    def closeEvent(self, event):
        """Handle application close event"""
        # Clean up any running workers
        for worker in self.workers:
            if worker.isRunning():
                worker.terminate()
                worker.wait()
        
        event.accept() 