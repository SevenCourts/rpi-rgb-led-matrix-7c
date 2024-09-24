#! /bin/bash

set -eu

declare panel_config
panel_config="${PANEL_CONFIG-}"
readonly panel_config

# shellcheck source=panel.conf
if [[ -n $panel_config && -f $panel_config ]]; then
  source "$panel_config"
fi

declare is_emulator
is_emulator="${USE_RGB_MATRIX_EMULATOR-}"
readonly is_emulator

declare is_vertical
is_vertical="${ORIENTATION_VERTICAL-}"
readonly is_vertical

declare -a cmd_args
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
if [[ -n $is_vertical ]]; then
  if [[ -z $is_emulator ]]; then
    cmd_args=(
      --led-chain=3
      --led-cols=64
      --led-multiplexing=1
      --led-parallel=2
      --led-pixel-mapper=Rotate:270
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
      --led-rows=192
    )
  fi
fi
readonly cmd_args

cd "$(dirname "${BASH_SOURCE[0]}")"
python3 ./m1.py "${cmd_args[@]}" "$@"
