#!/bin/bash

# Set the virtual environment directory
VENV_DIR=venv

# Check if Python is installed
python3 --version >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Python is not installed. Please install Python 3.10 or higher and try again."
    exit 1
fi

# Check Python version
python3 -c "import sys; assert sys.version_info >= (3, 10), 'Python 3.10 or higher is required'; print('Python version check passed.')"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Install required packages
echo "Installing required packages..."
pip install -r requirements.txt

# Run the main.py script
python main.py

# Deactivate the virtual environment
deactivate