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

### Running Locally with Emulator

Start the emulator (default connects to local server at port 5005):
```bash
./m1-emulator.sh
```

Open browser to `http://localhost:8888` to view the display.

Environment variables in `m1-emulator.sh` control behavior:
- `USE_RGB_MATRIX_EMULATOR=True` - enables emulator mode
- `TABLEAU_SERVER_BASE_URL` - backend server URL (dev/staging/prod)
- `TABLEAU_DEBUG=True` - enables DEBUG logging level (otherwise INFO)
- `PANEL_STATE_FILE` - path to persistent state JSON file
- `IMAGES_CACHE_DIR` - path for cached images

### Running on Hardware

On Raspberry Pi with connected LED matrix:
```bash
./m1.sh
```

This script passes hardware-specific LED matrix parameters (chain length, rows, cols, multiplexing, GPIO slowdown, etc.) to the Python application.

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

- **`sevencourts/m1/view_scoreboard.py`** - Tennis match scoreboard rendering
  - Draws team names (uppercase, various font sizes based on length)
  - Draws set scores (3 sets displayed, handles tiebreaks with superscript)
  - Draws game scores (15/30/40/A format)
  - Service indicator (yellow dot)
  - Winner display with "MATCH" text

- **`sevencourts/m1/view_signage.py`** - Signage mode for promotional content

- **`sevencourts/m1/view_clock.py`** - Clock display (HH:MM format)
  - Multiple font sizes for different layouts

- **`sevencourts/m1/view_image.py`** - Idle mode image display
  - Preset images or uploaded custom images

- **`sevencourts/m1/view_message.py`** - Text message display

- **`sevencourts/m1/booking/ebusy/`** - eBusy booking system integration
  - `view_single.py` - Single court booking view
  - `view_multiple.py` - Multiple court booking view

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

### SystemD Services

**7c.service** - Main scoreboard application
- WorkingDirectory: `/opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c`
- Runs `m1.sh` with hardware parameters
- Restarts automatically on failure (RestartSec=5)
- Depends on `7c-hostname.service`

**7c-controller.service** - WiFi/Bluetooth controller
- Rust binary at `/opt/7c/7c_m1_controller`
- Manages WiFi configuration via SevenCourts Admin mobile app
- Reads config from `/etc/7c_m1_assoc.json`

**7c-hostname.service** - Sets hostname from hardware serial number
- Runs `/opt/7c/7c-set-hostname.sh` on boot
- Hostname is last 8 bytes of `/sys/firmware/devicetree/base/serial-number`

### Remote Access
Panels connect to `vpn.sevencourts.com` via OpenVPN for remote SSH access and firmware updates.

### Switching Server Stage
Edit systemd service environment:
```bash
EDITOR=vim systemctl edit 7c
```
Set `TABLEAU_SERVER_BASE_URL` environment variable to dev/staging/prod URL.

## File Paths in Production

- Panel state: `/opt/7c/last_panel_state.json`
- Config: `/opt/7c/panel.conf`
- Firmware: `/opt/7c/rpi-rgb-led-matrix/bindings/python/rpi-rgb-led-matrix-7c/`
- Controller config: `/etc/7c_m1_assoc.json`
- SystemD services: `/etc/systemd/system/7c*.service`

## Logging

Log level is controlled by `TABLEAU_DEBUG` environment variable:
- Set to any value → DEBUG level
- Unset → INFO level

View logs:
```bash
journalctl -u 7c -f
journalctl -u 7c-controller -f
```