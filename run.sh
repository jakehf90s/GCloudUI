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
