#!/bin/bash

source ./scripts/share.sh

rm -f "${HOME}/.local/bin/$NAME"
echo "Uninstalled $NAME from ${HOME}/.local/bin/$NAME"