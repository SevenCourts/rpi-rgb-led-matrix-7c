# Demos for comparing C++ and Python implementations of "same" program

## Sample image

1. SSH to panel.
1. `curl 'https://filesamples.com/samples/image/ppm/sample_640%C3%97426.ppm' -o ~/sample.ppm`.

## C++

```sh
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix/examples-api-use
sudo apt-get update
sudo apt-get install libgraphicsmagick++-dev libwebp-dev -y
make image-example

sudo ./image-example --led-cols=64 --led-rows=32 --led-pwm-lsb-nanoseconds=50 --led-slowdown-gpio=5 --led-multiplexing=1 --led-row-addr-type=0 --led-parallel=2 --led-chain=3 ~/sample.ppm
# If after start the screen is black, then kill program and restart it.
```

## Python

```sh
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix/bindings/python/samples
vim image-viewer.py # replace content of file with content of `./image-viewer-demo.py`
chmod +x image-viewer.py

sudo ./image-viewer.py ~/sample.ppm
# If after start the screen is black or image rendered slowly by pixels up-down left-right, then kill program and restart it.
```
