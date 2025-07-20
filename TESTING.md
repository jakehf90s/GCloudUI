# Google Cloud Access Tool - Testing Guide

This document describes the testing framework for the Google Cloud Access Tool application.

## Overview

The application includes a comprehensive testing suite with three types of tests:

1. **Quick Tests** - Basic application startup and import verification
2. **Unit Tests** - Individual function testing with mocked dependencies
3. **Integration Tests** - Real Google Cloud API testing (requires authentication)

## Test Files

- `test_core.py` - Integration tests for core Google Cloud API functions
- `test_unit.py` - Unit tests with mocked dependencies
- `run_tests.py` - Test runner script that orchestrates all tests

## Running Tests

### Quick Test (Recommended for basic verification)

```bash
python run_tests.py --quick
```

This test verifies:
- Application can be imported successfully
- Core modules are accessible
- Google Cloud authentication status

### Unit Tests (No Google Cloud setup required)

```bash
python run_tests.py --unit
```

These tests use mocked Google Cloud clients and verify:
- All core functions handle success and error cases correctly
- Data structures are properly formatted
- Error handling works as expected

### Integration Tests (Requires Google Cloud setup)

```bash
python run_tests.py --integration
```

These tests make real API calls to Google Cloud and verify:
- Authentication works correctly
- API endpoints are accessible
- Real data can be retrieved and processed

### All Tests

```bash
python run_tests.py --all
```

Runs all three test suites in sequence.

## Test Results

### Unit Tests

Unit tests are designed to pass without any Google Cloud setup. They test:

- ✅ API initialization
- ✅ Cloud Run services retrieval (mocked)
- ✅ Container images retrieval (mocked)
- ✅ Logs retrieval (mocked)
- ✅ Service accounts retrieval (mocked)
- ✅ IAM permissions retrieval (mocked)
- ✅ Image building (mocked)
- ✅ Image pushing (mocked)
- ✅ Service creation (mocked)
- ✅ Permission addition (mocked)
- ✅ gcloud command execution (mocked)
- ✅ Authentication checking (mocked)
- ✅ Error handling for all functions

### Integration Tests

Integration tests require Google Cloud authentication and may fail if:

- APIs are not enabled in the project
- Insufficient permissions
- Network connectivity issues

Expected results:
- ✅ Authentication - Should pass if `gcloud auth application-default login` was run
- ⚠️ Cloud Run Services - May fail if Cloud Run API is not enabled
- ⚠️ Container Images - May fail if Artifact Registry API is not enabled
- ⚠️ Logs - May fail if Logging API permissions are insufficient
- ✅ Service Accounts - Should pass (returns empty list)
- ✅ IAM Permissions - Should pass (returns empty list)
- ⚠️ Image Build - May fail if Cloud Build API is not enabled
- ✅ Image Push - Should pass (mock implementation)
- ⚠️ Service Creation - May fail if Cloud Run API is not enabled
- ✅ Add Permission - Should pass (mock implementation)
- ✅ gcloud Command - Should pass if gcloud CLI is installed

## Test Output

### Console Output

Tests provide detailed console output with:
- 🔐 Authentication status
- 🚀 Cloud Run operations
- 🐳 Container operations
- 📋 Logging operations
- 👤 IAM operations
- 🔨 Build operations
- 📤 Push operations
- ⚙️ gcloud operations

### JSON Results

Integration tests save detailed results to timestamped JSON files:
- `test_results_YYYYMMDD_HHMMSS.json`
- Contains all test results, errors, and timing information
- Useful for debugging and CI/CD integration

## Prerequisites

### For Unit Tests
- Python 3.8+
- Virtual environment with dependencies installed
- No Google Cloud setup required

### For Integration Tests
- Python 3.8+
- Virtual environment with dependencies installed
- Google Cloud CLI installed (`gcloud`)
- Authenticated with `gcloud auth application-default login`
- Google Cloud project with appropriate APIs enabled

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure virtual environment is activated
   - Check that all dependencies are installed: `pip install -r requirements.txt`

2. **Authentication Errors**
   - Run `gcloud auth application-default login`
   - Verify project is set: `gcloud config get-value project`

3. **API Errors**
   - Enable required APIs in Google Cloud Console:
     - Cloud Run API
     - Artifact Registry API
     - Cloud Build API
     - Logging API

4. **Permission Errors**
   - Ensure service account has appropriate roles:
     - Cloud Run Admin
     - Artifact Registry Reader
     - Cloud Build Editor
     - Logs Viewer

### Debug Mode

For detailed debugging, you can run individual test files:

```bash
# Run unit tests with verbose output
python -m unittest test_unit -v

# Run integration tests with specific project
python test_core.py --project-id YOUR_PROJECT_ID
```

## Continuous Integration

The test suite is designed to work in CI/CD environments:

- Unit tests run without external dependencies
- Integration tests can be skipped if Google Cloud setup is not available
- JSON output can be parsed for automated reporting
- Exit codes indicate overall test success/failure

## Adding New Tests

### Unit Tests

1. Add test methods to `TestGCloudAPI` class in `test_unit.py`
2. Use `@patch` decorator to mock Google Cloud clients
3. Test both success and error scenarios
4. Verify return data structure and content

### Integration Tests

1. Add test methods to `GCloudAPITester` class in `test_core.py`
2. Test real API calls with proper error handling
3. Include appropriate assertions for expected behavior
4. Handle cases where APIs may not be available

## Test Coverage

Current test coverage includes:

- ✅ Core API initialization
- ✅ All major Google Cloud service interactions
- ✅ Error handling and edge cases
- ✅ Data structure validation
- ✅ Authentication flows
- ✅ Command-line interface testing

## Performance

- Unit tests: ~1-2 seconds
- Integration tests: ~10-30 seconds (depending on API response times)
- Quick tests: ~1 second

## Security

- Tests do not modify production resources
- Integration tests use read-only operations where possible
- Mock implementations prevent accidental API calls
- No sensitive data is logged in test output 