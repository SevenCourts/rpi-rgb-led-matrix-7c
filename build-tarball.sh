#!/bin/bash
#
# Build a self-contained app tarball for SevenCourts M1 scoreboard.
#
# On x86_64 hosts, uses Docker with QEMU emulation to cross-build
# the rgbmatrix native library for ARM64.
#
# Usage: ./build-tarball.sh
# Output: 7c-app-<sha>.tar.gz + 7c-app-<sha>.sha256 in current directory

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHA="$(git -C "$REPO_DIR" rev-parse --short HEAD)"
APP_DIR="7c-app-$SHA"
STAGING="/tmp/7c-tarball-staging"

echo "=== Building app tarball for $SHA ==="

rm -rf "$STAGING"
mkdir -p "$STAGING/$APP_DIR"

# --- Step 1: Build rgbmatrix + vendor Python deps (ARM64, single container) ---
echo "--- Building native libs + vendoring deps via Docker (arm64 QEMU) ---"

BUILD_OUT="/tmp/7c-build-out"
rm -rf "$BUILD_OUT"
mkdir -p "$BUILD_OUT"

docker run --rm --platform linux/arm64 \
  -v "$BUILD_OUT:/out" \
  python:3.11-slim-bullseye \
  bash -c '
    set -eux
    apt-get update && apt-get install -y git build-essential python3-dev cython3

    # Build rgbmatrix
    git clone --depth 1 --branch sevencourts/v2 \
      https://github.com/sevencourts/rpi-rgb-led-matrix.git /tmp/sdk
    cd /tmp/sdk
    make -C lib
    make -C bindings/python/rgbmatrix
    cd bindings/python
    python3 setup.py build_ext --inplace

    # Copy rgbmatrix outputs
    mkdir -p /out/rgbmatrix/lib /out/rgbmatrix/python/rgbmatrix
    cp /tmp/sdk/lib/librgbmatrix.a /out/rgbmatrix/lib/
    find /tmp/sdk/bindings/python -name "*.so" -exec cp {} /out/rgbmatrix/python/rgbmatrix/ \;
    cp /tmp/sdk/bindings/python/rgbmatrix/*.py /out/rgbmatrix/python/rgbmatrix/

    # Vendor Python deps
    pip install --target=/out/vendor orjson==3.10
  '

cp -r "$BUILD_OUT/rgbmatrix" "$STAGING/$APP_DIR/rgbmatrix"
cp -r "$BUILD_OUT/vendor" "$STAGING/$APP_DIR/vendor"

# --- Step 3: Stage app files ---
echo "--- Staging app files ---"

cd "$REPO_DIR"
cp m1.sh samplebase.py "$STAGING/$APP_DIR/"
cp -r sevencourts "$STAGING/$APP_DIR/sevencourts"
cp -r fonts "$STAGING/$APP_DIR/fonts"
cp -r images "$STAGING/$APP_DIR/images"
echo "$SHA" > "$STAGING/$APP_DIR/VERSION"

# --- Step 4: Create tarball + checksum ---
echo "--- Creating tarball ---"

cd "$STAGING"
tar czf "$REPO_DIR/7c-app-$SHA.tar.gz" "$APP_DIR"
cd "$REPO_DIR"
sha256sum "7c-app-$SHA.tar.gz" > "7c-app-$SHA.sha256"

echo ""
echo "=== Done ==="
echo "Tarball: 7c-app-$SHA.tar.gz ($(du -h "7c-app-$SHA.tar.gz" | cut -f1))"
echo "Checksum: 7c-app-$SHA.sha256"
echo ""
echo "Contents:"
tar tzf "7c-app-$SHA.tar.gz" | head -30
echo "..."

# Cleanup
rm -rf "$STAGING" "$BUILD_OUT"
