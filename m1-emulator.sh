#! /bin/bash

set -eu

cd "$(dirname "${BASH_SOURCE[0]}")"

RUNTIME_DIR=.runtime
export PANEL_CONFIG=$RUNTIME_DIR/panel.config
export IMAGES_CACHE_DIR=$RUNTIME_DIR/panel.config

mkdir -p $RUNTIME_DIR
mkdir -p $IMAGES_CACHE_DIR

export USE_RGB_MATRIX_EMULATOR="True"
export TABLEAU_SERVER_BASE_URL="http://127.0.0.1:5005"
# export TABLEAU_SERVER_BASE_URL="https://dev.server.sevencourts.com"
# export TABLEAU_SERVER_BASE_URL="https://staging.server.sevencourts.com"
# export TABLEAU_SERVER_BASE_URL="https://prod.server.sevencourts.com"
export TABLEAU_DEBUG="True"



./m1.sh "$@"
