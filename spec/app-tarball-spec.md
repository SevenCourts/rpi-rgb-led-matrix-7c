# App Tarball Specification

Status: active
Date: 2026-03-29

## Overview

The SevenCourts OS (`sevencourts.os`) expects the scoreboard app deployed as a
self-contained tarball to `/opt/7c/current/`. The init script `S99sevencourts`
runs `/opt/7c/current/m1.sh` with auto-restart on failure.

## Tarball Contents

Build a single `7c-app-<version>.tar.gz` that, when extracted and symlinked
as `/opt/7c/current`, is immediately runnable:

```
7c-app-<sha>/
├── m1.sh                          # Launch script
├── samplebase.py                  # RGB matrix base class
├── sevencourts/                   # Python package (m1, views, gateway, etc.)
├── sevencourts-daemon             # BLE/WiFi controller binary (aarch64)
├── commit-id                      # Full git commit hash
├── commit-date                    # Commit date (YYYY-MM-DD)
├── fonts/                         # All BDF fonts
├── images/                        # flags, logos, weather, clipart
├── rgbmatrix/
│   ├── lib/librgbmatrix.so*       # Compiled native library (aarch64)
│   └── python/rgbmatrix/          # Python bindings (*.so + *.py)
├── vendor/                        # Vendored Python deps not in OS (e.g., orjson)
└── VERSION                        # Git short SHA (sentinel file for updater)
```

## Target OS Details

| Property | Value |
|----------|-------|
| OS | Buildroot Linux (BusyBox init, NOT systemd) |
| Architecture | aarch64 (Raspberry Pi 4) |
| Python | 3.14 |
| Init system | BusyBox init.d scripts (no `systemctl`) |
| App service | `/etc/init.d/S99sevencourts` runs `m1.sh` |
| App location | `/opt/7c/current` → symlink to `/opt/7c/releases/<version>/` |
| Config | `PANEL_CONFIG=/opt/7c/panel.conf` (set by init system) |

### Python packages already in the OS image (do NOT vendor):

- `pillow` (PIL)
- `requests`
- `dateutil`
- `smbus`

### Python packages NOT in the OS image (MUST vendor):

- `orjson`
- Any other deps not listed above

## m1.sh Adjustments

The current `m1.sh` sets PYTHONPATH to `/opt/7c/rgbmatrix/python`. Update to
use a path relative to the tarball root:

```bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$SCRIPT_DIR/rgbmatrix/python${PYTHONPATH:+:$PYTHONPATH}"
```

Also add vendor dir to PYTHONPATH if it exists:

```bash
if [ -d "$SCRIPT_DIR/vendor" ]; then
  export PYTHONPATH="$SCRIPT_DIR/vendor:$PYTHONPATH"
fi
```

## Build Process (CI)

On push to release branch or manual trigger:

1. Build `rgbmatrix` native lib for aarch64 (use `docker buildx` with arm64
   emulation or a self-hosted arm64 runner). Must link against Python 3.14.
2. Collect all app files into a staging directory
3. Vendor Python deps not in OS: `pip install orjson --target=vendor/`
   (must target aarch64)
4. Write `VERSION` file: `git rev-parse --short HEAD > VERSION`
5. Create tarball: `tar czf 7c-app-<sha>.tar.gz -C staging .`
6. Create checksum: `sha256sum 7c-app-<sha>.tar.gz > <sha>.sha256`
7. Upload as GitHub Release asset or workflow artifact

## Deploy Flow

On the OS side, the updater (`7c-updater.sh`) handles:

1. Download tarball + checksum from update server
2. Verify SHA-256
3. Extract to `/opt/7c/.staging/<version>/` (temp)
4. Atomic move to `/opt/7c/releases/<version>/`
5. Swap symlink: `/opt/7c/current` → `/opt/7c/releases/<version>/`
6. Restart service: `/etc/init.d/S99sevencourts restart`
7. Health check after 30s — auto-rollback on failure
8. Prune old releases (keep last 3)

## Manual Test Deploy

```bash
# From the sevencourts.os project:
scripts/deploy-app.sh <device-ip> 7c-app-<sha>.tar.gz
```

## Checksum Format

The `.sha256` file must be compatible with `sha256sum -c`:

```
<hex-hash>  7c-app-<sha>.tar.gz
```
