#!/usr/bin/env python3
"""
Google Cloud Access Tool - Unit Tests
This script provides unit tests for core functions with mock data.
"""

import sys
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add the project root to the path
sys.path.insert(0, '.')

from core.gcloudapi import GCloudAPI


class TestGCloudAPI(unittest.TestCase):
    """Unit tests for GCloudAPI class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api = GCloudAPI("test-project-id", "us-central1")
    
    def test_init_with_project_id(self):
        """Test initialization with project ID"""
        api = GCloudAPI("my-project", "us-west1")
        self.assertEqual(api.project_id, "my-project")
        self.assertEqual(api.location, "us-west1")
    
    def test_init_without_project_id(self):
        """Test initialization without project ID"""
        with patch('core.gcloudapi.default') as mock_default:
            mock_default.return_value = (Mock(), "default-project")
            api = GCloudAPI()
            self.assertEqual(api.project_id, "default-project")
    
    def test_init_without_project_id_no_auth(self):
        """Test initialization without project ID and no authentication"""
        with patch('core.gcloudapi.default') as mock_default:
            from google.auth.exceptions import DefaultCredentialsError
            mock_default.side_effect = DefaultCredentialsError()
            api = GCloudAPI()
            self.assertEqual(api.project_id, "your-project-id")
    
    @patch('core.gcloudapi.run_v2.ServicesClient')
    def test_get_cloud_run_services_success(self, mock_client_class):
        """Test successful Cloud Run services retrieval"""
        # Mock the client and its response
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Create mock service objects
        mock_service = Mock()
        mock_service.name = "projects/test-project/locations/us-central1/services/test-service"
        mock_service.status.url = "https://test-service-url"
        mock_service.status.latest_ready_revision_name = "test-revision"
        mock_service.metadata.create_time.isoformat.return_value = "2023-01-01T00:00:00"
        
        # Mock conditions
        mock_condition = Mock()
        mock_condition.type = "Ready"
        mock_service.status.conditions = [mock_condition]
        
        mock_client.list_services.return_value = [mock_service]
        
        # Test the function
        result = self.api.get_cloud_run_services()
        
        # Verify the result
        self.assertTrue(result['success'])
        self.assertEqual(result['type'], 'services')
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['name'], mock_service.name)
        self.assertEqual(result['data'][0]['status'], 'Ready')
    
    @patch('core.gcloudapi.run_v2.ServicesClient')
    def test_get_cloud_run_services_error(self, mock_client_class):
        """Test Cloud Run services retrieval with error"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.list_services.side_effect = Exception("API Error")
        
        result = self.api.get_cloud_run_services()
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'API Error')
    
    @patch('core.gcloudapi.artifactregistry.ArtifactRegistryClient')
    def test_get_container_images_success(self, mock_client_class):
        """Test successful container images retrieval"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Create mock repository objects
        mock_repo = Mock()
        mock_repo.name = "projects/test-project/locations/us-central1/repositories/test-repo"
        mock_repo.description = "Test repository"
        mock_repo.format_.name = "DOCKER"
        
        mock_client.list_repositories.return_value = [mock_repo]
        
        result = self.api.get_container_images()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['type'], 'images')
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['name'], mock_repo.name)
        self.assertEqual(result['data'][0]['format'], 'DOCKER')
    
    @patch('core.gcloudapi.logging_v2.Client')
    def test_get_logs_success(self, mock_client_class):
        """Test successful logs retrieval"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Create mock log entry
        mock_entry = Mock()
        mock_entry.timestamp.isoformat.return_value = "2023-01-01T00:00:00"
        mock_entry.severity.name = "INFO"
        mock_entry.text_payload = "Test log message"
        mock_entry.resource.type = "cloud_run_revision"
        
        mock_client.list_entries.return_value = [mock_entry]
        
        result = self.api.get_logs()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['type'], 'logs')
        self.assertEqual(len(result['data']), 1)
        self.assertEqual(result['data'][0]['text_payload'], "Test log message")
        self.assertEqual(result['data'][0]['severity'], "INFO")
    
    def test_get_service_accounts_success(self):
        """Test successful service accounts retrieval"""
        result = self.api.get_service_accounts()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['type'], 'service_accounts')
        self.assertEqual(len(result['data']), 0)  # Empty list for now
    
    def test_get_permissions_success(self):
        """Test successful permissions retrieval"""
        result = self.api.get_permissions()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['type'], 'permissions')
        self.assertEqual(len(result['data']), 0)  # Empty list for now
    
    @patch('core.gcloudapi.cloudbuild_v1.CloudBuildClient')
    def test_build_image_success(self, mock_client_class):
        """Test successful image build"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Create mock operation
        mock_operation = Mock()
        mock_operation.name = "operations/test-operation"
        mock_client.create_build.return_value = mock_operation
        
        build_config = {
            'bucket': 'test-bucket',
            'object': 'test-source.tar.gz',
            'image_name': 'gcr.io/test-project/test-image:latest'
        }
        
        result = self.api.build_image(build_config)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['type'], 'build_started')
        self.assertEqual(result['data']['operation'], "operations/test-operation")
    
    def test_push_image_success(self):
        """Test successful image push"""
        result = self.api.push_image('gcr.io/test-project/test-image:latest')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['type'], 'push_completed')
        self.assertIn('message', result['data'])
    
    @patch('core.gcloudapi.run_v2.ServicesClient')
    def test_create_cloud_run_service_success(self, mock_client_class):
        """Test successful Cloud Run service creation"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # Create mock operation
        mock_operation = Mock()
        mock_operation.name = "operations/test-service-operation"
        mock_client.create_service.return_value = mock_operation
        
        service_config = {
            'name': 'test-service',
            'image': 'gcr.io/test-project/test-image:latest',
            'port': 8080,
            'cpu': '1000m',
            'memory': '512Mi'
        }
        
        result = self.api.create_cloud_run_service(service_config)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['type'], 'service_created')
        self.assertEqual(result['data']['operation'], "operations/test-service-operation")
    
    def test_add_permission_success(self):
        """Test successful permission addition"""
        result = self.api.add_permission('roles/viewer', 'user:test@example.com')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['type'], 'permission_added')
        self.assertIn('message', result['data'])
    
    @patch('subprocess.run')
    def test_run_gcloud_command_success(self, mock_run):
        """Test successful gcloud command execution"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = '{"project": "test-project"}'
        mock_result.stderr = ''
        mock_run.return_value = mock_result
        
        result = self.api.run_gcloud_command(['config', 'list'])
        
        self.assertTrue(result['success'])
        self.assertEqual(result['return_code'], 0)
        self.assertEqual(result['stdout'], '{"project": "test-project"}')
    
    @patch('subprocess.run')
    def test_run_gcloud_command_error(self, mock_run):
        """Test gcloud command execution with error"""
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(1, 'gcloud', 'Command failed')
        
        result = self.api.run_gcloud_command(['invalid', 'command'])
        
        self.assertFalse(result['success'])
        self.assertEqual(result['return_code'], 1)
    
    @patch('subprocess.run')
    def test_run_gcloud_command_not_found(self, mock_run):
        """Test gcloud command when gcloud is not found"""
        mock_run.side_effect = FileNotFoundError()
        
        result = self.api.run_gcloud_command(['config', 'list'])
        
        self.assertFalse(result['success'])
        self.assertEqual(result['error'], 'gcloud command not found')
    
    @patch('core.gcloudapi.default')
    def test_check_authentication_success(self, mock_default):
        """Test successful authentication check"""
        mock_default.return_value = (Mock(), "test-project")
        
        result = self.api.check_authentication()
        
        self.assertTrue(result['success'])
        self.assertTrue(result['authenticated'])
        self.assertEqual(result['project'], "test-project")
    
    @patch('core.gcloudapi.default')
    def test_check_authentication_failure(self, mock_default):
        """Test authentication check failure"""
        from google.auth.exceptions import DefaultCredentialsError
        mock_default.side_effect = DefaultCredentialsError()
        
        result = self.api.check_authentication()
        
        self.assertFalse(result['success'])
        self.assertFalse(result['authenticated'])
        self.assertIn('error', result)


class TestGCloudAPIErrorHandling(unittest.TestCase):
    """Test error handling in GCloudAPI"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api = GCloudAPI("test-project-id", "us-central1")
    
    def test_get_cloud_run_services_exception(self):
        """Test exception handling in get_cloud_run_services"""
        with patch('core.gcloudapi.run_v2.ServicesClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.list_services.side_effect = Exception("Network error")
            
            result = self.api.get_cloud_run_services()
            
            self.assertFalse(result['success'])
            self.assertEqual(result['error'], 'Network error')
            self.assertEqual(result['data'], [])
    
    def test_get_container_images_exception(self):
        """Test exception handling in get_container_images"""
        with patch('core.gcloudapi.artifactregistry.ArtifactRegistryClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.list_repositories.side_effect = Exception("Permission denied")
            
            result = self.api.get_container_images()
            
            self.assertFalse(result['success'])
            self.assertEqual(result['error'], 'Permission denied')
            self.assertEqual(result['data'], [])
    
    def test_get_logs_exception(self):
        """Test exception handling in get_logs"""
        with patch('core.gcloudapi.logging_v2.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.list_entries.side_effect = Exception("Logging API error")
            
            result = self.api.get_logs()
            
            self.assertFalse(result['success'])
            self.assertEqual(result['error'], 'Logging API error')
            self.assertEqual(result['data'], [])


def run_tests():
    """Run all unit tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestGCloudAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestGCloudAPIErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 