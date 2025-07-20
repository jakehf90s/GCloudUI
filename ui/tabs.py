"""
UI Tab Components
This module contains all the individual tab components for the application.
"""

from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox, QGroupBox,
    QFormLayout, QMessageBox, QProgressBar, QSplitter, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from core.gcloudapi import GCloudAPI
from ui.workers import GCloudWorker


class BaseTab(QWidget):
    """Base class for all tabs"""
    error_occurred = pyqtSignal(str)
    
    def __init__(self, gcloud_api: GCloudAPI):
        super().__init__()
        self.gcloud_api = gcloud_api
        self.workers = []
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Initialize the UI - to be overridden by subclasses"""
        pass
    
    def setup_connections(self):
        """Setup signal connections - to be overridden by subclasses"""
        pass
    
    def cleanup_workers(self):
        """Clean up any running workers"""
        for worker in self.workers:
            if worker.isRunning():
                worker.terminate()
                worker.wait()


class ServicesTab(BaseTab):
    """Cloud Run Services tab"""
    
    def init_ui(self):
        """Initialize the services tab UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Cloud Run Services")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_services)
        header_layout.addWidget(refresh_btn)
        
        create_btn = QPushButton("Create New Service")
        create_btn.clicked.connect(self.create_service_dialog)
        header_layout.addWidget(create_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Services table
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(5)
        self.services_table.setHorizontalHeaderLabels([
            "Service Name", "Status", "URL", "Latest Revision", "Created"
        ])
        self.services_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.services_table)
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def refresh_services(self):
        """Refresh Cloud Run services"""
        worker = GCloudWorker("get_services", self.gcloud_api)
        worker.result_ready.connect(self.on_services_loaded)
        worker.error_occurred.connect(self.error_occurred.emit)
        self.workers.append(worker)
        worker.start()
    
    def on_services_loaded(self, result):
        """Handle services loaded result"""
        if result['success'] and result['type'] == 'services':
            services = result['data']
            self.services_table.setRowCount(len(services))
            
            for i, service in enumerate(services):
                self.services_table.setItem(i, 0, QTableWidgetItem(service['name'].split('/')[-1]))
                self.services_table.setItem(i, 1, QTableWidgetItem(service['status']))
                self.services_table.setItem(i, 2, QTableWidgetItem(service['url']))
                self.services_table.setItem(i, 3, QTableWidgetItem(service['revision']))
                self.services_table.setItem(i, 4, QTableWidgetItem(service['created']))
        else:
            self.error_occurred.emit(result.get('error', 'Unknown error'))
    
    def create_service_dialog(self):
        """Show dialog to create new service"""
        QMessageBox.information(
            self,
            "Create Service",
            "Service creation dialog would be implemented here."
        )


class BuildTab(BaseTab):
    """Cloud Build tab"""
    
    def init_ui(self):
        """Initialize the build tab UI"""
        layout = QVBoxLayout(self)
        
        # Build configuration
        config_group = QGroupBox("Build Configuration")
        config_layout = QFormLayout(config_group)
        
        self.build_source = QLineEdit()
        self.build_source.setPlaceholderText("gs://bucket/source.tar.gz")
        config_layout.addRow("Source:", self.build_source)
        
        self.build_image_name = QLineEdit()
        self.build_image_name.setPlaceholderText("gcr.io/project/image:tag")
        config_layout.addRow("Image Name:", self.build_image_name)
        
        self.build_bucket = QLineEdit()
        self.build_bucket.setPlaceholderText("your-build-bucket")
        config_layout.addRow("Build Bucket:", self.build_bucket)
        
        layout.addWidget(config_group)
        
        # Build actions
        actions_layout = QHBoxLayout()
        
        build_btn = QPushButton("Build Image")
        build_btn.clicked.connect(self.build_image)
        actions_layout.addWidget(build_btn)
        
        push_btn = QPushButton("Push Image")
        push_btn.clicked.connect(self.push_image)
        actions_layout.addWidget(push_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Build logs
        self.build_logs = QTextEdit()
        self.build_logs.setReadOnly(True)
        layout.addWidget(QLabel("Build Logs:"))
        layout.addWidget(self.build_logs)
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def build_image(self):
        """Build container image"""
        if not self.build_image_name.text():
            QMessageBox.warning(self, "Error", "Please enter an image name")
            return
        
        build_config = {
            'bucket': self.build_bucket.text(),
            'object': self.build_source.text(),
            'image_name': self.build_image_name.text()
        }
        
        worker = GCloudWorker("build_image", self.gcloud_api, build_config=build_config)
        worker.result_ready.connect(self.on_build_completed)
        worker.error_occurred.connect(self.error_occurred.emit)
        self.workers.append(worker)
        worker.start()
    
    def on_build_completed(self, result):
        """Handle build completion"""
        if result['success'] and result['type'] == 'build_started':
            self.build_logs.append(f"Build started: {result['data']['operation']}")
        else:
            self.error_occurred.emit(result.get('error', 'Unknown error'))
    
    def push_image(self):
        """Push image to registry"""
        if not self.build_image_name.text():
            QMessageBox.warning(self, "Error", "Please enter an image name")
            return
        
        worker = GCloudWorker("push_image", self.gcloud_api, image_name=self.build_image_name.text())
        worker.result_ready.connect(self.on_push_completed)
        worker.error_occurred.connect(self.error_occurred.emit)
        self.workers.append(worker)
        worker.start()
    
    def on_push_completed(self, result):
        """Handle push completion"""
        if result['success'] and result['type'] == 'push_completed':
            self.build_logs.append(result['data']['message'])
        else:
            self.error_occurred.emit(result.get('error', 'Unknown error'))


class ImagesTab(BaseTab):
    """Container Images tab"""
    
    def init_ui(self):
        """Initialize the images tab UI"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Container Images")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_images)
        header_layout.addWidget(refresh_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Images table
        self.images_table = QTableWidget()
        self.images_table.setColumnCount(3)
        self.images_table.setHorizontalHeaderLabels([
            "Repository Name", "Format", "Description"
        ])
        self.images_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.images_table)
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def refresh_images(self):
        """Refresh container images"""
        worker = GCloudWorker("get_images", self.gcloud_api)
        worker.result_ready.connect(self.on_images_loaded)
        worker.error_occurred.connect(self.error_occurred.emit)
        self.workers.append(worker)
        worker.start()
    
    def on_images_loaded(self, result):
        """Handle images loaded result"""
        if result['success'] and result['type'] == 'images':
            images = result['data']
            self.images_table.setRowCount(len(images))
            
            for i, image in enumerate(images):
                self.images_table.setItem(i, 0, QTableWidgetItem(image['name']))
                self.images_table.setItem(i, 1, QTableWidgetItem(image['format']))
                self.images_table.setItem(i, 2, QTableWidgetItem(image['description']))
        else:
            self.error_occurred.emit(result.get('error', 'Unknown error'))


class LogsTab(BaseTab):
    """Logs tab"""
    
    def init_ui(self):
        """Initialize the logs tab UI"""
        layout = QVBoxLayout(self)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter:"))
        self.logs_filter = QComboBox()
        self.logs_filter.addItems([
            "All logs",
            "Cloud Run",
            "Cloud Build",
            "Container Registry"
        ])
        filter_layout.addWidget(self.logs_filter)
        
        refresh_btn = QPushButton("Refresh Logs")
        refresh_btn.clicked.connect(self.refresh_logs)
        filter_layout.addWidget(refresh_btn)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Logs display
        self.logs_display = QTextEdit()
        self.logs_display.setReadOnly(True)
        layout.addWidget(self.logs_display)
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def refresh_logs(self):
        """Refresh logs"""
        filter_str = "resource.type=cloud_run_revision"  # Default filter
        worker = GCloudWorker("get_logs", self.gcloud_api, filter_str=filter_str)
        worker.result_ready.connect(self.on_logs_loaded)
        worker.error_occurred.connect(self.error_occurred.emit)
        self.workers.append(worker)
        worker.start()
    
    def on_logs_loaded(self, result):
        """Handle logs loaded result"""
        if result['success'] and result['type'] == 'logs':
            logs = result['data']
            
            log_text = ""
            for log in logs:
                log_text += f"[{log['timestamp']}] {log['severity']}: {log['text_payload']}\n"
            
            self.logs_display.setText(log_text)
        else:
            self.error_occurred.emit(result.get('error', 'Unknown error'))


class IAMTab(BaseTab):
    """IAM Management tab"""
    
    def init_ui(self):
        """Initialize the IAM tab UI"""
        layout = QVBoxLayout(self)
        
        # Split into two sections
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Service Accounts section
        sa_widget = QWidget()
        sa_layout = QVBoxLayout(sa_widget)
        
        sa_header = QHBoxLayout()
        sa_title = QLabel("Service Accounts")
        sa_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        sa_header.addWidget(sa_title)
        
        refresh_sa_btn = QPushButton("Refresh")
        refresh_sa_btn.clicked.connect(self.refresh_service_accounts)
        sa_header.addWidget(refresh_sa_btn)
        sa_header.addStretch()
        sa_layout.addLayout(sa_header)
        
        self.sa_table = QTableWidget()
        self.sa_table.setColumnCount(4)
        self.sa_table.setHorizontalHeaderLabels([
            "Name", "Email", "Display Name", "Description"
        ])
        sa_layout.addWidget(self.sa_table)
        
        # Permissions section
        perm_widget = QWidget()
        perm_layout = QVBoxLayout(perm_widget)
        
        perm_header = QHBoxLayout()
        perm_title = QLabel("IAM Permissions")
        perm_title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        perm_header.addWidget(perm_title)
        
        refresh_perm_btn = QPushButton("Refresh")
        refresh_perm_btn.clicked.connect(self.refresh_permissions)
        perm_header.addWidget(refresh_perm_btn)
        
        add_perm_btn = QPushButton("Add Permission")
        add_perm_btn.clicked.connect(self.add_permission_dialog)
        perm_header.addWidget(add_perm_btn)
        
        perm_header.addStretch()
        perm_layout.addLayout(perm_header)
        
        self.perm_tree = QTreeWidget()
        self.perm_tree.setHeaderLabels(["Role", "Members"])
        perm_layout.addWidget(self.perm_tree)
        
        # Add to splitter
        splitter.addWidget(sa_widget)
        splitter.addWidget(perm_widget)
        splitter.setSizes([400, 400])
        
        layout.addWidget(splitter)
    
    def setup_connections(self):
        """Setup signal connections"""
        pass
    
    def refresh_service_accounts(self):
        """Refresh service accounts"""
        worker = GCloudWorker("get_service_accounts", self.gcloud_api)
        worker.result_ready.connect(self.on_service_accounts_loaded)
        worker.error_occurred.connect(self.error_occurred.emit)
        self.workers.append(worker)
        worker.start()
    
    def on_service_accounts_loaded(self, result):
        """Handle service accounts loaded result"""
        if result['success'] and result['type'] == 'service_accounts':
            accounts = result['data']
            self.sa_table.setRowCount(len(accounts))
            
            for i, account in enumerate(accounts):
                self.sa_table.setItem(i, 0, QTableWidgetItem(account['name']))
                self.sa_table.setItem(i, 1, QTableWidgetItem(account['email']))
                self.sa_table.setItem(i, 2, QTableWidgetItem(account['display_name']))
                self.sa_table.setItem(i, 3, QTableWidgetItem(account['description']))
        else:
            self.error_occurred.emit(result.get('error', 'Unknown error'))
    
    def refresh_permissions(self):
        """Refresh IAM permissions"""
        worker = GCloudWorker("get_permissions", self.gcloud_api)
        worker.result_ready.connect(self.on_permissions_loaded)
        worker.error_occurred.connect(self.error_occurred.emit)
        self.workers.append(worker)
        worker.start()
    
    def on_permissions_loaded(self, result):
        """Handle permissions loaded result"""
        if result['success'] and result['type'] == 'permissions':
            permissions = result['data']
            self.perm_tree.clear()
            
            for perm in permissions:
                item = QTreeWidgetItem(self.perm_tree)
                item.setText(0, perm['role'])
                item.setText(1, ', '.join(perm['members']))
        else:
            self.error_occurred.emit(result.get('error', 'Unknown error'))
    
    def add_permission_dialog(self):
        """Show dialog to add permission"""
        QMessageBox.information(
            self,
            "Add Permission",
            "Permission addition dialog would be implemented here."
        ) 