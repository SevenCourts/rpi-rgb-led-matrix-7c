#!/bin/bash

set -eu

cd $(dirname $0)

export USE_RGB_MATRIX_EMULATOR="True"
export TABLEAU_SERVER_BASE_URL="http://127.0.0.1:5000"

./m1.sh
