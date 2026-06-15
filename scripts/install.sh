#!/bin/bash

# macos or linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing on macOS..."
    # Install dependencies for macOS
    brew install python3
    brew install pyinstaller
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Installing on Linux..."
    # Install dependencies for Linux, get distribution info
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID

        if [[ "$DISTRO" == "ubuntu" ]]; then
            sudo apt update
            sudo apt install -y python3 python3-pip
            pip3 install pyinstaller
        elif [[ "$DISTRO" == "fedora" ]]; then
            sudo dnf install -y python3 python3-pip
            pip3 install pyinstaller
        else
            echo "Unsupported Linux distribution: $DISTRO"
            exit 1
        fi
    else
        echo "Cannot determine Linux distribution."
        exit 1
    fi
else
    echo "Unsupported OS: $OSTYPE"
    exit 1
fi

# build
./scripts/build.sh

# install
echo "Installing..."
sudo cp dist/fast_ssh /usr/local/bin/fast_ssh
echo "Installed to $(which fast_ssh)"
