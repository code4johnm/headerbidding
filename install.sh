#!/bin/bash
set -e

if [[ $# -gt 1 ]]; then
    echo "Usage: install.sh [--flash | --no-flash]" >&2
    exit 1
fi

if [[ $# -gt 0 ]]; then
    case "$1" in
        "--flash")
            flash=true
            ;;
        "--no-flash")
            flash=false
            ;;
        *)
            echo "Usage: install.sh [--flash | --no-flash]" >&2
            exit 1
            ;;
    esac
else
    echo "Would you like to install Adobe Flash Player? (Only required for crawls with Flash) [y,N]"
    read -s -n 1 response
    if [[ $response = "" ]] || [ $response == 'n' ] || [ $response == 'N' ]; then
        flash=false
        echo Not installing Adobe Flash Plugin
    elif [ $response == 'y' ] || [ $response == 'Y' ]; then
        flash=true
        echo Installing Adobe Flash Plugin
    else
        echo Unrecognized response, exiting
        exit 1
    fi
fi

if [ "$flash" = true ]; then
    sudo sh -c 'echo "deb http://archive.canonical.com/ubuntu/ trusty partner" >> /etc/apt/sources.list.d/canonical_partner.list'
fi
sudo apt-get update

sudo apt-get install -y firefox htop git python-dev libxml2-dev libxslt-dev libffi-dev libssl-dev build-essential xvfb libboost-python-dev libleveldb-dev libjpeg-dev curl wget

# For some versions of ubuntu, the package libleveldb1v5 isn't available. Use libleveldb1 instead.
sudo apt-get install -y libleveldb1v5 || sudo apt-get install -y libleveldb1

if [ "$flash" = true ]; then
    sudo apt-get install -y adobe-flashplugin
fi

# Check if we're running on continuous integration
# Python requirements are already installed by .travis.yml on Travis
if [ "$TRAVIS" != "true" ]; then
  wget https://bootstrap.pypa.io/get-pip.py
  python get-pip.py --user
  rm get-pip.py
	pip install --user --upgrade -r requirements.txt
fi

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
