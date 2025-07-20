#!/bin/bash

# Google Cloud Access Tool - Docker Run Script
# This script provides easy commands to run the application in Docker

set -e

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

# Function to check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Please install Docker from https://docker.com"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running"
        echo "Please start Docker and try again"
        exit 1
    fi
    
    print_success "Docker is available"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose not found, using docker compose (v2)"
        DOCKER_COMPOSE="docker compose"
    else
        DOCKER_COMPOSE="docker-compose"
    fi
}

# Function to build the Docker image
build_image() {
    print_status "Building Docker image..."
    docker build -t gcloud-access-tool .
    print_success "Docker image built successfully"
}

# Function to run with GUI (Linux/macOS)
run_gui() {
    print_status "Running with GUI support..."
    
    # Check if X11 is available (Linux)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [[ -z "$DISPLAY" ]]; then
            print_error "DISPLAY environment variable not set"
            echo "Please ensure X11 is running and DISPLAY is set"
            exit 1
        fi
        
        # Allow X11 connections from Docker
        xhost +local:docker 2>/dev/null || true
        
        # Run with X11 socket mounted
        docker run -it --rm \
            -e DISPLAY=$DISPLAY \
            -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
            -v ~/.config/gcloud:/home/gclouduser/.config/gcloud:ro \
            -v $(pwd)/data:/app/data:rw \
            --network host \
            gcloud-access-tool
            
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS with XQuartz
        if ! command -v socat &> /dev/null; then
            print_warning "socat not found. Installing..."
            if command -v brew &> /dev/null; then
                brew install socat
            else
                print_error "Please install socat manually"
                exit 1
            fi
        fi
        
        # Start XQuartz if not running
        if ! pgrep -x "Xquartz" > /dev/null; then
            print_status "Starting XQuartz..."
            open -a XQuartz
            sleep 3
        fi
        
        # Allow connections from Docker
        socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$DISPLAY\" &
        SOCAT_PID=$!
        
        # Run container
        docker run -it --rm \
            -e DISPLAY=host.docker.internal:0 \
            -v ~/.config/gcloud:/home/gclouduser/.config/gcloud:ro \
            -v $(pwd)/data:/app/data:rw \
            gcloud-access-tool
            
        # Clean up socat
        kill $SOCAT_PID 2>/dev/null || true
        
    else
        print_error "Unsupported OS for GUI mode"
        exit 1
    fi
}

# Function to run headless
run_headless() {
    print_status "Running in headless mode..."
    
    # Create data directory if it doesn't exist
    mkdir -p data
    
    # Run with Xvfb for headless display
    docker run -it --rm \
        -e DISPLAY=:99 \
        -v ~/.config/gcloud:/home/gclouduser/.config/gcloud:ro \
        -v $(pwd)/data:/app/data:rw \
        -p 8080:8080 \
        gcloud-access-tool
}

# Function to run with Docker Compose
run_compose() {
    local profile=$1
    
    print_status "Running with Docker Compose (profile: $profile)..."
    
    # Create data directory if it doesn't exist
    mkdir -p data
    
    # Set environment variables
    export GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT:-}
    
    # Run with specified profile
    $DOCKER_COMPOSE --profile $profile up --build
}

# Function to stop Docker Compose
stop_compose() {
    print_status "Stopping Docker Compose services..."
    $DOCKER_COMPOSE down
    print_success "Services stopped"
}

# Function to show logs
show_logs() {
    print_status "Showing logs..."
    $DOCKER_COMPOSE logs -f
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    # Stop and remove containers
    docker stop $(docker ps -q --filter ancestor=gcloud-access-tool) 2>/dev/null || true
    docker rm $(docker ps -aq --filter ancestor=gcloud-access-tool) 2>/dev/null || true
    
    # Remove image
    docker rmi gcloud-access-tool 2>/dev/null || true
    
    # Clean up Docker Compose
    $DOCKER_COMPOSE down --rmi all --volumes --remove-orphans 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Function to show help
show_help() {
    echo "Google Cloud Access Tool - Docker Runner"
    echo "========================================"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build           Build the Docker image"
    echo "  gui             Run with GUI support (Linux/macOS)"
    echo "  headless        Run in headless mode"
    echo "  compose-gui     Run with Docker Compose (GUI profile)"
    echo "  compose-headless Run with Docker Compose (headless profile)"
    echo "  stop            Stop Docker Compose services"
    echo "  logs            Show Docker Compose logs"
    echo "  cleanup         Clean up Docker resources"
    echo "  help            Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  GOOGLE_CLOUD_PROJECT  Your Google Cloud project ID"
    echo ""
    echo "Examples:"
    echo "  $0 build                    # Build the image"
    echo "  $0 gui                      # Run with GUI"
    echo "  GOOGLE_CLOUD_PROJECT=my-project $0 gui  # Run with project set"
    echo "  $0 compose-gui              # Run with Docker Compose"
    echo ""
}

# Main script logic
main() {
    # Check Docker
    check_docker
    check_docker_compose
    
    # Parse command
    case "${1:-help}" in
        "build")
            build_image
            ;;
        "gui")
            build_image
            run_gui
            ;;
        "headless")
            build_image
            run_headless
            ;;
        "compose-gui")
            run_compose "gui"
            ;;
        "compose-headless")
            run_compose "headless"
            ;;
        "stop")
            stop_compose
            ;;
        "logs")
            show_logs
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 