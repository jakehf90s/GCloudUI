"""
Configuration file for Google Cloud Access Tool
"""

import os
from typing import Dict, Any

# Default configuration
DEFAULT_CONFIG = {
    'project_id': os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id'),
    'location': 'us-central1',
    'build_bucket': 'your-build-bucket',
    'container_registry': 'gcr.io',
    'default_region': 'us-central1',
    'log_level': 'INFO',
    'max_log_entries': 100,
    'refresh_interval': 30,  # seconds
}

# Common IAM roles for quick access
COMMON_ROLES = {
    'Viewer': 'roles/viewer',
    'Editor': 'roles/editor',
    'Owner': 'roles/owner',
    'Cloud Run Admin': 'roles/run.admin',
    'Cloud Build Editor': 'roles/cloudbuild.builds.editor',
    'Container Registry Admin': 'roles/storage.admin',
    'Logs Viewer': 'roles/logging.viewer',
    'Service Account User': 'roles/iam.serviceAccountUser',
}

# Common member types
MEMBER_TYPES = {
    'User': 'user:',
    'Service Account': 'serviceAccount:',
    'Group': 'group:',
    'Domain': 'domain:',
}

# Cloud Run service templates
SERVICE_TEMPLATES = {
    'basic': {
        'name': 'my-service',
        'image': 'gcr.io/PROJECT_ID/my-service:latest',
        'port': 8080,
        'cpu': '1000m',
        'memory': '512Mi',
        'max_instances': 10,
        'min_instances': 0,
    },
    'high_performance': {
        'name': 'my-service',
        'image': 'gcr.io/PROJECT_ID/my-service:latest',
        'port': 8080,
        'cpu': '2000m',
        'memory': '2Gi',
        'max_instances': 100,
        'min_instances': 1,
    },
    'cost_optimized': {
        'name': 'my-service',
        'image': 'gcr.io/PROJECT_ID/my-service:latest',
        'port': 8080,
        'cpu': '500m',
        'memory': '256Mi',
        'max_instances': 5,
        'min_instances': 0,
    }
}

# Build configurations
BUILD_CONFIGS = {
    'docker': {
        'steps': [
            {
                'name': 'gcr.io/cloud-builders/docker',
                'args': ['build', '-t', 'IMAGE_NAME', '.']
            }
        ]
    },
    'multi_stage': {
        'steps': [
            {
                'name': 'gcr.io/cloud-builders/docker',
                'args': ['build', '-t', 'IMAGE_NAME', '-f', 'Dockerfile.multi', '.']
            }
        ]
    },
    'with_tests': {
        'steps': [
            {
                'name': 'gcr.io/cloud-builders/docker',
                'args': ['build', '-t', 'IMAGE_NAME', '.']
            },
            {
                'name': 'gcr.io/cloud-builders/docker',
                'args': ['run', 'IMAGE_NAME', 'npm', 'test']
            }
        ]
    }
}

def get_config() -> Dict[str, Any]:
    """Get current configuration"""
    return DEFAULT_CONFIG.copy()

def update_config(updates: Dict[str, Any]) -> None:
    """Update configuration with new values"""
    DEFAULT_CONFIG.update(updates)

def get_project_id() -> str:
    """Get current project ID"""
    return DEFAULT_CONFIG['project_id']

def set_project_id(project_id: str) -> None:
    """Set project ID"""
    DEFAULT_CONFIG['project_id'] = project_id

def get_location() -> str:
    """Get current location/region"""
    return DEFAULT_CONFIG['location']

def set_location(location: str) -> None:
    """Set location/region"""
    DEFAULT_CONFIG['location'] = location 