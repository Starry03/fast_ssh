#!/bin/bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
install_root="${HOME}/.local"
bin_dir="${install_root}/bin"
data_dir="${XDG_DATA_HOME:-${HOME}/.local/share}/fast_ssh"

echo "Installing fast_ssh to ${bin_dir}/fast_ssh"
echo "Data files will be installed to ${data_dir}"

cd "${repo_root}"

if [[ ! -f dist/fast_ssh ]]; then
    ./scripts/build.sh
fi

mkdir -p "${bin_dir}" "${data_dir}"
install -m 755 dist/fast_ssh "${bin_dir}/fast_ssh"

echo "Installed fast_ssh to ${bin_dir}/fast_ssh"
if [[ ":${PATH}:" != *":${bin_dir}:"* ]]; then
    echo "Add ${bin_dir} to PATH if it is not already there."
fi
