#! /bin/bash

set -eu

export ORIENTATION_VERTICAL="True"

cd "$(dirname "${BASH_SOURCE[0]}")"
./m1.sh "$@"
