#!/bin/bash
set -e

if [[ $# -gt 1 ]]; then
    echo "Usage: install.sh [--no-flash]" >&2
    echo "Note: --flash is deprecated and ignored (Adobe Flash is obsolete)." >&2
    exit 1
fi

if [[ $# -gt 0 ]]; then
    case "$1" in
        "--flash")
            echo "Warning: --flash is deprecated (Adobe Flash is obsolete) and will be ignored."
            flash=false
            ;;
        "--no-flash")
            flash=false
            ;;
        *)
            echo "Usage: install.sh [--no-flash]" >&2
            echo "Note: --flash is deprecated and ignored." >&2
            exit 1
            ;;
    esac
else
    # Flash is obsolete. Default to not installing it.
    flash=false
    echo "Adobe Flash is no longer supported (EOL 2020). Skipping Flash installation."
fi

# ===================================================================
# FLASH SUPPORT HAS BEEN REMOVED
# Adobe Flash reached end-of-life in December 2020. It is not supported
# by any modern browser and is not required for header bidding / Prebid.js
# research.
#
# The --flash option is kept only for backward compatibility with old
# scripts. Requesting Flash will now print a warning and be ignored.
# ===================================================================
if [ "$flash" = true ]; then
    echo ""
    echo "WARNING: Adobe Flash is obsolete and no longer supported."
    echo "The --flash option is deprecated and will be ignored."
    echo "Continuing without Flash..."
    echo ""
    flash=false
fi

# Note: We no longer do legacy system-wide apt installs of Firefox or
# old Python packages here. Those paths are broken on modern distros.
# The modern installation uses conda (environment.yaml) + scripts/install-firefox.sh.

# Legacy system Python / pip setup has been removed.
# Use the modern conda-based installation instead:
#   conda env create -f environment.yaml
#   ./scripts/install-firefox.sh
echo "Note: Legacy system Python/pip setup removed. Prefer conda + modern installer."

# Install a recent Firefox (required by the current privileged WebExtension).
# The modern installation script targets Firefox 150+ unbranded builds
# which are required for the experiment APIs and match the manifest's
# strict_min_version.
echo "Installing modern Firefox using scripts/install-firefox.sh..."
if [ -x "./scripts/install-firefox.sh" ]; then
    ./scripts/install-firefox.sh
else
    echo "ERROR: scripts/install-firefox.sh not found or not executable." >&2
    echo "The legacy Firefox 52 installation path has been removed." >&2
    exit 1
fi

# Note: geckodriver is provided by the conda environment (environment.yaml)
# or can be installed separately. The modern stack uses geckodriver >= 0.35.
