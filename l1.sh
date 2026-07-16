#! /bin/bash
#
# Starts the LED test on an L1 panel (192x96, chain=3, parallel=3).
# Invoked by run.sh, which resolves PANEL_TYPE; can also be run directly.
#
# Env vars:
#
# - USE_RGB_MATRIX_EMULATOR -- when set, arguments for emulator used.

set -eu

declare is_emulator
is_emulator="${USE_RGB_MATRIX_EMULATOR-}"
readonly is_emulator
if [[ -n $is_emulator ]]; then
  export USE_RGB_MATRIX_EMULATOR
fi

declare -a cmd_args
if [[ -z $is_emulator ]]; then
  cmd_args=(
    --led-chain=3
    --led-cols=64
    --led-multiplexing=1
    --led-parallel=3
    --led-pwm-lsb-nanoseconds=50
    --led-row-addr-type=0
    --led-rows=32
    --led-slowdown-gpio=5
  )
else
  cmd_args=(
    --led-chain=3
    --led-cols=64
    --led-parallel=3
    --led-rows=32
  )
fi
readonly cmd_args

cd "$(dirname "${BASH_SOURCE[0]}")"
exec python3 ./led-test.py "${cmd_args[@]}" "$@"
