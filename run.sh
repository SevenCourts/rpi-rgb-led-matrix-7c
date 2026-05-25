#!/bin/bash
#
# Panel-type-aware launcher. The sevencourts.os supervisor (S10sevencourts)
# invokes this single entry point; we dispatch to the matching per-panel
# shell script which sets the correct `--led-*` hardware arguments.
#
# PANEL_TYPE resolution order:
#   1. PANEL_TYPE env var (set by an explicit caller — useful in dev).
#   2. PANEL_TYPE in /etc/7c/panel.conf (production source of truth).
#   3. Fallback: M1.

set -eu

cd "$(dirname "${BASH_SOURCE[0]}")"

if [ -z "${PANEL_TYPE:-}" ]; then
  for conf in /etc/7c/panel.conf /opt/7c/panel.conf; do
    if [ -f "$conf" ]; then
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
