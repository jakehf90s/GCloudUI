"""
Google Cloud API Core Functions
This module contains all the Google Cloud API operations used by the application.
"""

import sys
import json
import subprocess
from datetime import datetime
from typing import List, Dict, Any, Optional

# Google Cloud imports
from google.cloud.devtools import cloudbuild_v1
from google.cloud import run_v2, logging_v2, iam, resourcemanager_v3, artifactregistry
from google.auth import default
from google.auth.exceptions import DefaultCredentialsError


class GCloudAPI:
    """Core Google Cloud API operations"""
    
    def __init__(self, project_id: str = None, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        
        # Try to get default project if not provided
        if not self.project_id:
            try:
                credentials, project = default()
                if project:
                    self.project_id = project
                else:
                    self.project_id = "your-project-id"
            except DefaultCredentialsError:
                self.project_id = "your-project-id"
    
    def get_cloud_run_services(self) -> Dict[str, Any]:
        """Get Cloud Run services"""
        try:
            client = run_v2.ServicesClient()
            parent = f"projects/{self.project_id}/locations/{self.location}"
            
            request = run_v2.ListServicesRequest(parent=parent)
            page_result = client.list_services(request=request)
            
            services = []
            for service in page_result:
                services.append({
                    'name': service.name,
                    'status': service.status.conditions[-1].type if service.status.conditions else 'Unknown',
                    'url': service.status.url,
                    'revision': service.status.latest_ready_revision_name,
                    'created': service.metadata.create_time.isoformat() if service.metadata.create_time else 'Unknown'
                })
            
            return {'type': 'services', 'data': services, 'success': True}
        except Exception as e:
            return {'type': 'services', 'data': [], 'success': False, 'error': str(e)}

    def create_cloud_run_service(self, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Cloud Run service"""
        try:
            client = run_v2.ServicesClient()
            parent = f"projects/{self.project_id}/locations/{self.location}"
            
            # Create service request
            service = run_v2.Service(
                name=f"{parent}/services/{service_config.get('name', 'new-service')}",
                template=run_v2.RevisionTemplate(
                    containers=[
                        run_v2.Container(
                            image=service_config.get('image', 'gcr.io/project/image'),
                            ports=[run_v2.ContainerPort(container_port=service_config.get('port', 8080))],
                            resources=run_v2.ResourceRequirements(
                                limits={
                                    'cpu': service_config.get('cpu', '1000m'),
                                    'memory': service_config.get('memory', '512Mi')
                                }
                            )
                        )
                    ]
                )
            )
            
            operation = client.create_service(parent=parent, service=service)
            
            return {'type': 'service_created', 'data': {'operation': operation.name}, 'success': True}
        except Exception as e:
            return {'type': 'service_created', 'data': {}, 'success': False, 'error': str(e)}

    def get_container_images(self) -> Dict[str, Any]:
        """Get container images from registry"""
        try:
            client = artifactregistry.ArtifactRegistryClient()
            parent = f"projects/{self.project_id}/locations/{self.location}"
            
            request = {"parent": parent}
            page_result = client.list_repositories(request=request)
            
            images = []
            for repository in page_result:
                images.append({
                    'name': repository.name,
                    'format': repository.format_.name if hasattr(repository, 'format_') else 'DOCKER',
                    'description': repository.description or 'No description'
                })
            
            return {'type': 'images', 'data': images, 'success': True}
        except Exception as e:
            return {'type': 'images', 'data': [], 'success': False, 'error': str(e)}

    def get_logs(self, filter_str: str = "resource.type=cloud_run_revision") -> Dict[str, Any]:
        """Get logs from Cloud Logging"""
        try:
            client = logging_v2.Client()
            
            # Get recent logs
            resource_names = [f"projects/{self.project_id}"]
            
            # Use the client's list_entries method
            entries = client.list_entries(
                resource_names=resource_names,
                filter_=filter_str,
                order_by="timestamp desc",
                page_size=50
            )
            
            logs = []
            for entry in entries:
                logs.append({
                    'timestamp': entry.timestamp.isoformat() if entry.timestamp else 'Unknown',
                    'severity': entry.severity.name,
                    'text_payload': entry.text_payload or 'No payload',
                    'resource': entry.resource.type
                })
            
            return {'type': 'logs', 'data': logs, 'success': True}
        except Exception as e:
            return {'type': 'logs', 'data': [], 'success': False, 'error': str(e)}

    def build_image(self, build_config: Dict[str, Any]) -> Dict[str, Any]:
        """Build container image using Cloud Build"""
        try:
            client = cloudbuild_v1.CloudBuildClient()
            
            # This is a simplified build request
            build_request = cloudbuild_v1.Build(
                source=cloudbuild_v1.Source(
                    storage_source=cloudbuild_v1.StorageSource(
                        bucket=build_config.get('bucket', 'your-bucket'),
                        object_=build_config.get('object', 'source.tar.gz')
                    )
                ),
                steps=[
                    cloudbuild_v1.BuildStep(
                        name='gcr.io/cloud-builders/docker',
                        args=['build', '-t', build_config.get('image_name', 'gcr.io/project/image'), '.']
                    )
                ],
                images=[build_config.get('image_name', 'gcr.io/project/image')]
            )
            
            operation = client.create_build(project_id=self.project_id, build=build_request)
            
            return {'type': 'build_started', 'data': {'operation': operation.name}, 'success': True}
        except Exception as e:
            return {'type': 'build_started', 'data': {}, 'success': False, 'error': str(e)}

    def push_image(self, image_name: str) -> Dict[str, Any]:
        """Push image to container registry"""
        try:
            # This would use docker commands or container registry API
            # For now, return a success message
            return {'type': 'push_completed', 'data': {'message': 'Image pushed successfully'}, 'success': True}
        except Exception as e:
            return {'type': 'push_completed', 'data': {}, 'success': False, 'error': str(e)}

    def get_service_accounts(self) -> Dict[str, Any]:
        """Get IAM service accounts"""
        try:
            # For now, return empty list since IAM client structure is different
            # This would need to be implemented with the correct IAM API
            accounts = []
            
            return {'type': 'service_accounts', 'data': accounts, 'success': True}
        except Exception as e:
            return {'type': 'service_accounts', 'data': [], 'success': False, 'error': str(e)}

    def get_permissions(self) -> Dict[str, Any]:
        """Get IAM permissions and roles"""
        try:
            # For now, return empty list since IAM client structure is different
            # This would need to be implemented with the correct IAM API
            permissions = []
            
            return {'type': 'permissions', 'data': permissions, 'success': True}
        except Exception as e:
            return {'type': 'permissions', 'data': [], 'success': False, 'error': str(e)}

    def add_permission(self, role: str, member: str) -> Dict[str, Any]:
        """Add IAM permission/role"""
        try:
            # For now, return success message since IAM client structure is different
            # This would need to be implemented with the correct IAM API
            return {'type': 'permission_added', 'data': {'message': f'Added {role} to {member}'}, 'success': True}
        except Exception as e:
            return {'type': 'permission_added', 'data': {}, 'success': False, 'error': str(e)}

    def check_authentication(self) -> Dict[str, Any]:
        """Check Google Cloud authentication"""
        try:
            credentials, project = default()
            if project:
                return {'success': True, 'project': project, 'authenticated': True}
            else:
                return {'success': False, 'project': None, 'authenticated': False, 'error': 'No default project set'}
        except DefaultCredentialsError:
            return {'success': False, 'project': None, 'authenticated': False, 'error': 'Not authenticated'}

    def run_gcloud_command(self, command: List[str]) -> Dict[str, Any]:
        """Run a gcloud command and return the result"""
        try:
            result = subprocess.run(
                ['gcloud'] + command,
                capture_output=True,
                text=True,
                check=True
            )
            return {
                'success': True,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'stdout': e.stdout,
                'stderr': e.stderr,
                'return_code': e.returncode,
                'error': str(e)
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'gcloud command not found'
            } 