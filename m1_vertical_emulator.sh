#!/bin/bash
set -eu
cd $(dirname $0)
export USE_RGB_MATRIX_EMULATOR="True"
export ORIENTATION_VERTICAL="True"
python3 ./m1.py \
  --led-cols=64 \
  --led-rows=192 \
  --led-parallel=1 \
  --led-chain=1 \
  $*
