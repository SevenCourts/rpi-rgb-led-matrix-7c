#! /bin/bash
#
# Calls `./m1.py` with arguments selected using process' env vars and env vars
# loaded from panel configuration file.
#
# Env vars:
#
#  Don't put anything here, it's for `m1.py` only and will be overriden.
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
    --led-parallel=2
    --led-pwm-lsb-nanoseconds=50
    --led-row-addr-type=0
    --led-rows=32
    --led-slowdown-gpio=5
  )
else
  cmd_args=(
    --led-chain=1
    --led-cols=64
    --led-parallel=1
    --led-rows=32
    --led-chain=3
    --led-parallel=2
  )
fi
readonly cmd_args

cd "$(dirname "${BASH_SOURCE[0]}")"
python3 -m sevencourts.m1.main "${cmd_args[@]}" "$@"
