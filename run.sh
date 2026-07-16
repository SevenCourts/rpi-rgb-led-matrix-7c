#!/bin/bash
#
# Panel-type-aware launcher for the LED test firmware. 7c.service invokes
# this single entry point; we dispatch to the matching per-panel shell
# script which sets the correct `--led-*` hardware arguments.
#
# Same convention as run.sh in the production app (master branch).
#
# PANEL_TYPE resolution order:
#   1. PANEL_TYPE env var (set by an explicit caller — useful in dev).
#   2. PANEL_TYPE in the file named by PANEL_CONFIG (set by 7c.service).
#   3. PANEL_TYPE in /etc/7c/panel.conf or /opt/7c/panel.conf.
#   4. Fallback: M1.

set -eu

cd "$(dirname "${BASH_SOURCE[0]}")"

if [ -z "${PANEL_TYPE:-}" ]; then
  for conf in "${PANEL_CONFIG:-}" /etc/7c/panel.conf /opt/7c/panel.conf; do
    if [ -n "$conf" ] && [ -f "$conf" ]; then
      # shellcheck disable=SC1091
      . "$conf"
      break
    fi
  done
fi
PANEL_TYPE="${PANEL_TYPE:-M1}"

case "$PANEL_TYPE" in
  M1)  exec ./m1.sh  "$@" ;;
  L1)  exec ./l1.sh  "$@" ;;
  XL1) exec ./xl1.sh "$@" ;;
  *)
    echo "run.sh: unknown PANEL_TYPE='$PANEL_TYPE'; falling back to M1" >&2
    exec ./m1.sh "$@"
    ;;
esac
