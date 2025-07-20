# Google Cloud Access Tool - Setup Guide

This guide covers all the different ways to set up and run the Google Cloud Access Tool.

## 🚀 Quick Start

Choose your preferred setup method:

- **[Local Environment](#local-environment)** - Run directly on your machine
- **[Docker](#docker)** - Run in a containerized environment
- **[Docker Compose](#docker-compose)** - Run with orchestration

## 📋 Prerequisites

### Required
- **Python 3.8+** - [Download here](https://python.org)
- **Google Cloud SDK** - [Install here](https://cloud.google.com/sdk/docs/install)
- **Google Cloud Project** with billing enabled

### Optional
- **Docker** - For containerized deployment
- **Docker Compose** - For orchestrated deployment
- **X11/XQuartz** - For GUI in Docker (Linux/macOS)

## 🔧 Local Environment Setup

### Linux/macOS

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd GCloudAccess
   ```

2. **Run the setup script:**
   ```bash
   chmod +x setup-local.sh
   ./setup-local.sh
   ```

3. **Authenticate with Google Cloud:**
   ```bash
   gcloud auth application-default login
   ```

4. **Set your project:**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

5. **Run the application:**
   ```bash
   ./run.sh
   # or
   python run.py
   ```

### Windows

1. **Clone the repository:**
   ```cmd
   git clone <repository-url>
   cd GCloudAccess
   ```

2. **Run the setup script:**
   ```cmd
   setup-windows.bat
   ```

3. **Authenticate with Google Cloud:**
   ```cmd
   gcloud auth application-default login
   ```

4. **Set your project:**
   ```cmd
   gcloud config set project YOUR_PROJECT_ID
   ```

5. **Run the application:**
   ```cmd
   run.bat
   # or
   python run.py
   ```

### Manual Setup

If you prefer manual setup:

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Google Cloud SDK** (if not already installed):
   - **Linux:** Follow [official guide](https://cloud.google.com/sdk/docs/install#linux)
   - **macOS:** `brew install --cask google-cloud-sdk`
   - **Windows:** Download from [official site](https://cloud.google.com/sdk/docs/install#windows)

4. **Authenticate and configure:**
   ```bash
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

## 🐳 Docker Setup

### Prerequisites
- **Docker** installed and running
- **Google Cloud SDK** installed locally (for authentication)

### Quick Start

1. **Build and run with GUI:**
   ```bash
   chmod +x docker-run.sh
   ./docker-run.sh gui
   ```

2. **Build and run headless:**
   ```bash
   ./docker-run.sh headless
   ```

### Manual Docker Commands

1. **Build the image:**
   ```bash
   docker build -t gcloud-access-tool .
   ```

2. **Run with GUI (Linux):**
   ```bash
   xhost +local:docker
   docker run -it --rm \
     -e DISPLAY=$DISPLAY \
     -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
     -v ~/.config/gcloud:/home/gclouduser/.config/gcloud:ro \
     -v $(pwd)/data:/app/data:rw \
     --network host \
     gcloud-access-tool
   ```

3. **Run with GUI (macOS):**
   ```bash
   # Start XQuartz first
   open -a XQuartz
   
   # Run container
   docker run -it --rm \
     -e DISPLAY=host.docker.internal:0 \
     -v ~/.config/gcloud:/home/gclouduser/.config/gcloud:ro \
     -v $(pwd)/data:/app/data:rw \
     gcloud-access-tool
   ```

4. **Run headless:**
   ```bash
   docker run -it --rm \
     -e DISPLAY=:99 \
     -v ~/.config/gcloud:/home/gclouduser/.config/gcloud:ro \
     -v $(pwd)/data:/app/data:rw \
     -p 8080:8080 \
     gcloud-access-tool
   ```

## 🐙 Docker Compose Setup

### Prerequisites
- **Docker** and **Docker Compose** installed
- **Google Cloud SDK** installed locally

### Quick Start

1. **Run with GUI:**
   ```bash
   docker-compose --profile gui up --build
   ```

2. **Run headless:**
   ```bash
   docker-compose --profile headless up --build
   ```

3. **Stop services:**
   ```bash
   docker-compose down
   ```

### Using the Docker Run Script

1. **Run with GUI:**
   ```bash
   ./docker-run.sh compose-gui
   ```

2. **Run headless:**
   ```bash
   ./docker-run.sh compose-headless
   ```

3. **View logs:**
   ```bash
   ./docker-run.sh logs
   ```

4. **Stop services:**
   ```bash
   ./docker-run.sh stop
   ```

## 🔐 Authentication Setup

### Method 1: Application Default Credentials (Recommended)

1. **Authenticate:**
   ```bash
   gcloud auth application-default login
   ```

2. **Set project:**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

### Method 2: Service Account Key

1. **Create service account:**
   ```bash
   gcloud iam service-accounts create gcloud-access \
     --display-name="Google Cloud Access Tool"
   ```

2. **Grant permissions:**
   ```bash
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:gcloud-access@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/editor"
   ```

3. **Create key file:**
   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=gcloud-access@YOUR_PROJECT_ID.iam.gserviceaccount.com
   ```

4. **Set environment variable:**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/key.json"
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1

# Application Configuration
LOG_LEVEL=INFO
MAX_LOG_ENTRIES=100
REFRESH_INTERVAL=30

# Docker Configuration (if using Docker)
DISPLAY=:0
```

### Configuration File

The application uses `config.py` for default settings. You can modify:

```python
DEFAULT_CONFIG = {
    'project_id': os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id'),
    'location': 'us-central1',
    'build_bucket': 'your-build-bucket',
    'container_registry': 'gcr.io',
    'default_region': 'us-central1',
    'log_level': 'INFO',
    'max_log_entries': 100,
    'refresh_interval': 30,
}
```

## 🚨 Troubleshooting

### Common Issues

#### Authentication Errors
```bash
# Error: DefaultCredentialsError
gcloud auth application-default login
```

#### Permission Errors
```bash
# Error: Permission denied
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:your-email@domain.com" \
  --role="roles/editor"
```

#### Docker GUI Issues (Linux)
```bash
# Error: Cannot connect to X server
xhost +local:docker
```

#### Docker GUI Issues (macOS)
```bash
# Error: Cannot connect to X server
# Install and start XQuartz
brew install --cask xquartz
open -a XQuartz
```

#### Python Import Errors
```bash
# Error: ModuleNotFoundError
pip install -r requirements.txt
```

#### Google Cloud SDK Not Found
```bash
# Error: gcloud command not found
# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# macOS
brew install --cask google-cloud-sdk

# Windows
# Download from https://cloud.google.com/sdk/docs/install#windows
```

### Debug Mode

Run with debug logging:

```bash
# Local
LOG_LEVEL=DEBUG python run.py

# Docker
docker run -e LOG_LEVEL=DEBUG gcloud-access-tool
```

### Clean Installation

If you need to start fresh:

```bash
# Local
rm -rf venv
rm -rf data
rm -rf logs
./setup-local.sh

# Docker
./docker-run.sh cleanup
docker system prune -a
```

## 📁 Project Structure

```
GCloudAccess/
├── main.py                 # Main application
├── config.py              # Configuration settings
├── dialogs.py             # UI dialogs
├── utils.py               # Utility functions
├── run.py                 # Launcher script
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
├── setup-local.sh         # Local setup script (Linux/macOS)
├── setup-windows.bat      # Local setup script (Windows)
├── docker-run.sh          # Docker run script
├── README.md              # Main documentation
├── SETUP.md               # This setup guide
├── FEATURES.md            # Feature documentation
├── data/                  # Application data (created by setup)
├── logs/                  # Application logs (created by setup)
└── example/               # Example configurations
    ├── Dockerfile         # Example Dockerfile
    └── cloudbuild.yaml    # Example Cloud Build config
```

## 🔄 Updates

### Updating the Application

```bash
# Local
git pull
pip install -r requirements.txt

# Docker
git pull
./docker-run.sh build
```

### Updating Dependencies

```bash
# Update requirements.txt
pip freeze > requirements.txt

# Reinstall
pip install -r requirements.txt
```

## 📞 Support

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Review the logs in the `logs/` directory**
3. **Run in debug mode** to get more information
4. **Check Google Cloud Console** for API errors
5. **Verify your permissions** in IAM

## 🎯 Next Steps

After successful setup:

1. **Explore the UI** - Navigate through the different tabs
2. **Configure your project** - Set up your Google Cloud project
3. **Test basic operations** - Try listing services and images
4. **Set up monitoring** - Configure logging and alerts
5. **Customize configuration** - Modify settings for your needs

For advanced usage, see the [FEATURES.md](FEATURES.md) documentation. 