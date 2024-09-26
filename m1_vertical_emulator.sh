#! /bin/bash

set -eu

export USE_RGB_MATRIX_EMULATOR="True"
export ORIENTATION_VERTICAL="True"

cd "$(dirname "${BASH_SOURCE[0]}")"
./m1.sh "$@"
