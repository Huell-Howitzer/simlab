#!/bin/bash

PYTHON=$(which python3)
PYTHON_DIR=$(dirname "$PYTHON")

echo "Using Python at: $PYTHON"

# Check if Python is in /opt
if [[ "$PYTHON" == /opt/* ]]; then
    echo "Python is installed in /opt. Checking write permissions..."
    
    # Try writing a file to site-packages
    SITE_PACKAGES=$($PYTHON -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")

    if [ ! -w "$SITE_PACKAGES" ]; then
        echo "No write permissions to $SITE_PACKAGES."
        echo "Cannot install packages without elevated privileges."
        exit 1
    else
        echo "Write permissions OK."
    fi
fi

# Check if 'rich' is already available
$PYTHON -c "import rich" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "'rich' already installed."
    $PYTHON your_script.py
    exit 0
fi

echo "'rich' not found. Preparing to install..."

# Try conda if available and registry is reachable
if command -v conda &>/dev/null; then
    echo "Conda found. Checking registry..."
    if curl -s --head https://repo.anaconda.com/pkgs/main/ | grep "200 OK" > /dev/null; then
        echo "Conda registry is reachable. Installing with conda..."
        conda install -y rich && echo "Installed with conda."
    else
        echo "Conda registry unreachable. Skipping conda."
    fi
fi

# Check if PyPI is reachable (or GitLab mirror if you use one)
if ! curl -s --head https://pypi.org/simple/rich/ | grep "200 OK" > /dev/null; then
    echo "PyPI unreachable. Cannot proceed with pip install."
    exit 1
fi

# Check if rich is now available
$PYTHON -c "import rich" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Trying pip..."
    $PYTHON -m pip install rich || {
        echo "Failed to install 'rich'. Please install it manually."
        exit 1
    }
fi

# Finally run your script
$PYTHON your_script.py