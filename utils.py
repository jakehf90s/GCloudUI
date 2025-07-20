"""
Utility functions for Google Cloud Access Tool
"""

import os
import json
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import logging

from google.auth import default
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import resourcemanager_v3


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger("gcloud_access")
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def get_authenticated_project() -> Tuple[Optional[str], Optional[str]]:
    """Get the authenticated project ID and credentials"""
    try:
        credentials, project = default()
        return project, credentials
    except DefaultCredentialsError:
        return None, None


def validate_project_id(project_id: str) -> bool:
    """Validate if a project ID is properly formatted"""
    if not project_id or project_id == "your-project-id":
        return False
    
    # Basic validation: project ID should be 6-30 characters, lowercase, hyphens, numbers
    import re
    pattern = r'^[a-z][a-z0-9-]{4,28}[a-z0-9]$'
    return bool(re.match(pattern, project_id))


def list_projects() -> List[Dict[str, Any]]:
    """List all accessible projects"""
    try:
        client = resourcemanager_v3.ProjectsClient()
        request = resourcemanager_v3.ListProjectsRequest()
        page_result = client.list_projects(request=request)
        
        projects = []
        for project in page_result:
            projects.append({
                'project_id': project.project_id,
                'name': project.name,
                'display_name': project.display_name,
                'state': project.state.name
            })
        
        return projects
    except Exception as e:
        logging.error(f"Error listing projects: {e}")
        return []


def format_timestamp(timestamp) -> str:
    """Format timestamp for display"""
    if not timestamp:
        return "Unknown"
    
    if hasattr(timestamp, 'isoformat'):
        return timestamp.isoformat()
    
    try:
        dt = datetime.fromisoformat(str(timestamp))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp)


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"


def format_memory(memory_str: str) -> str:
    """Format memory string for display"""
    if not memory_str:
        return "Unknown"
    
    # Convert to a more readable format
    if memory_str.endswith('Mi'):
        return memory_str
    elif memory_str.endswith('Gi'):
        return memory_str
    else:
        return f"{memory_str}Mi"


def format_cpu(cpu_str: str) -> str:
    """Format CPU string for display"""
    if not cpu_str:
        return "Unknown"
    
    if cpu_str.endswith('m'):
        cores = int(cpu_str[:-1]) / 1000
        return f"{cores:.1f} cores"
    else:
        return f"{cpu_str} cores"


def parse_env_vars(env_text: str) -> Dict[str, str]:
    """Parse environment variables from text"""
    env_vars = {}
    if not env_text.strip():
        return env_vars
    
    for line in env_text.split('\n'):
        line = line.strip()
        if line and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip()
    
    return env_vars


def validate_image_name(image_name: str) -> bool:
    """Validate container image name format"""
    if not image_name:
        return False
    
    # Basic validation for GCR format
    if image_name.startswith('gcr.io/'):
        parts = image_name.split('/')
        if len(parts) >= 3:
            return True
    
    # Basic validation for other registries
    if '/' in image_name and ':' in image_name:
        return True
    
    return False


def run_gcloud_command(command: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """Run a gcloud command and return the result"""
    try:
        result = subprocess.run(
            ['gcloud'] + command,
            capture_output=capture_output,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", "gcloud command not found"
    except Exception as e:
        return -1, "", str(e)


def get_gcloud_config() -> Dict[str, str]:
    """Get current gcloud configuration"""
    config = {}
    
    # Get current project
    returncode, stdout, stderr = run_gcloud_command(['config', 'get-value', 'project'])
    if returncode == 0:
        config['project'] = stdout.strip()
    
    # Get current account
    returncode, stdout, stderr = run_gcloud_command(['config', 'get-value', 'account'])
    if returncode == 0:
        config['account'] = stdout.strip()
    
    # Get current region
    returncode, stdout, stderr = run_gcloud_command(['config', 'get-value', 'run/region'])
    if returncode == 0:
        config['region'] = stdout.strip()
    
    return config


def set_gcloud_config(key: str, value: str) -> bool:
    """Set gcloud configuration value"""
    returncode, stdout, stderr = run_gcloud_command(['config', 'set', key, value])
    return returncode == 0


def check_gcloud_auth() -> bool:
    """Check if gcloud is authenticated"""
    returncode, stdout, stderr = run_gcloud_command(['auth', 'list', '--filter=status:ACTIVE'])
    return returncode == 0 and 'ACTIVE' in stdout


def get_service_status_color(status: str) -> str:
    """Get color for service status"""
    status_lower = status.lower()
    if 'ready' in status_lower or 'active' in status_lower:
        return "green"
    elif 'error' in status_lower or 'failed' in status_lower:
        return "red"
    elif 'pending' in status_lower or 'creating' in status_lower:
        return "orange"
    else:
        return "gray"


def get_log_severity_color(severity: str) -> str:
    """Get color for log severity"""
    severity_lower = severity.lower()
    if severity_lower == 'error':
        return "red"
    elif severity_lower == 'warning':
        return "orange"
    elif severity_lower == 'info':
        return "blue"
    elif severity_lower == 'debug':
        return "gray"
    else:
        return "black"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human readable string"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def create_backup_config(config: Dict[str, Any], filename: str = None) -> str:
    """Create a backup of the current configuration"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gcloud_config_backup_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        return filename
    except Exception as e:
        logging.error(f"Error creating backup: {e}")
        return ""


def load_backup_config(filename: str) -> Dict[str, Any]:
    """Load configuration from backup file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading backup: {e}")
        return {}


def validate_url(url: str) -> bool:
    """Validate URL format"""
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, url))


def get_resource_name_from_path(path: str) -> str:
    """Extract resource name from full path"""
    if not path:
        return ""
    
    # Remove project prefix and get the last part
    parts = path.split('/')
    if len(parts) > 0:
        return parts[-1]
    return path


def format_permission_members(members: List[str]) -> str:
    """Format IAM members for display"""
    if not members:
        return "None"
    
    # Group by type
    user_members = [m for m in members if m.startswith('user:')]
    service_accounts = [m for m in members if m.startswith('serviceAccount:')]
    groups = [m for m in members if m.startswith('group:')]
    domains = [m for m in members if m.startswith('domain:')]
    
    formatted = []
    if user_members:
        formatted.append(f"Users: {len(user_members)}")
    if service_accounts:
        formatted.append(f"Service Accounts: {len(service_accounts)}")
    if groups:
        formatted.append(f"Groups: {len(groups)}")
    if domains:
        formatted.append(f"Domains: {len(domains)}")
    
    return ", ".join(formatted) if formatted else "None"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    import re
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    return sanitized or "unnamed" 