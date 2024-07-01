#!/bin/bash
set -eu
cd $(dirname $0)
export USE_RGB_MATRIX_EMULATOR="True"
python3 entrance_demo.py \
  --led-cols=192 \
  --led-rows=192 \
  --led-parallel=1 \
  --led-chain=1 \
  $*
