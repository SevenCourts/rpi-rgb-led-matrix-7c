#! /bin/bash
#
# Runs the LED test on an XL1 panel (320x96, chain=5, parallel=3).
# Convenience wrapper around `m1.sh`; alternatively set PANEL_TYPE=XL1
# in the panel configuration file (PANEL_CONFIG) and run `m1.sh` directly.

set -eu

cd "$(dirname "${BASH_SOURCE[0]}")"
PANEL_TYPE=XL1 exec ./m1.sh "$@"
