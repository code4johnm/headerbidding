#!/bin/bash
set -e

# Modern development dependencies for headerbidding / OpenWPM.
#
# This script assumes you have already created and activated the conda
# environment:
#   conda env create -f environment.yaml
#   conda activate openwpm
#
# It installs additional tools needed for:
# - Building the TypeScript WebExtension
# - Running tests and development workflows

echo "Installing development dependencies inside the active environment..."

# Ensure we are inside the openwpm conda environment if possible
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)" 2>/dev/null || true
    conda activate openwpm 2>/dev/null || true
fi

# Install Node.js tools via conda if available, otherwise fall back
if conda list nodejs &> /dev/null 2>&1; then
    echo "Using Node.js from conda environment."
else
    echo "Warning: Node.js not found in conda. The Extension build may fail."
fi

# Modern extension build no longer uses the deprecated 'jpm' tool.
# The build is handled by npm + webpack inside the Extension directory.
# See scripts/build-extension.sh for the current build command.

pip install -U -r requirements-dev.txt

echo "Development dependencies installed."
echo "To build the extension later, run: ./scripts/build-extension.sh (with the openwpm env active)"
