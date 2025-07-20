#!/usr/bin/env python3
"""
Google Cloud Access Tool - Test Runner
This script runs both unit tests and integration tests.
"""

import sys
import argparse
import subprocess
from pathlib import Path


def run_unit_tests():
    """Run unit tests"""
    print("🧪 Running Unit Tests...")
    print("=" * 50)
    
    try:
        result = subprocess.run([sys.executable, 'test_unit.py'], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Unit tests failed:")
        print(e.stdout)
        print(e.stderr)
        return False


def run_integration_tests(project_id=None, location="us-central1"):
    """Run integration tests"""
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)
    
    cmd = [sys.executable, 'test_core.py']
    if project_id:
        cmd.extend(['--project-id', project_id])
    if location:
        cmd.extend(['--location', location])
    
    try:
        result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Integration tests failed with exit code: {e.returncode}")
        return False


def run_quick_test():
    """Run a quick test to verify the application can start"""
    print("⚡ Running Quick Application Test...")
    print("=" * 50)
    
    try:
        # Try to import the main application
        from ui.main_window import GCloudAccessApp
        from core.gcloudapi import GCloudAPI
        
        # Test API initialization
        api = GCloudAPI()
        auth_result = api.check_authentication()
        
        print("✅ Application imports successfully")
        print(f"   Authentication: {'✅' if auth_result['authenticated'] else '❌'}")
        if auth_result['authenticated']:
            print(f"   Project: {auth_result['project']}")
        else:
            print(f"   Error: {auth_result.get('error', 'Unknown')}")
        
        return True
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='Run Google Cloud Access Tool Tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--quick', action='store_true', help='Run quick application test only')
    parser.add_argument('--project-id', help='Google Cloud Project ID for integration tests')
    parser.add_argument('--location', default='us-central1', help='Google Cloud location for integration tests')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    # If no specific test type is specified, run all
    if not any([args.unit, args.integration, args.quick]):
        args.all = True
    
    print("🚀 Google Cloud Access Tool - Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run quick test
    if args.quick or args.all:
        results.append(('Quick Test', run_quick_test()))
    
    # Run unit tests
    if args.unit or args.all:
        results.append(('Unit Tests', run_unit_tests()))
    
    # Run integration tests
    if args.integration or args.all:
        results.append(('Integration Tests', run_integration_tests(args.project_id, args.location)))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 