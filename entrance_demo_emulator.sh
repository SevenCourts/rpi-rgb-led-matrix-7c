#!/bin/bash

set -eu

cd $(dirname $0)

export USE_RGB_MATRIX_EMULATOR="True"

./entrance_demo.sh "$@"
