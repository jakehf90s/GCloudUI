"""
Background Workers for Google Cloud Operations
This module contains QThread-based workers for non-blocking API operations.
"""

from typing import Dict, Any, Optional
from PyQt6.QtCore import QThread, pyqtSignal

from core.gcloudapi import GCloudAPI


class GCloudWorker(QThread):
    """Background worker for Google Cloud operations"""
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)

    def __init__(self, operation: str, gcloud_api: GCloudAPI, **kwargs):
        super().__init__()
        self.operation = operation
        self.gcloud_api = gcloud_api
        self.kwargs = kwargs

    def run(self):
        """Execute the specified operation"""
        try:
            if self.operation == "get_services":
                result = self.gcloud_api.get_cloud_run_services()
            elif self.operation == "create_service":
                result = self.gcloud_api.create_cloud_run_service(self.kwargs.get('service_config', {}))
            elif self.operation == "get_images":
                result = self.gcloud_api.get_container_images()
            elif self.operation == "get_logs":
                result = self.gcloud_api.get_logs(self.kwargs.get('filter_str', "resource.type=cloud_run_revision"))
            elif self.operation == "build_image":
                result = self.gcloud_api.build_image(self.kwargs.get('build_config', {}))
            elif self.operation == "push_image":
                result = self.gcloud_api.push_image(self.kwargs.get('image_name', ''))
            elif self.operation == "get_service_accounts":
                result = self.gcloud_api.get_service_accounts()
            elif self.operation == "get_permissions":
                result = self.gcloud_api.get_permissions()
            elif self.operation == "add_permission":
                result = self.gcloud_api.add_permission(
                    self.kwargs.get('role', 'roles/viewer'),
                    self.kwargs.get('member', 'user:example@example.com')
                )
            else:
                raise ValueError(f"Unknown operation: {self.operation}")
            
            self.result_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e)) 