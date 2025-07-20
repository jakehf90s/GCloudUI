#!/usr/bin/env python3
"""
Launcher script for Google Cloud Access Tool
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are installed"""
    import pkg_resources
    
    required_packages = [
        'PyQt6',
        'google-cloud-build',
        'google-cloud-run',
        'google-cloud-artifact-registry',
        'google-cloud-logging',
        'google-cloud-iam',
        'google-cloud-resource-manager'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            pkg_resources.get_distribution(package)
        except pkg_resources.DistributionNotFound:
            missing_packages.append(package)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with:")
        print("pip install -r requirements.txt")
        sys.exit(1)

def check_gcloud_installation():
    """Check if gcloud CLI is installed"""
    try:
        result = subprocess.run(['gcloud', 'version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✓ Google Cloud SDK found")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("⚠ Google Cloud SDK not found")
    print("Please install Google Cloud SDK from: https://cloud.google.com/sdk/docs/install")
    return False

def check_gcloud_auth():
    """Check if gcloud is authenticated"""
    try:
        result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and 'ACTIVE' in result.stdout:
            print("✓ Google Cloud authentication found")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("⚠ Google Cloud authentication required")
    print("Run: gcloud auth application-default login")
    return False

def check_project_setup():
    """Check if a project is configured"""
    try:
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            project = result.stdout.strip()
            print(f"✓ Project configured: {project}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("⚠ No project configured")
    print("Run: gcloud config set project YOUR_PROJECT_ID")
    return False

def setup_environment():
    """Setup environment variables"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))

def main():
    """Main launcher function"""
    print("Google Cloud Access Tool - Launcher")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    print("✓ Python version compatible")
    
    # Check dependencies
    check_dependencies()
    print("✓ Dependencies installed")
    
    # Setup environment
    setup_environment()
    
    # Check gcloud installation
    gcloud_installed = check_gcloud_installation()
    
    # Check authentication
    gcloud_auth = check_gcloud_auth()
    
    # Check project setup
    project_setup = check_project_setup()
    
    print("\n" + "=" * 40)
    
    if not gcloud_installed:
        print("\n❌ Cannot start application without Google Cloud SDK")
        print("Please install Google Cloud SDK first")
        sys.exit(1)
    
    if not gcloud_auth:
        print("\n⚠ Application may not work properly without authentication")
        print("Run: gcloud auth application-default login")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    if not project_setup:
        print("\n⚠ Application may not work properly without project configuration")
        print("Run: gcloud config set project YOUR_PROJECT_ID")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n🚀 Starting Google Cloud Access Tool...")
    print("=" * 40)
    
    try:
        # Import and run the main application
        from main import main as app_main
        app_main()
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("Make sure all files are in the same directory")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 