#!/bin/bash
set -eu
cd $(dirname $0)
python3 entrance_demo.py \
  --led-cols=64 \
  --led-rows=32 \
  --led-slowdown-gpio=5 \
  --led-multiplexing=1 \
  --led-row-addr-type=0 \
  --led-parallel=2 \
  --led-chain=3 \
  --led-pixel-mapper="Rotate:270" \
  $*
