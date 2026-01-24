#!/usr/bin/env bash
#
# Arguments:
# 1. environment name or server base URL:
#   - local (default)
#   - dev
#   - staging
#   - prod
#

set -eu

proj_dir="$(realpath "$(dirname "${BASH_SOURCE[0]}")")"
readonly proj_dir

readonly param_env_or_url="${1:-}"

case "$param_env_or_url" in
local)
  base_url='http://127.0.0.1:5005'
  shift
  ;;
dev)
  base_url='https://dev.server.sevencourts.com'
  shift
  ;;
staging)
  base_url='https://staging.server.sevencourts.com'
  shift
  ;;
prod)
  base_url='https://prod.server.sevencourts.com'
  shift
  ;;
*) base_url='http://127.0.0.1:5005' ;;
esac
readonly base_url

(
  cd "$proj_dir"

  RUNTIME_DIR="$proj_dir/.runtime"
  export PANEL_STATE_FILE="$RUNTIME_DIR/last_panel_state.json"
  export IMAGES_CACHE_DIR="$RUNTIME_DIR/cache"

  mkdir -p "$RUNTIME_DIR" "$IMAGES_CACHE_DIR"

  export USE_RGB_MATRIX_EMULATOR="True"
  export TABLEAU_SERVER_BASE_URL="$base_url"
  export TABLEAU_DEBUG="True"

  ./m1.sh "$@"
)
