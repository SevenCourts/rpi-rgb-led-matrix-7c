#!/bin/bash
set -eu
cd $(dirname $0)
export ORIENTATION_VERTICAL="True"
python3 ./m1.py \
  --led-cols=64 \
  --led-rows=32 \
  --led-parallel=2 \
  --led-chain=3 \
  --led-pixel-mapper="Rotate:270" \
  --led-pwm-lsb-nanoseconds=50 \
  --led-slowdown-gpio=5 \
  --led-multiplexing=1 \
  --led-row-addr-type=0 \
  $*
