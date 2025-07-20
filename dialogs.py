"""
Dialog classes for Google Cloud Access Tool
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QLabel, QComboBox, QSpinBox, QTextEdit, QGroupBox,
    QCheckBox, QMessageBox, QFileDialog, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from config import COMMON_ROLES, MEMBER_TYPES, SERVICE_TEMPLATES


class CreateServiceDialog(QDialog):
    """Dialog for creating a new Cloud Run service"""
    
    def __init__(self, parent=None, project_id="your-project-id"):
        super().__init__(parent)
        self.project_id = project_id
        self.result_data = {}
        
        self.setWindowTitle("Create Cloud Run Service")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Service basic info
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        self.service_name = QLineEdit()
        self.service_name.setPlaceholderText("my-service")
        basic_layout.addRow("Service Name:", self.service_name)
        
        self.image_url = QLineEdit()
        self.image_url.setPlaceholderText(f"gcr.io/{self.project_id}/my-service:latest")
        basic_layout.addRow("Container Image:", self.image_url)
        
        self.port = QSpinBox()
        self.port.setRange(1, 65535)
        self.port.setValue(8080)
        basic_layout.addRow("Port:", self.port)
        
        layout.addWidget(basic_group)
        
        # Resource configuration
        resource_group = QGroupBox("Resource Configuration")
        resource_layout = QFormLayout(resource_group)
        
        self.cpu = QComboBox()
        self.cpu.addItems(["1000m", "2000m", "4000m", "8000m"])
        resource_layout.addRow("CPU:", self.cpu)
        
        self.memory = QComboBox()
        self.memory.addItems(["512Mi", "1Gi", "2Gi", "4Gi", "8Gi"])
        resource_layout.addRow("Memory:", self.memory)
        
        self.max_instances = QSpinBox()
        self.max_instances.setRange(1, 1000)
        self.max_instances.setValue(10)
        resource_layout.addRow("Max Instances:", self.max_instances)
        
        self.min_instances = QSpinBox()
        self.min_instances.setRange(0, 100)
        self.min_instances.setValue(0)
        resource_layout.addRow("Min Instances:", self.min_instances)
        
        layout.addWidget(resource_group)
        
        # Environment variables
        env_group = QGroupBox("Environment Variables")
        env_layout = QVBoxLayout(env_group)
        
        self.env_vars = QTextEdit()
        self.env_vars.setPlaceholderText("KEY1=value1\nKEY2=value2")
        self.env_vars.setMaximumHeight(100)
        env_layout.addWidget(self.env_vars)
        
        layout.addWidget(env_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("Create Service")
        create_btn.clicked.connect(self.accept)
        create_btn.setDefault(True)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
        
    def get_service_config(self):
        """Get the service configuration from the dialog"""
        env_vars_text = self.env_vars.toPlainText()
        env_vars = {}
        
        if env_vars_text.strip():
            for line in env_vars_text.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        
        return {
            'name': self.service_name.text(),
            'image': self.image_url.text(),
            'port': self.port.value(),
            'cpu': self.cpu.currentText(),
            'memory': self.memory.currentText(),
            'max_instances': self.max_instances.value(),
            'min_instances': self.min_instances.value(),
            'env_vars': env_vars
        }


class AddPermissionDialog(QDialog):
    """Dialog for adding IAM permissions"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.result_data = {}
        
        self.setWindowTitle("Add IAM Permission")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Role selection
        role_layout = QFormLayout()
        
        self.role_combo = QComboBox()
        for display_name, role in COMMON_ROLES.items():
            self.role_combo.addItem(display_name, role)
        role_layout.addRow("Role:", self.role_combo)
        
        layout.addLayout(role_layout)
        
        # Member selection
        member_layout = QFormLayout()
        
        self.member_type = QComboBox()
        for display_name, prefix in MEMBER_TYPES.items():
            self.member_type.addItem(display_name, prefix)
        member_layout.addRow("Member Type:", self.member_type)
        
        self.member_value = QLineEdit()
        self.member_value.setPlaceholderText("example@example.com")
        member_layout.addRow("Member Value:", self.member_value)
        
        layout.addLayout(member_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        add_btn = QPushButton("Add Permission")
        add_btn.clicked.connect(self.accept)
        add_btn.setDefault(True)
        button_layout.addWidget(add_btn)
        
        layout.addLayout(button_layout)
        
    def get_permission_data(self):
        """Get the permission data from the dialog"""
        role = self.role_combo.currentData()
        member_type = self.member_type.currentData()
        member_value = self.member_value.text()
        
        return {
            'role': role,
            'member': f"{member_type}{member_value}"
        }


class BuildConfigDialog(QDialog):
    """Dialog for configuring Cloud Build"""
    
    def __init__(self, parent=None, project_id="your-project-id"):
        super().__init__(parent)
        self.project_id = project_id
        self.result_data = {}
        
        self.setWindowTitle("Configure Cloud Build")
        self.setModal(True)
        self.setMinimumWidth(600)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Source configuration
        source_group = QGroupBox("Source Configuration")
        source_layout = QFormLayout(source_group)
        
        self.source_type = QComboBox()
        self.source_type.addItems(["Cloud Storage", "Git Repository", "Local Directory"])
        source_layout.addRow("Source Type:", self.source_type)
        
        self.source_path = QLineEdit()
        self.source_path.setPlaceholderText("gs://bucket/source.tar.gz")
        source_layout.addRow("Source Path:", self.source_path)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_source)
        source_layout.addRow("", browse_btn)
        
        layout.addWidget(source_group)
        
        # Build configuration
        build_group = QGroupBox("Build Configuration")
        build_layout = QFormLayout(build_group)
        
        self.image_name = QLineEdit()
        self.image_name.setPlaceholderText(f"gcr.io/{self.project_id}/my-image:latest")
        build_layout.addRow("Image Name:", self.image_name)
        
        self.build_config = QComboBox()
        self.build_config.addItems(["Docker", "Multi-stage", "With Tests"])
        build_layout.addRow("Build Type:", self.build_config)
        
        self.timeout = QSpinBox()
        self.timeout.setRange(1, 720)
        self.timeout.setValue(10)
        self.timeout.setSuffix(" minutes")
        build_layout.addRow("Timeout:", self.timeout)
        
        layout.addWidget(build_group)
        
        # Advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QFormLayout(advanced_group)
        
        self.machine_type = QComboBox()
        self.machine_type.addItems(["E2_HIGHCPU_8", "E2_HIGHCPU_32", "E2_HIGHMEM_8", "E2_HIGHMEM_32"])
        advanced_layout.addRow("Machine Type:", self.machine_type)
        
        self.substitutions = QTextEdit()
        self.substitutions.setPlaceholderText("_VERSION=1.0.0\n_ENVIRONMENT=production")
        self.substitutions.setMaximumHeight(80)
        advanced_layout.addRow("Substitutions:", self.substitutions)
        
        layout.addWidget(advanced_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        build_btn = QPushButton("Start Build")
        build_btn.clicked.connect(self.accept)
        build_btn.setDefault(True)
        button_layout.addWidget(build_btn)
        
        layout.addLayout(button_layout)
        
    def browse_source(self):
        """Browse for local source directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if directory:
            self.source_path.setText(directory)
            
    def get_build_config(self):
        """Get the build configuration from the dialog"""
        substitutions_text = self.substitutions.toPlainText()
        substitutions = {}
        
        if substitutions_text.strip():
            for line in substitutions_text.split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    substitutions[key.strip()] = value.strip()
        
        return {
            'source_type': self.source_type.currentText(),
            'source_path': self.source_path.text(),
            'image_name': self.image_name.text(),
            'build_type': self.build_config.currentText(),
            'timeout': self.timeout.value(),
            'machine_type': self.machine_type.currentText(),
            'substitutions': substitutions
        }


class ProjectSettingsDialog(QDialog):
    """Dialog for project settings and configuration"""
    
    def __init__(self, parent=None, current_config=None):
        super().__init__(parent)
        self.current_config = current_config or {}
        
        self.setWindowTitle("Project Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Project settings
        project_group = QGroupBox("Project Configuration")
        project_layout = QFormLayout(project_group)
        
        self.project_id = QLineEdit(self.current_config.get('project_id', ''))
        project_layout.addRow("Project ID:", self.project_id)
        
        self.location = QLineEdit(self.current_config.get('location', 'us-central1'))
        project_layout.addRow("Default Location:", self.location)
        
        self.build_bucket = QLineEdit(self.current_config.get('build_bucket', ''))
        project_layout.addRow("Build Bucket:", self.build_bucket)
        
        layout.addWidget(project_group)
        
        # Application settings
        app_group = QGroupBox("Application Settings")
        app_layout = QFormLayout(app_group)
        
        self.log_level = QComboBox()
        self.log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        self.log_level.setCurrentText(self.current_config.get('log_level', 'INFO'))
        app_layout.addRow("Log Level:", self.log_level)
        
        self.max_logs = QSpinBox()
        self.max_logs.setRange(10, 1000)
        self.max_logs.setValue(self.current_config.get('max_log_entries', 100))
        app_layout.addRow("Max Log Entries:", self.max_logs)
        
        self.refresh_interval = QSpinBox()
        self.refresh_interval.setRange(5, 300)
        self.refresh_interval.setValue(self.current_config.get('refresh_interval', 30))
        self.refresh_interval.setSuffix(" seconds")
        app_layout.addRow("Refresh Interval:", self.refresh_interval)
        
        layout.addWidget(app_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.accept)
        save_btn.setDefault(True)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
    def get_settings(self):
        """Get the settings from the dialog"""
        return {
            'project_id': self.project_id.text(),
            'location': self.location.text(),
            'build_bucket': self.build_bucket.text(),
            'log_level': self.log_level.currentText(),
            'max_log_entries': self.max_logs.value(),
            'refresh_interval': self.refresh_interval.value()
        } 