# Google Cloud Access Tool

A PyQt6-based desktop application for managing Google Cloud Platform services with a user-friendly interface.

## Features

### Cloud Run Services
- **View Services**: List all Cloud Run services in your project
- **Create Services**: Deploy new Cloud Run services
- **Service Status**: Monitor service health and status
- **Service URLs**: Access service endpoints directly

### Cloud Build
- **Build Images**: Create container images from source code
- **Push Images**: Push built images to Container Registry
- **Build Logs**: Monitor build progress and logs
- **Build Configuration**: Customize build parameters

### Container Images
- **List Images**: View all container images in your registry
- **Image Details**: See image metadata and descriptions
- **Repository Management**: Manage image repositories

### Logs
- **Real-time Logs**: View Cloud Run, Cloud Build, and Container Registry logs
- **Log Filtering**: Filter logs by service type
- **Log Search**: Search through log entries

### IAM Management
- **Service Accounts**: View and manage service accounts
- **Permissions**: View current IAM permissions and roles
- **Role Management**: Add and modify IAM roles
- **Access Control**: Manage user and service account access

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Google Cloud SDK** installed and configured
3. **Google Cloud Project** with the following APIs enabled:
   - Cloud Run API
   - Cloud Build API
   - Container Registry API
   - Cloud Logging API
   - IAM API
   - Resource Manager API

## Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Authenticate with Google Cloud**:
   ```bash
   gcloud auth application-default login
   ```

4. **Set your project ID** (optional):
   ```bash
   export GOOGLE_CLOUD_PROJECT=your-project-id
   ```

## Usage

### Starting the Application

```bash
python main.py
```

### Configuration

The application uses the `config.py` file for default settings. You can modify:

- **Project ID**: Your Google Cloud project ID
- **Location**: Default region for Cloud Run services
- **Build Bucket**: Storage bucket for build artifacts
- **Container Registry**: Registry for storing images

### Basic Workflow

1. **Authentication**: The app will check your Google Cloud authentication on startup
2. **Select Project**: Ensure you're working with the correct project
3. **Navigate Tabs**: Use the tab interface to access different features
4. **Refresh Data**: Click refresh buttons to update information
5. **Monitor Operations**: Watch the status bar for operation progress

## API Permissions Required

Your Google Cloud account needs the following roles:

- **Cloud Run Admin** (`roles/run.admin`)
- **Cloud Build Editor** (`roles/cloudbuild.builds.editor`)
- **Container Registry Admin** (`roles/storage.admin`)
- **Logs Viewer** (`roles/logging.viewer`)
- **IAM Admin** (`roles/iam.admin`) - for IAM management
- **Service Account User** (`roles/iam.serviceAccountUser`)

## Troubleshooting

### Authentication Issues
- Run `gcloud auth application-default login`
- Ensure your account has the required permissions
- Check that the correct project is set

### API Errors
- Enable required APIs in Google Cloud Console
- Verify project ID is correct
- Check billing is enabled for the project

### Build Failures
- Ensure source code is properly uploaded to Cloud Storage
- Check Dockerfile exists and is valid
- Verify build bucket permissions

## Development

### Project Structure
```
GCloudAccess/
├── main.py              # Main application file
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Adding New Features

1. **Add new worker methods** in `GCloudWorker` class
2. **Create UI components** in the main application
3. **Connect signals** for async operations
4. **Update configuration** if needed

### Testing

The application can be tested with:
- A Google Cloud project with billing enabled
- Sample container images
- Test Cloud Run services

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review Google Cloud documentation
3. Open an issue in the repository

## Additional Features (Future)

- **Service Scaling**: Scale Cloud Run services up/down
- **Custom Domains**: Configure custom domains for services
- **Environment Variables**: Manage service environment variables
- **Secrets Management**: Handle sensitive configuration
- **Monitoring**: Integration with Cloud Monitoring
- **Cost Analysis**: Track and analyze costs
- **Multi-Project Support**: Switch between multiple projects
- **Export/Import**: Backup and restore configurations 