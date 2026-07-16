#! /bin/bash
#
# Calls `./m1.py` with arguments selected using process' env vars and env vars
# loaded from panel configuration file.
#
# Env vars:
#
# - PANEL_CONFIG -- path to panel configuration, which is a shell env file.
#  Don't put anything here, it's for `m1.py` only and will be overriden.
# - PANEL_TYPE -- M1 (default) / L1 / XL1. Selects the LED matrix geometry.
#  May also be set in the panel configuration file (PANEL_CONFIG).
# - USE_RGB_MATRIX_EMULATOR -- when set, arguments for emulator used.

set -eu

declare panel_config
panel_config="${PANEL_CONFIG-}"
readonly panel_config

# PANEL_TYPE from the process environment (e.g. via xl1.sh) takes
# precedence over the one from the panel configuration file.
declare panel_type_env
panel_type_env="${PANEL_TYPE-}"
readonly panel_type_env

# shellcheck source=panel.conf
if [[ -n $panel_config && -f $panel_config ]]; then
  source "$panel_config"
fi

declare is_emulator
is_emulator="${USE_RGB_MATRIX_EMULATOR-}"
readonly is_emulator
if [[ -n $is_emulator ]]; then
  export USE_RGB_MATRIX_EMULATOR
fi

# Panel geometry (64x32 modules, multiplexing=1):
#   M1  - 192x64 (chain=3, parallel=2)
#   L1  - 192x96 (chain=3, parallel=3)
#   XL1 - 320x96 (chain=5, parallel=3)
declare panel_type
panel_type="${panel_type_env:-${PANEL_TYPE:-M1}}"
readonly panel_type

declare led_chain led_parallel
case $panel_type in
  XL1) led_chain=5; led_parallel=3 ;;
  L1)  led_chain=3; led_parallel=3 ;;
  M1)  led_chain=3; led_parallel=2 ;;
  *)
    echo "m1.sh: unknown PANEL_TYPE '$panel_type', expected M1 / L1 / XL1" >&2
    exit 1
    ;;
esac
readonly led_chain led_parallel

declare -a cmd_args
if [[ -z $is_emulator ]]; then
  cmd_args=(
    --led-chain="$led_chain"
    --led-cols=64
    --led-multiplexing=1
    --led-parallel="$led_parallel"
    --led-pwm-lsb-nanoseconds=50
    --led-row-addr-type=0
    --led-rows=32
    --led-slowdown-gpio=5
  )
else
  cmd_args=(
    --led-chain="$led_chain"
    --led-cols=64
    --led-parallel="$led_parallel"
    --led-rows=32
  )
fi
readonly cmd_args

cd "$(dirname "${BASH_SOURCE[0]}")"
python3 ./m1.py "${cmd_args[@]}" "$@"
