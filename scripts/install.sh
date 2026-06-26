#!/bin/bash

set -euo pipefail

source ./scripts/share.sh

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
install_root="${HOME}/.local"
bin_dir="${install_root}/bin"
data_dir="${XDG_DATA_HOME:-${HOME}/.local/share}/$NAME"

echo "Installing $NAME to ${bin_dir}/$NAME"
echo "Data files will be installed to ${data_dir}"

cd "${repo_root}"

if [[ ! -f dist/$NAME ]]; then
    ./scripts/build.sh
fi

mkdir -p "${bin_dir}" "${data_dir}"
install -m 755 dist/$NAME "${bin_dir}/$NAME"

echo "Installed $NAME to ${bin_dir}/$NAME"
if [[ ":${PATH}:" != *":${bin_dir}:"* ]]; then
    echo "Add ${bin_dir} to PATH if it is not already there."
fi
