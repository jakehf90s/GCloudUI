#!/bin/bash

# Google Cloud Access Tool - Local Environment Setup Script
# This script sets up the local environment for running the application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    if command_exists pip3; then
        pip3 install -r requirements.txt
    elif command_exists pip; then
        pip install -r requirements.txt
    else
        print_error "pip not found. Please install pip first."
        exit 1
    fi
    
    print_success "Python dependencies installed successfully"
}

# Function to install Google Cloud SDK on Linux
install_gcloud_linux() {
    print_status "Installing Google Cloud SDK on Linux..."
    
    # Add Google Cloud SDK repository
    echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
    
    # Import Google Cloud public key
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
    
    # Update package list and install
    sudo apt-get update
    sudo apt-get install -y google-cloud-cli
    
    print_success "Google Cloud SDK installed successfully"
}

# Function to install Google Cloud SDK on macOS
install_gcloud_macos() {
    print_status "Installing Google Cloud SDK on macOS..."
    
    if command_exists brew; then
        brew install --cask google-cloud-sdk
    else
        print_warning "Homebrew not found. Installing via official installer..."
        
        # Download and install Google Cloud SDK
        curl https://sdk.cloud.google.com | bash
        exec -l $SHELL
    fi
    
    print_success "Google Cloud SDK installed successfully"
}

# Function to install system dependencies
install_system_deps() {
    local os=$(detect_os)
    
    print_status "Installing system dependencies for $os..."
    
    if [[ "$os" == "linux" ]]; then
        # Install X11 and Qt dependencies
        sudo apt-get update
        sudo apt-get install -y \
            python3-dev \
            python3-pip \
            python3-venv \
            libx11-6 \
            libxext6 \
            libxrender1 \
            libxtst6 \
            libxi6 \
            libxrandr2 \
            libxss1 \
            libgconf-2-4 \
            libnss3 \
            libcups2 \
            libdrm2 \
            libxkbcommon0 \
            libatspi2.0-0 \
            libxcomposite1 \
            libxcursor1 \
            libxdamage1 \
            libxfixes3 \
            libxrandr2 \
            libgbm1 \
            libasound2 \
            qt6-base-dev \
            qt6-tools-dev \
            qt6-tools-dev-tools
        
    elif [[ "$os" == "macos" ]]; then
        if command_exists brew; then
            brew install qt@6
        else
            print_warning "Homebrew not found. Please install Qt6 manually."
        fi
    fi
    
    print_success "System dependencies installed"
}

# Function to setup virtual environment
setup_virtual_env() {
    print_status "Setting up Python virtual environment..."
    
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment setup complete"
}

# Function to setup Google Cloud authentication
setup_gcloud_auth() {
    print_status "Setting up Google Cloud authentication..."
    
    if command_exists gcloud; then
        print_status "Google Cloud SDK found. Checking authentication..."
        
        # Check if already authenticated
        if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
            print_success "Already authenticated with Google Cloud"
        else
            print_warning "Not authenticated. Please run: gcloud auth application-default login"
        fi
        
        # Check if project is set
        local project=$(gcloud config get-value project 2>/dev/null)
        if [[ -n "$project" ]]; then
            print_success "Project configured: $project"
        else
            print_warning "No project configured. Please run: gcloud config set project YOUR_PROJECT_ID"
        fi
    else
        print_error "Google Cloud SDK not found. Please install it first."
        exit 1
    fi
}

# Function to create data directory
create_data_dir() {
    print_status "Creating data directory..."
    
    mkdir -p data
    mkdir -p logs
    
    print_success "Data directories created"
}

# Function to setup environment variables
setup_env_vars() {
    print_status "Setting up environment variables..."
    
    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        cat > .env << EOF
# Google Cloud Access Tool Environment Variables
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_REGION=us-central1
LOG_LEVEL=INFO
MAX_LOG_ENTRIES=100
REFRESH_INTERVAL=30
EOF
        print_success ".env file created"
    else
        print_status ".env file already exists"
    fi
}

# Function to create desktop shortcut (Linux)
create_desktop_shortcut() {
    local os=$(detect_os)
    
    if [[ "$os" == "linux" ]]; then
        print_status "Creating desktop shortcut..."
        
        cat > ~/Desktop/gcloud-access.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Google Cloud Access Tool
Comment=Manage Google Cloud Platform services
Exec=$(pwd)/run.sh
Icon=$(pwd)/icon.png
Terminal=false
Categories=Development;Network;
EOF
        
        chmod +x ~/Desktop/gcloud-access.desktop
        print_success "Desktop shortcut created"
    fi
}

# Function to create run script
create_run_script() {
    print_status "Creating run script..."
    
    cat > run.sh << 'EOF'
#!/bin/bash

# Google Cloud Access Tool - Run Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment if it exists
if [[ -d "$SCRIPT_DIR/venv" ]]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Load environment variables
if [[ -f "$SCRIPT_DIR/.env" ]]; then
    export $(cat "$SCRIPT_DIR/.env" | grep -v '^#' | xargs)
fi

# Run the application
cd "$SCRIPT_DIR"
python run.py
EOF
    
    chmod +x run.sh
    print_success "Run script created"
}

# Main setup function
main() {
    echo "=========================================="
    echo "Google Cloud Access Tool - Local Setup"
    echo "=========================================="
    
    local os=$(detect_os)
    print_status "Detected OS: $os"
    
    # Check Python version
    if ! command_exists python3; then
        print_error "Python 3.8+ is required but not installed"
        exit 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_success "Python version: $python_version"
    
    # Install system dependencies
    install_system_deps
    
    # Setup virtual environment
    setup_virtual_env
    
    # Install Python dependencies
    install_python_deps
    
    # Install Google Cloud SDK
    if ! command_exists gcloud; then
        if [[ "$os" == "linux" ]]; then
            install_gcloud_linux
        elif [[ "$os" == "macos" ]]; then
            install_gcloud_macos
        else
            print_error "Unsupported OS for automatic Google Cloud SDK installation"
            print_warning "Please install Google Cloud SDK manually"
        fi
    else
        print_success "Google Cloud SDK already installed"
    fi
    
    # Setup Google Cloud authentication
    setup_gcloud_auth
    
    # Create directories
    create_data_dir
    
    # Setup environment variables
    setup_env_vars
    
    # Create run script
    create_run_script
    
    # Create desktop shortcut
    create_desktop_shortcut
    
    echo ""
    echo "=========================================="
    print_success "Setup completed successfully!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Authenticate with Google Cloud:"
    echo "   gcloud auth application-default login"
    echo ""
    echo "2. Set your project ID:"
    echo "   gcloud config set project YOUR_PROJECT_ID"
    echo ""
    echo "3. Run the application:"
    echo "   ./run.sh"
    echo "   or"
    echo "   python run.py"
    echo ""
    echo "4. Or use the desktop shortcut (Linux)"
    echo ""
}

# Run main function
main "$@" 