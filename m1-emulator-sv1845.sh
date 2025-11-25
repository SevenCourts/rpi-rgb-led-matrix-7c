#! /bin/bash

mkdir .runtime

set -eu

cd "$(dirname "${BASH_SOURCE[0]}")"

export PANEL_CONFIG=.runtime/panel.config

export USE_RGB_MATRIX_EMULATOR="True"
# export TABLEAU_SERVER_BASE_URL="http://127.0.0.1:5005"
export TABLEAU_SERVER_BASE_URL="https://dev.server.sevencourts.com"
# export TABLEAU_SERVER_BASE_URL="https://staging.server.sevencourts.com"
# export TABLEAU_SERVER_BASE_URL="https://prod.server.sevencourts.com"
export TABLEAU_DEBUG="True"
export TABLEAU_PANEL_CODE="ffb1e14b"

./m1.sh "$@"
