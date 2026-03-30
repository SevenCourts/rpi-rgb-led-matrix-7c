# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the SevenCourts M1 scoreboard firmware for Raspberry Pi-based RGB LED matrix displays (192x64 pixels). The scoreboard displays live tennis match scores, booking information, signage, and idle mode content (clocks, images, messages) by polling a backend server API.

**Key Technologies:**
- Python 3.9
- `rpi-rgb-led-matrix` C++ library with Python bindings for hardware control
- `RGBMatrixEmulator` for local development without hardware
- Raspberry Pi OS Lite 64-bit (kernel 5.15.84-v8+)
- SystemD services for production deployment

## Development Commands

### Environment Setup

Uses [Devbox](https://www.jetify.com/devbox) (Nix-based) for reproducible development:
```bash
devbox shell          # activates Python 3.9 + .venv
```

Python dependencies (no requirements.txt — install manually):
```bash
pip install Pillow requests python-dateutil orjson==3.10 RGBMatrixEmulator==0.14.1
```

### Running Locally with Emulator

```bash
./m1-emulator.sh      # starts emulator, open http://localhost:8888
```

Environment variables in `m1-emulator.sh` control behavior:
- `USE_RGB_MATRIX_EMULATOR=True` - enables emulator mode
- `TABLEAU_SERVER_BASE_URL` - backend server URL (dev/staging/prod)
- `TABLEAU_DEBUG=True` - enables DEBUG logging level (otherwise INFO)
- `PANEL_STATE_FILE` - path to persistent state JSON file
- `IMAGES_CACHE_DIR` - path for cached images

### Running on Hardware

```bash
./m1.sh               # on Raspberry Pi with connected LED matrix
```

This script passes hardware-specific LED matrix parameters (chain length, rows, cols, multiplexing, GPIO slowdown, etc.) to the Python application.

### Testing

Integration tests use [Hurl](https://hurl.dev/) (HTTP request testing), not pytest:
```bash
# Set target panel (BASE64-encoded hostname)
export HURL_7c_target_panel=<base64-hostname>
# Run all tests (Windows: run_full.cmd)
cd test/hurl && hurl --test *.hurl
```

Test files are in `test/hurl/` — they exercise scoreboard rendering modes via the backend API.

### Formatting

Black formatter is configured via VSCode (format-on-save). No CLI linting tools are configured.

### Docker

```bash
docker container run -it --rm tennismath.tableau.emulator
```
Override server with `TABLEAU_SERVER_BASE_URL` env var. CI builds via `.github/workflows/build.yml` (manual trigger, pushes to GHCR).

### Panel Deployment

Deploy firmware to a remote panel:
```bash
install/m1-deploy.sh install/m1-setup/_setup.sh <panel-ip> [branch] [daemon-url]
```

### Server Stage URLs

- DEV: `https://dev.server.sevencourts.com`
- STAGING: `https://staging.server.sevencourts.com`
- PROD: `https://prod.server.sevencourts.com` (default)

## Architecture

### Application Entry Point

- **`sevencourts/m1/main.py`** - Main application loop
  - Spawns 3 daemon threads:
    - `_poll_panel_info()` - Registers panel with server, continuously fetches panel state (1s interval)
    - `_poll_weather_info()` - Fetches weather data from OpenWeatherMap (120s interval)
    - `_refresh_time()` - Updates current time in panel timezone (1s interval)
  - Main render loop checks for state changes, redraws canvas when state updates
  - Uses `panel_info_lock` and `weather_info_lock` for thread-safe state access

### Core Modules

- **`sevencourts/m1/model.py`** - Data model
  - `PanelState` dataclass holds global state (panel_info, weather_info, panel_id, time, server error status)
  - Persists state to JSON file (`/opt/7c/last_panel_state.json` in production)

- **`sevencourts/m1/view.py`** - Top-level view dispatcher
  - Routes to appropriate view based on panel_info content:
    - Scoreboard mode (`team1` in info) → `view_scoreboard.py`
    - Booking mode (`booking` in info) → `booking/ebusy/view.py`
    - Signage mode (`signage-info` in info) → `view_signage.py`
    - Idle mode (`idle-info` in info) → `view_clock.py` / `view_image.py` / `view_message.py`
    - Standby mode (`standby` flag) → standby indicator
  - Draws status indicator dots (blue=error, green=init, dark green=standby)

- **`sevencourts/gateway.py`** - Backend API client
  - `register_panel()` - POST /panels/ with hostname, IP, firmware version
  - `fetch_panel_info(panel_id)` - GET /panels/{id}/match with telemetry headers (uptime, CPU temp, time)
  - Returns match data (status 200) or idle-info (status 205)
  - Base URL: `TABLEAU_SERVER_BASE_URL` env var (defaults to prod.tableau.tennismath.com)

- **`sevencourts/rgbmatrix.py`** - Graphics abstraction layer
  - Conditional imports: uses `RGBMatrixEmulator` if `USE_RGB_MATRIX_EMULATOR` env var set, otherwise `rgbmatrix` hardware library
  - Defines color constants (COLOR_7C_BLUE, COLOR_7C_GOLD, etc.)
  - Loads BDF fonts (SDK fonts, Spleen fonts, 7-segment fonts)
  - Provides drawing utilities (text, rectangles, matrices, images)

- **`sevencourts/network.py`** - Network utilities
  - `hostname()` - returns system hostname
  - `ip_address()` - gets external IP by connecting to 8.8.8.8
  - Network connectivity checks
  - Default socket timeout: 30 seconds

- **`sevencourts/images.py`** - Image loading and caching
  - Downloads images from backend server paths
  - Caches images locally with ETag-based validation
  - PIL/Pillow for image processing

### View Modules

View modules live in `sevencourts/m1/` and follow the naming convention `view_*.py`. The top-level dispatcher (`view.py`) routes to the appropriate view based on `panel_info` content. Key views: `view_scoreboard.py` (tennis scores), `view_clock.py`, `view_image.py`, `view_message.py`, `view_signage.py`, and `booking/ebusy/` (court bookings).

## Important Patterns

### State Management
All panel state flows through the `PanelState` dataclass. The render loop uses deep copy comparison to detect changes and only redraws when state differs. This minimizes unnecessary rendering.

### Error Handling
The main render loop has a top-level exception handler that catches drawing errors and displays them on screen using `draw_error()`. This prevents the panel from going blank on errors.

### Threading
All background polling threads are daemon threads so they don't block Ctrl+C shutdown. Thread-safe access to shared state uses locks (`panel_info_lock`, `weather_info_lock`).

### Server Communication
The panel registers on startup and continuously polls for updates. If registration fails, it retries indefinitely. Communication errors set `server_communication_error` flag which displays a blue status indicator.

### Environment-Based Configuration
The codebase uses environment variables for all configuration (server URLs, debug mode, file paths). This allows the same code to run in emulator, on hardware, or in Docker without changes.

## Production Deployment

### Current: sevencourts.os (Buildroot image)

New panels run [sevencourts.os](https://github.com/SevenCourts/sevencourts.os) — a custom Buildroot Linux image with BusyBox init. The app is deployed as a self-contained tarball to `/opt/7c/current/` via the `7c-updater.sh` mechanism. This repo's CI builds the tarball; the OS repo bakes it into the image.

**Service definitions live in sevencourts.os**, not here:
- `S10sevencourts` — app service (runs `m1.sh` from `/opt/7c/current/`)
- `S05hostname` — hostname from Pi serial number
- `S98daemon` — sevencourts-daemon (WiFi/BLE provisioning)

### Legacy: SystemD (Raspberry Pi OS)

A handful of older panels still run stock Raspberry Pi OS with SystemD services. The legacy provisioning scripts and service files are in `install/m1-setup/` (see `install/m1-setup/DEPRECATED.md`).

### Related Repositories

- **[sevencourts.os](https://github.com/SevenCourts/sevencourts.os)** — OS image (Buildroot config, rootfs overlay, init scripts, updater). Consumes the app tarball produced by this repo's CI.
- **[sevencourts.daemon](https://github.com/SevenCourts/sevencourts.daemon)** — WiFi/BLE controller daemon (Rust). IPC format docs: `/docs/ipc/` in that repo.
- **[sevencourts.ops](https://github.com/SevenCourts/sevencourts.ops)** — Panel manufacturing, registration, deployment, and field operations tooling.
- **Interface contract**: The tarball format is specified in `sevencourts.os/spec/app-tarball-spec.md`.

### Remote Access
Panels connect to `vpn.sevencourts.com` via OpenVPN for remote SSH access and firmware updates.

## File Paths on Device

- App root: `/opt/7c/current/` (symlink to active release)
- Panel state: `/opt/7c/last_panel_state.json`
- Config: `/opt/7c/panel.conf`
- Controller daemon config: `/etc/7c_m1_assoc.json`

## Logging

Log level is controlled by `TABLEAU_DEBUG` environment variable:
- Set to any value → DEBUG level
- Unset → INFO level

View logs (sevencourts.os):
```bash
cat /var/log/sevencourts.log
```