#! /bin/bash

set -eu

export USE_RGB_MATRIX_EMULATOR="True"
export TABLEAU_SERVER_BASE_URL="http://127.0.0.1:5005"

cd "$(dirname "${BASH_SOURCE[0]}")"
./m1.sh "$@"
