#!/bin/bash

# Development script with Python 3.11 enforcement

# Check Python version
if ! command -v python3.11 &> /dev/null
then
    echo "ERROR: Python 3.11 is not installed or not found in PATH"
    echo "Please install Python 3.11 to run this application"
    echo "Visit https://www.python.org/downloads/ for installation instructions"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment with Python 3.11..."
    python3.11 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment with Python 3.11"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate

# Verify Python version in venv
PYTHON_VERSION=$(python --version 2>&1)
if [[ $PYTHON_VERSION != *"Python 3.11"* ]]; then
    echo "ERROR: Virtual environment is not using Python 3.11"
    echo "Current version: $PYTHON_VERSION"
    echo "Deactivating and exiting..."
    deactivate
    exit 1
fi

# Install/update dependencies
echo "Installing dependencies with Python 3.11..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    deactivate
    exit 1
fi

# Run the application with auto-reload for development
echo "Starting the application with auto-reload for development..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
