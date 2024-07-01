#!/bin/bash
set -eu
cd $(dirname $0)
python3 ./p10.py \
  --led-cols=32 \
  --led-rows=16 \
  --led-slowdown-gpio=2 \
  --led-multiplexing=3 \
  --led-row-addr-type=2 \
  $*
