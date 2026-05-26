#!/bin/bash
set -e

# Note: This install script assumes that node and python is already setup
# and is meant for setting up local development rather than CI environments

if [[ $# -gt 0 ]]; then
    echo "Usage: install-mac.sh" >&2
    exit 1
fi

brew install leveldb

pip install -U -r requirements.txt

# Make npm packages available
brew install node || brew upgrade node

# Install modern Firefox (150+) using the dedicated cross-platform script.
# This is required for the current privileged WebExtension (manifest strict_min_version: 150.0).
echo "Installing modern Firefox using scripts/install-firefox.sh (cross-platform)..."
if [ -x "./scripts/install-firefox.sh" ]; then
    ./scripts/install-firefox.sh
else
    echo "ERROR: scripts/install-firefox.sh not found." >&2
    echo "Legacy Firefox 52 installation has been removed from this project." >&2
    exit 1
fi

# geckodriver should come from conda (environment.yaml pins a modern version).
# If not using conda, install it separately and ensure it is on PATH.

# Dependencies for OpenWPM development -- NOT needed to run the platform.
# * Required for compiling Firefox extension
npm install jpm -g

pip install -U -r requirements-dev.txt
