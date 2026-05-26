#!/bin/bash
set -e

# Modern macOS development setup for headerbidding / OpenWPM.
#
# Recommended flow:
#   conda env create -f environment.yaml
#   conda activate openwpm
#   ./install-mac-dev.sh

if [[ $# -gt 0 ]]; then
    echo "Usage: ./install-mac-dev.sh" >&2
    exit 1
fi

echo "Setting up macOS development dependencies..."

# Install modern Firefox (150+) if not already present
if [ -x "./scripts/install-firefox.sh" ]; then
    ./scripts/install-firefox.sh
else
    echo "ERROR: scripts/install-firefox.sh not found." >&2
    exit 1
fi

# geckodriver is expected to come from the conda environment.yaml

# Development-only tools (not required to run crawls)
brew install leveldb || true

# The modern extension no longer uses the deprecated 'jpm' tool.
# Building is done via npm/webpack. See scripts/build-extension.sh.

pip install -U -r requirements-dev.txt

echo "macOS development setup complete."
echo "Activate the environment with: conda activate openwpm"
echo "Build the extension with: ./scripts/build-extension.sh"
